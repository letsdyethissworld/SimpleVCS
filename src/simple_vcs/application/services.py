from typing import List, Optional, Dict
from pathlib import Path
from datetime import datetime

from ..domain.models import Commit, Index, Tree, Diff
from ..domain.repositories import (
    ObjectRepository, ReferenceRepository, 
    IndexRepository, WorktreeRepository
)
from ..domain.services import (
    HashService, CommitService as DomainCommitService, 
    BranchService as DomainBranchService, MergeService, 
    RevertService, DiffService
)
from ..infrastructure.repositories import FileIndexRepository

class InitService:
    """Сервис для инициализации репозитория"""
    
    def __init__(self, 
                 object_repo: ObjectRepository,
                 reference_repo: ReferenceRepository,
                 index_repo: IndexRepository):
        self.object_repo = object_repo
        self.reference_repo = reference_repo
        self.index_repo = index_repo
    
    def execute(self) -> str:
        """Выполнить инициализацию репозитория"""
        # Инициализация выполняется при создании репозиториев
        # Устанавливаем начальное состояние
        self.reference_repo.set_current_branch("master")
        self.index_repo.clear_index()
        return "Initialized empty Simple VCS repository"

class AddService:
    """Сервис для добавления файлов в индекс"""
    
    def __init__(self,
                 object_repo: ObjectRepository,
                 index_repo: IndexRepository,
                 worktree_repo: WorktreeRepository,
                 hash_service: HashService):
        self.object_repo = object_repo
        self.index_repo = index_repo
        self.worktree_repo = worktree_repo
        self.hash_service = hash_service
    
    def execute(self, file_paths: List[str]) -> str:
        """Добавить файлы в индекс"""
        index = self.index_repo.get_index()
        
        for file_path in file_paths:
            if not self.worktree_repo.file_exists(file_path):
                raise FileNotFoundError(f"File {file_path} does not exist")
            
            content = self.worktree_repo.read_file(file_path)
            blob_hash = self.object_repo.save_blob(content)
            index.entries[file_path] = blob_hash
        
        self.index_repo.save_index(index)
        return f"Added {len(file_paths)} files to index"

class CommitService:
    """Сервис для создания коммитов"""
    
    def __init__(self,
                 object_repo: ObjectRepository,
                 reference_repo: ReferenceRepository,
                 index_repo: IndexRepository,
                 commit_service: DomainCommitService):
        self.object_repo = object_repo
        self.reference_repo = reference_repo
        self.index_repo = index_repo
        self.commit_service = commit_service
    
    def execute(self, message: str, author: str) -> str:
        """Создать коммит"""
        index = self.index_repo.get_index()
        if not index.entries:
            raise ValueError("No files in index to commit")
        
        # Создаем tree из индекса
        tree_hash = self.object_repo.save_tree(index.entries)
        
        # Получаем текущий коммит для родителя
        current_branch = self.reference_repo.get_current_branch()
        parent_hashes = []
        if current_branch:
            parent_hash = self.reference_repo.get_branch_commit(current_branch)
            if parent_hash:
                parent_hashes.append(parent_hash)
        
        # Создаем коммит через доменный сервис
        commit_hash = self.commit_service.create_commit(
            tree_hash=tree_hash,
            message=message,
            parent_hashes=parent_hashes,
            author=author
        )
        
        # Обновляем ветку
        if current_branch:
            self.reference_repo.set_branch_commit(current_branch, commit_hash)
        
        # Очищаем индекс после коммита
        self.index_repo.clear_index()
        
        return commit_hash

class BranchService:
    """Сервис для работы с ветками"""
    
    def __init__(self, reference_repo: ReferenceRepository):
        self.reference_repo = reference_repo
    
    def list_branches(self) -> List[str]:
        """Получить список веток"""
        return self.reference_repo.list_branches()
    
    def create_branch(self, branch_name: str) -> str:
        """Создать ветку от текущего коммита"""
        current_branch = self.reference_repo.get_current_branch()
        if not current_branch:
            raise ValueError("No current branch")
        
        current_commit = self.reference_repo.get_branch_commit(current_branch)
        if not current_commit:
            raise ValueError("Current branch has no commits")
        
        self.reference_repo.create_branch(branch_name, current_commit)
        return f"Created branch '{branch_name}'"
    
    def delete_branch(self, branch_name: str) -> str:
        """Удалить ветку"""
        current_branch = self.reference_repo.get_current_branch()
        if current_branch == branch_name:
            raise ValueError("Cannot delete current branch")
        
        branches = self.reference_repo.list_branches()
        if branch_name not in branches:
            raise ValueError(f"Branch '{branch_name}' does not exist")
        
        # В реальной реализации здесь была бы проверка на слияние
        # Для простоты просто удаляем
        branch_path = self.reference_repo.refs_path / "heads" / branch_name
        if branch_path.exists():
            branch_path.unlink()
        
        return f"Deleted branch '{branch_name}'"

