from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from pathlib import Path

from .models import Blob, Tree, Commit, Branch, Index

class ObjectRepository(ABC):
    """Абстракция для хранилища объектов (blobs, trees, commits)"""
    
    @abstractmethod
    def save_blob(self, content: str) -> str:
        """Сохранить blob объект и вернуть его хеш"""
        pass
    
    @abstractmethod
    def get_blob(self, hash: str) -> Optional[Blob]:
        """Получить blob объект по хешу"""
        pass
    
    @abstractmethod
    def save_tree(self, entries: Dict[str, str]) -> str:
        """Сохранить tree объект и вернуть его хеш"""
        pass
    
    @abstractmethod
    def get_tree(self, hash: str) -> Optional[Tree]:
        """Получить tree объект по хешу"""
        pass
    
    @abstractmethod
    def save_commit(self, commit: Commit) -> str:
        """Сохранить commit объект и вернуть его хеш"""
        pass
    
    @abstractmethod
    def get_commit(self, hash: str) -> Optional[Commit]:
        """Получить commit объект по хешу"""
        pass
    
    @abstractmethod
    def exists(self, hash: str) -> bool:
        """Проверить существование объекта"""
        pass

class ReferenceRepository(ABC):
    """Абстракция для управления ссылками (ветки, HEAD)"""
    
    @abstractmethod
    def get_current_branch(self) -> Optional[str]:
        """Получить текущую ветку"""
        pass
    
    @abstractmethod
    def set_current_branch(self, branch_name: str):
        """Установить текущую ветку"""
        pass
    
    @abstractmethod
    def get_branch_commit(self, branch_name: str) -> Optional[str]:
        """Получить коммит, на который указывает ветка"""
        pass
    
    @abstractmethod
    def set_branch_commit(self, branch_name: str, commit_hash: str):
        """Установить коммит для ветки"""
        pass
    
    @abstractmethod
    def list_branches(self) -> List[str]:
        """Получить список всех веток"""
        pass
    
    @abstractmethod
    def create_branch(self, branch_name: str, commit_hash: str):
        """Создать новую ветку"""
        pass

class IndexRepository(ABC):
    """Абстракция для работы с индексом"""
    
    @abstractmethod
    def get_index(self) -> Index:
        """Получить текущий индекс"""
        pass
    
    @abstractmethod
    def save_index(self, index: Index):
        """Сохранить индекс"""
        pass
    
    @abstractmethod
    def clear_index(self):
        """Очистить индекс"""
        pass

class WorktreeRepository(ABC):
    """Абстракция для работы с рабочими файлами"""
    
    @abstractmethod
    def read_file(self, path: str) -> str:
        """Прочитать файл из рабочей директории"""
        pass
    
    @abstractmethod
    def write_file(self, path: str, content: str):
        """Записать файл в рабочую директорию"""
        pass
    
    @abstractmethod
    def file_exists(self, path: str) -> bool:
        """Проверить существование файла"""
        pass
    
    @abstractmethod
    def list_files(self) -> List[str]:
        """Получить список всех файлов в рабочей директории"""
        pass