import hashlib
import json
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from datetime import datetime
import difflib

from ..domain.models import (
    Commit, Blob, Tree, Diff, FileChange, ChangeType, 
    MergeResult, Conflict
)
from ..domain.services import (
    HashService, CommitService, BranchService, 
    MergeService, RevertService, DiffService
)
from .repositories import FileObjectRepository

class SHA1HashService(HashService):
    """Реализация сервиса хеширования с SHA1"""
    
    def compute_hash(self, data: str) -> str:
        return hashlib.sha1(data.encode()).hexdigest()

class SimpleCommitService(CommitService):
    """Простая реализация сервиса коммитов"""
    
    def __init__(self, object_repo: FileObjectRepository):
        self.object_repo = object_repo
    
    def create_commit(self, tree_hash: str, message: str, 
                     parent_hashes: List[str], author: str) -> str:
        commit = Commit(
            hash="",  # Будет вычислен при сохранении
            tree_hash=tree_hash,
            parent_hashes=parent_hashes,
            message=message,
            author=author,
            timestamp=datetime.now(),
            committer=author
        )
        return self.object_repo.save_commit(commit)

class AdvancedBranchService(BranchService):
    """Продвинутая реализация сервиса веток"""
    
    def __init__(self, object_repo: FileObjectRepository, reference_repo):
        self.object_repo = object_repo
        self.reference_repo = reference_repo
    
    def create_branch(self, branch_name: str, from_commit: str) -> str:
        if not self.object_repo.exists(from_commit):
            raise ValueError(f"Commit {from_commit} does not exist")
        self.reference_repo.create_branch(branch_name, from_commit)
        return branch_name
    
    def delete_branch(self, branch_name: str):
        current_branch = self.reference_repo.get_current_branch()
        if current_branch == branch_name:
            raise ValueError("Cannot delete current branch")
        branch_path = self.reference_repo.refs_path / "heads" / branch_name
        if branch_path.exists():
            branch_path.unlink()
    
    def get_branch_history(self, branch_name: str) -> List[Commit]:
        commit_hash = self.reference_repo.get_branch_commit(branch_name)
        history = []
        while commit_hash:
            commit = self.object_repo.get_commit(commit_hash)
            if not commit:
                break
            history.append(commit)
            commit_hash = commit.parent_hashes[0] if commit.parent_hashes else None
        return history

class ThreeWayMergeService(MergeService):
    """Реализация трехстороннего слияния"""
    
    def __init__(self, object_repo: FileObjectRepository, diff_service: DiffService):
        self.object_repo = object_repo
        self.diff_service = diff_service
    
    def find_common_ancestor(self, commit1_hash: str, commit2_hash: str) -> Optional[str]:
        """Найти общего предка используя BFS"""
        visited = set()
        
        def get_parents(commit_hash):
            commit = self.object_repo.get_commit(commit_hash)
            return commit.parent_hashes if commit else []
        
        # BFS от первого коммита
        queue = [commit1_hash]
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            queue.extend(get_parents(current))
        
        # BFS от второго коммита до нахождения пересечения
        queue = [commit2_hash]
        visited2 = set()
        while queue:
            current = queue.pop(0)
            if current in visited:
                return current
            if current in visited2:
                continue
            visited2.add(current)
            queue.extend(get_parents(current))
        
        return None
    
    def three_way_merge(self, base_tree: Tree, ours_tree: Tree, theirs_tree: Tree) -> MergeResult:
        """Выполнить трехстороннее слияние"""
        our_diff = self.diff_service.compute_tree_diff(base_tree, ours_tree)
        their_diff = self.diff_service.compute_tree_diff(base_tree, theirs_tree)
        
        conflicts = self.detect_conflicts(our_diff, their_diff)
        
        if conflicts:
            return MergeResult(success=False, conflicts=[c.file_path for c in conflicts])
        
        # Применяем оба набора изменений к базе
        merged_entries = dict(base_tree.entries)
        
        # Наши изменения
        for change in our_diff.changes:
            if change.change_type in [ChangeType.ADDED, ChangeType.MODIFIED]:
                merged_entries[change.path] = change.new_hash
            elif change.change_type == ChangeType.DELETED:
                merged_entries.pop(change.path, None)
        
        # Их изменения
        for change in their_diff.changes:
            if change.change_type in [ChangeType.ADDED, ChangeType.MODIFIED]:
                merged_entries[change.path] = change.new_hash
            elif change.change_type == ChangeType.DELETED:
                merged_entries.pop(change.path, None)
        
        merged_tree_hash = self.object_repo.save_tree(merged_entries)
        return MergeResult(success=True, conflicts=[], merged_tree_hash=merged_tree_hash)
    
    def detect_conflicts(self, our_diff: Diff, their_diff: Diff) -> List[Conflict]:
        """Обнаружить конфликты слияния"""
        conflicts = []
        
        our_changes = {change.path: change for change in our_diff.changes}
        their_changes = {change.path: change for change in their_diff.changes}
        
        all_files = set(our_changes.keys()) | set(their_changes.keys())
        
        for file_path in all_files:
            our_change = our_changes.get(file_path)
            their_change = their_changes.get(file_path)
            
            if our_change and their_change:
                # Обе ветки изменили файл - проверяем конфликт
                if our_change.new_hash != their_change.new_hash:
                    our_content = self.object_repo.get_blob(our_change.new_hash).content
                    their_content = self.object_repo.get_blob(their_change.new_hash).content
                    base_content = self.object_repo.get_blob(our_change.old_hash).content if our_change.old_hash else ""
                    
                    conflicts.append(Conflict(
                        file_path=file_path,
                        our_content=our_content,
                        their_content=their_content,
                        base_content=base_content
                    ))
        
        return conflicts
    
    def is_fast_forward(self, from_commit_hash: str, to_commit_hash: str) -> bool:
        """Проверить возможность fast-forward слияния"""
        current = from_commit_hash
        while current:
            if current == to_commit_hash:
                return True
            commit = self.object_repo.get_commit(current)
            if not commit or not commit.parent_hashes:
                break
            current = commit.parent_hashes[0]
        return False

