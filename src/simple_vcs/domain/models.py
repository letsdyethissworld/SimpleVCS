from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from abc import ABC

class ChangeType(Enum):
    ADDED = 'added'
    MODIFIED ='modified'
    DELETED = 'deleted'

@dataclass
class Blob:
    hash: str
    content: str
    size: str

@dataclass
class Tree:
    hash: str
    entries: Dict[str, str]

@dataclass
class Commit:
    hash: str
    tree_hash: str
    parent_hashes: List[str]
    message: str
    author: str
    timestamp: datetime
    commiter: str

@dataclass
class Branch:
    name: str
    commit_hash: str

@dataclass
class Index:
    entries: Dict[str, str]

@dataclass
class FileChange:
    path: str
    change_type: ChangeType
    old_hash: Optional[str] = None
    new_hash: Optional[str] = None

@dataclass
class Diff:
    changes: List[FileChange]
    conflicts: List[str]

@dataclass  
class MergeResult:
    success: bool
    conflicts: List[str]
    merged_tree_hash: Optional[str] = None

@dataclass
class Conflict:
    file_path: str
    our_content: str
    their_content: str
    base_content: str