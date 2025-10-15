from pathlib import Path
from .core import SimpleVCS
from .repository import find_repo_root, ensure_repo_initialized

def init(path: str = ".") -> None:
    """Initialize a new repository"""
    vcs = SimpleVCS(path)
    vcs.init()

def add(files: list) -> None:
    """Add files to index"""
    repo_root = ensure_repo_initialized()
    vcs = SimpleVCS(repo_root)
    
    for file_path in files:
        vcs.add(file_path)

def commit(message: str) -> None:
    """Create a new commit"""
    repo_root = ensure_repo_initialized()
    vcs = SimpleVCS(repo_root)
    vcs.commit(message)

def log() -> None:
    """Show commit history"""
    repo_root = ensure_repo_initialized()
    vcs = SimpleVCS(repo_root)
    vcs.log()

def status() -> None:
    """Show repository status"""
    repo_root = ensure_repo_initialized()
    vcs = SimpleVCS(repo_root)
    vcs.status()