class GitStyleRevertService(RevertService):
    """Реализация отката в стиле Git"""
    
    def __init__(self, object_repo: FileObjectRepository, diff_service: DiffService):
        self.object_repo = object_repo
        self.diff_service = diff_service
    
    def compute_revert_patch(self, commit_to_revert: Commit, parent_commit: Commit) -> Diff:
        """Вычислить инвертированный патч для отката"""
        if not parent_commit:
            raise ValueError("Cannot revert initial commit")
        
        commit_tree = self.object_repo.get_tree(commit_to_revert.tree_hash)
        parent_tree = self.object_repo.get_tree(parent_commit.tree_hash)
        
        # Получаем изменения в коммите
        changes = self.diff_service.compute_tree_diff(parent_tree, commit_tree)
        
        # Инвертируем изменения
        inverted_changes = []
        for change in changes.changes:
            if change.change_type == ChangeType.ADDED:
                inverted_changes.append(FileChange(
                    path=change.path,
                    change_type=ChangeType.DELETED,
                    old_hash=change.new_hash
                ))
            elif change.change_type == ChangeType.DELETED:
                inverted_changes.append(FileChange(
                    path=change.path,
                    change_type=ChangeType.ADDED,
                    new_hash=change.old_hash
                ))
            elif change.change_type == ChangeType.MODIFIED:
                inverted_changes.append(FileChange(
                    path=change.path,
                    change_type=ChangeType.MODIFIED,
                    old_hash=change.new_hash,
                    new_hash=change.old_hash
                ))
        
        return Diff(changes=inverted_changes, conflicts=[])
    
    def apply_revert(self, current_tree: Tree, revert_patch: Diff) -> Tree:
        """Применить патч отката"""
        new_entries = dict(current_tree.entries)
        
        for change in revert_patch.changes:
            if change.change_type == ChangeType.ADDED:
                new_entries[change.path] = change.new_hash
            elif change.change_type == ChangeType.DELETED:
                new_entries.pop(change.path, None)
            elif change.change_type == ChangeType.MODIFIED:
                new_entries[change.path] = change.new_hash
        
        new_tree_hash = self.object_repo.save_tree(new_entries)
        return self.object_repo.get_tree(new_tree_hash)

class UnifiedDiffService(DiffService):
    """Реализация сервиса diff с unified diff форматом"""
    
    def __init__(self, object_repo: FileObjectRepository):
        self.object_repo = object_repo
    
    def compute_file_diff(self, old_content: str, new_content: str) -> List[str]:
        """Сгенерировать unified diff для файла"""
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            old_lines, new_lines,
            fromfile='a/file', tofile='b/file',
            lineterm=''
        )
        return list(diff)
    
    def compute_tree_diff(self, old_tree: Tree, new_tree: Tree) -> Diff:
        """Вычислить различия между деревьями"""
        changes = []
        
        all_files = set(old_tree.entries.keys()) | set(new_tree.entries.keys())
        
        for file_path in all_files:
            old_hash = old_tree.entries.get(file_path)
            new_hash = new_tree.entries.get(file_path)
            
            if old_hash and not new_hash:
                # Файл удален
                changes.append(FileChange(
                    path=file_path,
                    change_type=ChangeType.DELETED,
                    old_hash=old_hash
                ))
            elif not old_hash and new_hash:
                # Файл добавлен
                changes.append(FileChange(
                    path=file_path,
                    change_type=ChangeType.ADDED,
                    new_hash=new_hash
                ))
            elif old_hash != new_hash:
                # Файл изменен
                changes.append(FileChange(
                    path=file_path,
                    change_type=ChangeType.MODIFIED,
                    old_hash=old_hash,
                    new_hash=new_hash
                ))
        
        return Diff(changes=changes, conflicts=[])
    
    def compute_worktree_diff(self, worktree_files: Dict[str, str], index_tree: Tree) -> Diff:
        """Вычислить diff между рабочими файлами и индексом"""
        changes = []
        
        all_files = set(worktree_files.keys()) | set(index_tree.entries.keys())
        
        for file_path in all_files:
            worktree_content = worktree_files.get(file_path)
            index_hash = index_tree.entries.get(file_path)
            
            if worktree_content is None and index_hash:
                # Файл удален в worktree
                changes.append(FileChange(
                    path=file_path,
                    change_type=ChangeType.DELETED,
                    old_hash=index_hash
                ))
            elif worktree_content and not index_hash:
                # Файл добавлен в worktree
                worktree_hash = hashlib.sha1(worktree_content.encode()).hexdigest()
                changes.append(FileChange(
                    path=file_path,
                    change_type=ChangeType.ADDED,
                    new_hash=worktree_hash
                ))
            elif worktree_content and index_hash:
                # Файл существует в обоих - проверяем изменения
                worktree_hash = hashlib.sha1(worktree_content.encode()).hexdigest()
                if worktree_hash != index_hash:
                    changes.append(FileChange(
                        path=file_path,
                        change_type=ChangeType.MODIFIED,
                        old_hash=index_hash,
                        new_hash=worktree_hash
                    ))
        
        return Diff(changes=changes, conflicts=[])
    
    def compute_staged_diff(self, index_tree: Tree, head_tree: Tree) -> Diff:
        """Вычислить diff между индексом и HEAD"""
        return self.compute_tree_diff(head_tree, index_tree)