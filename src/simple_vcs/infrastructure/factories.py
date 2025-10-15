from pathlib import Path

from ..domain.services import (
    HashService, CommitService, BranchService, 
    MergeService, RevertService, DiffService
)
from .repositories import (
    FileObjectRepository, FileReferenceRepository,
    FileIndexRepository, FileSystemWorktreeRepository
)
from .services import (
    SHA1HashService, SimpleCommitService, AdvancedBranchService,
    ThreeWayMergeService, GitStyleRevertService, UnifiedDiffService
)

class RepositoryFactory:
    """Фабрика для создания всех зависимостей системы"""
    
    def __init__(self, repo_path: Path = None):
        self.repo_path = repo_path or Path.cwd()
        self.vcs_path = self.repo_path / ".simple_vcs"
        
        # Создаем необходимые директории
        self.vcs_path.mkdir(exist_ok=True)
        (self.vcs_path / "objects").mkdir(exist_ok=True)
        (self.vcs_path / "refs").mkdir(exist_ok=True)
        (self.vcs_path / "refs" / "heads").mkdir(exist_ok=True)
    
    def create_object_repo(self) -> FileObjectRepository:
        """Создать репозиторий объектов"""
        return FileObjectRepository(self.vcs_path / "objects")
    
    def create_reference_repo(self) -> FileReferenceRepository:
        """Создать репозиторий ссылок"""
        return FileReferenceRepository(
            self.vcs_path / "refs",
            self.vcs_path / "HEAD"
        )
    
    def create_index_repo(self) -> FileIndexRepository:
        """Создать репозиторий индекса"""
        return FileIndexRepository(self.vcs_path / "index")
    
    def create_worktree_repo(self) -> FileSystemWorktreeRepository:
        """Создать репозиторий рабочей директории"""
        return FileSystemWorktreeRepository(self.repo_path)
    
    def create_hash_service(self) -> HashService:
        """Создать сервис хеширования"""
        return SHA1HashService()
    
    def create_commit_service(self) -> CommitService:
        """Создать сервис коммитов"""
        return SimpleCommitService(self.create_object_repo())
    
    def create_branch_service(self) -> BranchService:
        """Создать сервис веток"""
        return AdvancedBranchService(
            self.create_object_repo(),
            self.create_reference_repo()
        )
    
    def create_merge_service(self) -> MergeService:
        """Создать сервис слияния"""
        return ThreeWayMergeService(
            self.create_object_repo(),
            self.create_diff_service()
        )
    
    def create_revert_service(self) -> RevertService:
        """Создать сервис отката"""
        return GitStyleRevertService(
            self.create_object_repo(),
            self.create_diff_service()
        )
    
    def create_diff_service(self) -> DiffService:
        """Создать сервис diff"""
        return UnifiedDiffService(self.create_object_repo())