class LogService:
    """Сервис для показа истории коммитов"""
    
    def __init__(self,
                 object_repo: ObjectRepository,
                 reference_repo: ReferenceRepository):
        self.object_repo = object_repo
        self.reference_repo = reference_repo
    
    def execute(self):
        """Показать историю коммитов"""
        current_branch = self.reference_repo.get_current_branch()
        if not current_branch:
            print("No commits yet")
            return
        
        current_commit_hash = self.reference_repo.get_branch_commit(current_branch)
        if not current_commit_hash:
            print("No commits yet")
            return
        
        commit_hash = current_commit_hash
        while commit_hash:
            commit = self.object_repo.get_commit(commit_hash)
            if not commit:
                break
            
            # Форматируем время
            timestamp = commit.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"commit {commit_hash[:8]}")
            print(f"Author: {commit.author}")
            print(f"Date: {timestamp}")
            print(f"    {commit.message}\n")
            
            # Переходим к родителю
            commit_hash = commit.parent_hashes[0] if commit.parent_hashes else None

class StatusService:
    """Сервис для показа статуса репозитория"""
    
    def __init__(self,
                 object_repo: ObjectRepository,
                 index_repo: IndexRepository,
                 worktree_repo: WorktreeRepository):
        self.object_repo = object_repo
        self.index_repo = index_repo
        self.worktree_repo = worktree_repo
    
    def execute(self):
        """Показать статус репозитория"""
        print("Repository status:")
        
        # Проверяем изменения между рабочими файлами и индексом
        index = self.index_repo.get_index()
        has_changes = False
        
        for file_path in self.worktree_repo.list_files():
            if file_path not in index.entries:
                print(f"untracked: {file_path}")
                has_changes = True
            else:
                current_content = self.worktree_repo.read_file(file_path)
                current_hash = hashlib.sha1(current_content.encode()).hexdigest()
                if current_hash != index.entries[file_path]:
                    print(f"modified: {file_path}")
                    has_changes = True
        
        # Проверяем удаленные файлы
        for file_path in index.entries:
            if not self.worktree_repo.file_exists(file_path):
                print(f"deleted: {file_path}")
                has_changes = True
        
        if not has_changes:
            print("working tree clean")

class CheckoutService:
    """Сервис для переключения между ветками и коммитами"""
    
    def __init__(self,
                 object_repo: ObjectRepository,
                 reference_repo: ReferenceRepository,
                 worktree_repo: WorktreeRepository,
                 index_repo: IndexRepository):
        self.object_repo = object_repo
        self.reference_repo = reference_repo
        self.worktree_repo = worktree_repo
        self.index_repo = index_repo
    
    def execute(self, target: str) -> str:
        """Переключиться на ветку или коммит"""
        # Проверяем, является ли target веткой
        branches = self.reference_repo.list_branches()
        if target in branches:
            return self._checkout_branch(target)
        else:
            return self._checkout_commit(target)
    
    def _checkout_branch(self, branch_name: str) -> str:
        """Переключиться на ветку"""
        commit_hash = self.reference_repo.get_branch_commit(branch_name)
        if not commit_hash:
            raise ValueError(f"Branch '{branch_name}' has no commits")
        
        self._restore_commit_state(commit_hash)
        self.reference_repo.set_current_branch(branch_name)
        return f"Switched to branch '{branch_name}'"
    
    def _checkout_commit(self, commit_hash: str) -> str:
        """Переключиться на коммит (detached HEAD)"""
        if not self.object_repo.exists(commit_hash):
            raise ValueError(f"Commit '{commit_hash}' does not exist")
        
        commit = self.object_repo.get_commit(commit_hash)
        if not commit:
            raise ValueError(f"Commit '{commit_hash}' not found")
        
        self._restore_commit_state(commit_hash)
        # В detached HEAD просто записываем хеш коммита в HEAD
        self.reference_repo.head_path.write_text(commit_hash)
        return f"HEAD is now at {commit_hash[:8]}"
    
    def _restore_commit_state(self, commit_hash: str):
        """Восстановить состояние из коммита"""
        commit = self.object_repo.get_commit(commit_hash)
        if not commit:
            raise ValueError(f"Commit '{commit_hash}' not found")
        
        tree = self.object_repo.get_tree(commit.tree_hash)
        if not tree:
            raise ValueError(f"Tree for commit '{commit_hash}' not found")
        
        # Очищаем рабочую директорию
        current_files = self.worktree_repo.list_files()
        for file_path in current_files:
            # В реальной реализации нужно аккуратно удалять файлы
            # Для простоты просто очищаем содержимое
            self.worktree_repo.write_file(file_path, "")
        
        # Восстанавливаем файлы из tree
        for file_path, blob_hash in tree.entries.items():
            blob = self.object_repo.get_blob(blob_hash)
            if blob:
                self.worktree_repo.write_file(file_path, blob.content)
        
        # Обновляем индекс
        self.index_repo.save_index(Index(entries=tree.entries))

