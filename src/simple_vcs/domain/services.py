from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Tuple

from .models import Commit, Blob, Tree, Diff, MergeResult, Conflict

class HashService(ABC):
    """Сервис для вычисления хешей"""
    
    @abstractmethod
    def compute_hash(self, data: str) -> str:
        """Вычислить хеш данных"""
        pass

class CommitService(ABC):
    """Сервис для работы с коммитами"""
    
    @abstractmethod
    def create_commit(self, tree_hash: str, message: str, 
                     parent_hashes: List[str], author: str) -> str:
        """Создать коммит и вернуть его хеш"""
        pass

class BranchService(ABC):
    """Сервис для работы с ветками"""
    
    @abstractmethod
    def create_branch(self, branch_name: str, from_commit: str) -> str:
        """Создать ветку от указанного коммита"""
        pass
    
    @abstractmethod
    def delete_branch(self, branch_name: str):
        """Удалить ветку"""
        pass
    
    @abstractmethod
    def get_branch_history(self, branch_name: str) -> List[Commit]:
        """Получить историю коммитов ветки"""
        pass

class MergeService(ABC):
    """Сервис для слияния веток"""
    
    @abstractmethod
    def find_common_ancestor(self, commit1: str, commit2: str) -> Optional[str]:
        """Найти общего предка двух коммитов"""
        pass
    
    @abstractmethod
    def three_way_merge(self, base: Tree, ours: Tree, theirs: Tree) -> MergeResult:
        """Выполнить трехстороннее слияние"""
        pass
    
    @abstractmethod
    def detect_conflicts(self, our_changes: Diff, their_changes: Diff) -> List[Conflict]:
        """Обнаружить конфликты при слиянии"""
        pass
    
    @abstractmethod
    def is_fast_forward(self, from_commit: str, to_commit: str) -> bool:
        """Проверить, является ли слияние fast-forward"""
        pass

class RevertService(ABC):
    """Сервис для отката коммитов"""
    
    @abstractmethod
    def compute_revert_patch(self, commit_to_revert: Commit, parent_commit: Commit) -> Diff:
        """Вычислить патч для отката коммита"""
        pass
    
    @abstractmethod
    def apply_revert(self, current_tree: Tree, revert_patch: Diff) -> Tree:
        """Применить патч отката к текущему состоянию"""
        pass

class DiffService(ABC):
    """Сервис для вычисления различий"""
    
    @abstractmethod
    def compute_file_diff(self, old_content: str, new_content: str) -> List[str]:
        """Вычислить различия между двумя версиями файла"""
        pass
    
    @abstractmethod
    def compute_tree_diff(self, old_tree: Tree, new_tree: Tree) -> Diff:
        """Вычислить различия между двумя деревьями"""
        pass
    
    @abstractmethod
    def compute_worktree_diff(self, worktree_files: Dict[str, str], index_tree: Tree) -> Diff:
        """Вычислить различия между рабочими файлами и индексом"""
        pass
    
    @abstractmethod
    def compute_staged_diff(self, index_tree: Tree, head_tree: Tree) -> Diff:
        """Вычислить различия между индексом и HEAD"""
        pass