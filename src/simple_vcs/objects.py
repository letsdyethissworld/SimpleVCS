import hashlib
from pathlib import Path
from typing import Optional, Tuple

def hash_object(data: str) -> str:
    """Generate SHA1 hash for content"""
    return hashlib.sha1(data.encode()).hexdigest()

def write_object(repo_path: Path, data: str, obj_type: str = "blob") -> str:
    """Write object to repository"""
    obj_hash = hash_object(data)
    obj_dir = repo_path / "objects" / obj_hash[:2]
    obj_dir.mkdir(exist_ok=True)
    obj_file = obj_dir / obj_hash[2:]
    
    obj_content = f"{obj_type} {len(data)}\0{data}"
    obj_file.write_text(obj_content)
    return obj_hash

def read_object(repo_path: Path, obj_hash: str) -> Optional[Tuple[str, str]]:
    """Read object from repository"""
    obj_file = repo_path / "objects" / obj_hash[:2] / obj_hash[2:]
    if not obj_file.exists():
        return None
        
    content = obj_file.read_text()
    header, data = content.split('\0', 1)
    obj_type, size = header.split(' ')
    return obj_type, data