class MergeServiceApp:
    """Сервис для слияния веток"""
    
    def __init__(self,
                 object_repo: ObjectRepository,
                 reference_repo: ReferenceRepository,
                 merge_service: MergeService,
                 commit_service: DomainCommitService):
        self.object_repo = object_repo
        self.reference_repo = reference_repo
        self.merge_service = merge_service
        self.commit_service = commit_service
    
    def execute(self, source_branch: str) -> str:
        """Выполнить слияние ветки в текущую"""
        current_branch = self.reference_repo.get_current_branch()
        if not current_branch:
            raise ValueError("Not on any branch")
        
        if current_branch == source_branch:
            raise ValueError("Cannot merge branch into itself")
        
        source_commit_hash = self.reference_repo.get_branch_commit(source_branch)
        if not source_commit_hash:
            raise ValueError(f"Branch '{source_branch}' has no commits")
        
        current_commit_hash = self.reference_repo.get_branch_commit(current_branch)
        if not current_commit_hash:
            raise ValueError("Current branch has no commits")
        
        # Проверяем fast-forward merge
        if self.merge_service.is_fast_forward(current_commit_hash, source_commit_hash):
            return self._fast_forward_merge(source_branch, source_commit_hash)
        
        # Выполняем трехстороннее слияние
        return self._three_way_merge(current_branch, current_commit_hash, source_branch, source_commit_hash)
    
    def _fast_forward_merge(self, source_branch: str, source_commit_hash: str) -> str:
        """Выполнить fast-forward слияние"""
        current_branch = self.reference_repo.get_current_branch()
        self.reference_repo.set_branch_commit(current_branch, source_commit_hash)
        return f"Fast-forward merge from '{source_branch}'"
    
    def _three_way_merge(self, current_branch: str, current_commit_hash: str, 
                        source_branch: str, source_commit_hash: str) -> str:
        """Выполнить трехстороннее слияние"""
        # Находим общего предка
        common_ancestor_hash = self.merge_service.find_common_ancestor(
            current_commit_hash, source_commit_hash
        )
        if not common_ancestor_hash:
            raise ValueError("Cannot find common ancestor for merge")
        
        # Получаем деревья для трехстороннего слияния
        base_tree = self.object_repo.get_tree(
            self.object_repo.get_commit(common_ancestor_hash).tree_hash
        )
        our_tree = self.object_repo.get_tree(
            self.object_repo.get_commit(current_commit_hash).tree_hash
        )
        their_tree = self.object_repo.get_tree(
            self.object_repo.get_commit(source_commit_hash).tree_hash
        )
        
        # Выполняем слияние
        merge_result = self.merge_service.three_way_merge(base_tree, our_tree, their_tree)
        
        if not merge_result.success:
            conflicts_str = ", ".join(merge_result.conflicts)
            return f"Merge conflicts detected in: {conflicts_str}"
        
        # Создаем merge commit
        commit_hash = self.commit_service.create_commit(
            tree_hash=merge_result.merged_tree_hash,
            message=f"Merge branch '{source_branch}' into {current_branch}",
            parent_hashes=[current_commit_hash, source_commit_hash],
            author="user"  # В реальной системе брали бы из конфига
        )
        
        # Обновляем текущую ветку
        self.reference_repo.set_branch_commit(current_branch, commit_hash)
        return f"Successfully merged '{source_branch}' into '{current_branch}'"

