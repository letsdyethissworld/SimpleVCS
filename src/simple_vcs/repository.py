from pathlib import Path
from typing import Optional

def find_repo_root(path: str = ".") -> Optional[Path]:
    """Find repository root directory"""
    current = Path(path).resolve()
    
    while current != current.parent:
        vcs_dir = current / ".simple_vcs"
        if vcs_dir.exists() and vcs_dir.is_dir():
            return current
        current = current.parent
    
    return None

def ensure_repo_initialized(path: str = ".") -> Path:
    """Ensure repository is initialized or raise error"""
    repo_root = find_repo_root(path)
    if not repo_root:
        raise RuntimeError("Not a Simple VCS repository (or any parent directory)")
    return repo_root