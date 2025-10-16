import hashlib
import json
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from datetime import datetime

from ..domain.models import Blob, Tree, Commit, Branch, Index
from ..domain.repositories import (
    ObjectRepository, ReferenceRepository, 
    IndexRepository, WorktreeRepository
)

class FileObjectRepository(ObjectRepository):
    """Реализация хранилища объектов в файловой системе"""
    
    def __init__(self, objects_path: Path):
        self.objects_path = objects_path
        
    def save_blob(self, content: str) -> str:
        """Сохранить blob объект"""
        blob_hash = self._compute_hash(content)
        self._write_object(blob_hash, "blob", content)
        return blob_hash
        
    def get_blob(self, hash: str) -> Optional[Blob]:
        """Получить blob объект"""
        result = self._read_object(hash)
        if not result or result[0] != "blob":
            return None
        obj_type, content = result
        return Blob(hash=hash, content=content, size=len(content))
    
    def save_tree(self, entries: Dict[str, str]) -> str:
        """Сохранить tree объект"""
        tree_data = json.dumps(entries, sort_keys=True)
        tree_hash = self._compute_hash(tree_data)
        self._write_object(tree_hash, "tree", tree_data)
        return tree_hash
        
    def get_tree(self, hash: str) -> Optional[Tree]:
        """Получить tree объект"""
        result = self._read_object(hash)
        if not result or result[0] != "tree":
            return None
        obj_type, content = result
        entries = json.loads(content)
        return Tree(hash=hash, entries=entries)
    
    def save_commit(self, commit: Commit) -> str:
        """Сохранить commit объект"""
        commit_data = {
            "tree": commit.tree_hash,
            "parents": commit.parent_hashes,
            "message": commit.message,
            "author": commit.author,
            "timestamp": commit.timestamp.isoformat(),
            "commiter": commit.commiter
        }
        serialized = json.dumps(commit_data, sort_keys=True)
        commit_hash = self._compute_hash(serialized)
        self._write_object(commit_hash, "commit", serialized)
        return commit_hash
        
    def get_commit(self, hash: str) -> Optional[Commit]:
        """Получить commit объект"""
        result = self._read_object(hash)
        if not result or result[0] != "commit":
            return None
        obj_type, content = result
        data = json.loads(content)
        return Commit(
            hash=hash,
            tree_hash=data["tree"],
            parent_hashes=data["parents"],
            message=data["message"],
            author=data["author"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            commiter=data.get("commiter", data["author"])
        )
    
    def exists(self, hash: str) -> bool:
        """Проверить существование объекта"""
        obj_path = self.objects_path / hash[:2] / hash[2:]
        return obj_path.exists()
    
    def _compute_hash(self, data: str) -> str:
        """Вычислить SHA1 хеш"""
        return hashlib.sha1(data.encode()).hexdigest()
    
    def _write_object(self, obj_hash: str, obj_type: str, data: str):
        """Записать объект в файл"""
        obj_dir = self.objects_path / obj_hash[:2]
        obj_dir.mkdir(exist_ok=True)
        obj_path = obj_dir / obj_hash[2:]
        
        obj_data = f"{obj_type} {len(data)}\0{data}"
        obj_path.write_text(obj_data)
    
    def _read_object(self, obj_hash: str) -> Optional[Tuple[str, str]]:
        """Прочитать объект из файла"""
        obj_path = self.objects_path / obj_hash[:2] / obj_hash[2:]
        if not obj_path.exists():
            return None
            
        content = obj_path.read_text()
        header, data = content.split('\0', 1)
        obj_type, size = header.split(' ')
        return obj_type, data

class FileReferenceRepository(ReferenceRepository):
    """Реализация хранилища ссылок в файловой системе"""
    
    def __init__(self, refs_path: Path, head_path: Path):
        self.refs_path = refs_path
        self.head_path = head_path
        
    def get_current_branch(self) -> Optional[str]:
        """Получить текущую ветку"""
        if not self.head_path.exists():
            return None
        content = self.head_path.read_text().strip()
        if content.startswith("ref: refs/heads/"):
            return content.split("/")[-1]
        return None
    
    def set_current_branch(self, branch_name: str):
        """Установить текущую ветку"""
        self.head_path.write_text(f"ref: refs/heads/{branch_name}")
    
    def get_branch_commit(self, branch_name: str) -> Optional[str]:
        """Получить коммит ветки"""
        branch_path = self.refs_path / "heads" / branch_name
        if branch_path.exists():
            return branch_path.read_text().strip()
        return None
    
    def set_branch_commit(self, branch_name: str, commit_hash: str):
        """Установить коммит для ветки"""
        branch_path = self.refs_path / "heads" / branch_name
        branch_path.parent.mkdir(parents=True, exist_ok=True)
        branch_path.write_text(commit_hash)
    
    def list_branches(self) -> List[str]:
        """Получить список веток"""
        branches_dir = self.refs_path / "heads"
        if not branches_dir.exists():
            return []
        return [f.name for f in branches_dir.iterdir() if f.is_file()]
    
    def create_branch(self, branch_name: str, commit_hash: str):
        """Создать ветку"""
        self.set_branch_commit(branch_name, commit_hash)

class FileIndexRepository(IndexRepository):
    """Реализация хранилища индекса в файловой системе"""
    
    def __init__(self, index_path: Path):
        self.index_path = index_path
        
    def get_index(self) -> Index:
        """Получить индекс"""
        if not self.index_path.exists():
            return Index(entries={})
        content = self.index_path.read_text()
        entries = json.loads(content)
        return Index(entries=entries)
    
    def save_index(self, index: Index):
        """Сохранить индекс"""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.index_path.write_text(json.dumps(index.entries, sort_keys=True, indent=2))
    
    def clear_index(self):
        """Очистить индекс"""
        if self.index_path.exists():
            self.index_path.unlink()

class FileSystemWorktreeRepository(WorktreeRepository):
    """Реализация работы с файловой системой"""
    
    def __init__(self, worktree_path: Path):
        self.worktree_path = worktree_path
        
    def read_file(self, path: str) -> str:
        """Прочитать файл"""
        file_path = self.worktree_path / path
        return file_path.read_text()
    
    def write_file(self, path: str, content: str):
        """Записать файл"""
        file_path = self.worktree_path / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
    
    def file_exists(self, path: str) -> bool:
        """Проверить существование файла"""
        return (self.worktree_path / path).exists()
    
    def list_files(self) -> List[str]:
        """Получить список файлов"""
        files = []
        for file_path in self.worktree_path.rglob("*"):
            if file_path.is_file() and not self._is_vcs_file(file_path):
                relative_path = file_path.relative_to(self.worktree_path)
                files.append(str(relative_path))
        return files
    
    def _is_vcs_file(self, file_path: Path) -> bool:
        """Проверить, является ли файл служебным VCS"""
        return ".simple_vcs" in file_path.parts