class RevertServiceApp:
    """Сервис для отката коммитов"""
    
    def __init__(self,
                 object_repo: ObjectRepository,
                 reference_repo: ReferenceRepository,
                 revert_service: RevertService,
                 commit_service: DomainCommitService):
        self.object_repo = object_repo
        self.reference_repo = reference_repo
        self.revert_service = revert_service
        self.commit_service = commit_service
    
    def execute(self, commit_hash: str) -> str:
        """Откатить указанный коммит"""
        commit_to_revert = self.object_repo.get_commit(commit_hash)
        if not commit_to_revert:
            raise ValueError(f"Commit '{commit_hash}' not found")
        
        if not commit_to_revert.parent_hashes:
            raise ValueError("Cannot revert initial commit")
        
        # Получаем родительский коммит
        parent_commit = self.object_repo.get_commit(commit_to_revert.parent_hashes[0])
        if not parent_commit:
            raise ValueError("Parent commit not found")
        
        # Вычисляем патч для отката
        revert_patch = self.revert_service.compute_revert_patch(commit_to_revert, parent_commit)
        
        # Получаем текущее состояние
        current_branch = self.reference_repo.get_current_branch()
        current_commit_hash = self.reference_repo.get_branch_commit(current_branch)
        current_commit = self.object_repo.get_commit(current_commit_hash)
        current_tree = self.object_repo.get_tree(current_commit.tree_hash)
        
        # Применяем откат
        reverted_tree = self.revert_service.apply_revert(current_tree, revert_patch)
        
        # Создаем коммит отката
        new_commit_hash = self.commit_service.create_commit(
            tree_hash=reverted_tree.hash,
            message=f"Revert \"{commit_to_revert.message}\"",
            parent_hashes=[current_commit_hash],
            author="user"
        )
        
        # Обновляем ветку
        self.reference_repo.set_branch_commit(current_branch, new_commit_hash)
        return f"Created revert commit {new_commit_hash[:8]}"

class DiffServiceApp:
    """Сервис для показа различий"""
    
    def __init__(self,
                 object_repo: ObjectRepository,
                 reference_repo: ReferenceRepository,
                 index_repo: IndexRepository,
                 worktree_repo: WorktreeRepository,
                 diff_service: DiffService):
        self.object_repo = object_repo
        self.reference_repo = reference_repo
        self.index_repo = index_repo
        self.worktree_repo = worktree_repo
        self.diff_service = diff_service
    
    def execute_worktree_diff(self):
        """Показать diff между рабочими файлами и индексом"""
        index = self.index_repo.get_index()
        index_tree = Tree(hash="", entries=index.entries)
        
        worktree_files = {}
        for file_path in self.worktree_repo.list_files():
            content = self.worktree_repo.read_file(file_path)
            worktree_files[file_path] = content
        
        diff = self.diff_service.compute_worktree_diff(worktree_files, index_tree)
        self._print_diff(diff, "Changes not staged for commit")
    
    def execute_staged_diff(self):
        """Показать diff между индексом и HEAD"""
        current_branch = self.reference_repo.get_current_branch()
        if not current_branch:
            print("No commits yet")
            return
        
        current_commit_hash = self.reference_repo.get_branch_commit(current_branch)
        current_commit = self.object_repo.get_commit(current_commit_hash)
        head_tree = self.object_repo.get_tree(current_commit.tree_hash)
        
        index = self.index_repo.get_index()
        index_tree = Tree(hash="", entries=index.entries)
        
        diff = self.diff_service.compute_staged_diff(index_tree, head_tree)
        self._print_diff(diff, "Changes to be committed")
    
    def execute_commit_diff(self, commit1_hash: str, commit2_hash: str):
        """Показать diff между двумя коммитами"""
        commit1 = self.object_repo.get_commit(commit1_hash)
        commit2 = self.object_repo.get_commit(commit2_hash)
        
        if not commit1 or not commit2:
            raise ValueError("One or both commits not found")
        
        tree1 = self.object_repo.get_tree(commit1.tree_hash)
        tree2 = self.object_repo.get_tree(commit2.tree_hash)
        
        diff = self.diff_service.compute_tree_diff(tree1, tree2)
        self._print_diff(diff, f"Diff between {commit1_hash[:8]} and {commit2_hash[:8]}")
    
    def _print_diff(self, diff: Diff, title: str):
        """Напечатать diff в понятном формате"""
        print(f"=== {title} ===")
        
        if not diff.changes:
            print("No changes")
            return
        
        for change in diff.changes:
            if change.change_type == ChangeType.ADDED:
                print(f"+++ Added: {change.path}")
            elif change.change_type == ChangeType.DELETED:
                print(f"--- Deleted: {change.path}")
            elif change.change_type == ChangeType.MODIFIED:
                print(f"*** Modified: {change.path}")
                
                # Показываем diff содержимого если есть
                if change.old_hash and change.new_hash:
                    old_blob = self.object_repo.get_blob(change.old_hash)
                    new_blob = self.object_repo.get_blob(change.new_hash)
                    if old_blob and new_blob:
                        file_diff = self.diff_service.compute_file_diff(
                            old_blob.content, new_blob.content
                        )
                        for line in file_diff:
                            print(line)