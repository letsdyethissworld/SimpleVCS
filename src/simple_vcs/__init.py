"""
Simple VCS - A simple version control system with DDD/SOLID architecture.
"""

__version__ = "0.2.0"
__author__ = "Kawori"

from .domain.models import Blob, Tree, Commit, FileChange, ChangeType
from .domain.repositories import (
    ObjectRepository, ReferenceRepository, 
    IndexRepository, WorktreeRepository
)
from .domain.services import (
    HashService, CommitService, BranchService,
    MergeService, RevertService, DiffService
)

__all__ = [
    # Models
    "Blob", "Tree", "Commit", "FileChange", "ChangeType",
    # Repository interfaces
    "ObjectRepository", "ReferenceRepository", "IndexRepository", "WorktreeRepository",
    # Service interfaces
    "HashService", "CommitService", "BranchService", "MergeService", "RevertService", "DiffService",
]