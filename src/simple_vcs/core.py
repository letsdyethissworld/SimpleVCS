import os
import hashlib
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

class SimpleVCS:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.vcs_path = self.repo_path / ".simple_vcs"
        self.objects_path = self.vcs_path / "objects"
        self.refs_path = self.vcs_path / "refs"
        self.head_path = self.vcs_path / "HEAD"
        
    def init(self) -> None:
        """Initialize a new repository"""
        self.vcs_path.mkdir(exist_ok=True)
        self.objects_path.mkdir(exist_ok=True)
        self.refs_path.mkdir(exist_ok=True)
        
        if not self.head_path.exists():
            self.head_path.write_text("ref: refs/heads/master")
            print("Initialized empty SimpleVCS repository")

    def _get_hash(self, data: str) -> str:
        """Generate hash for content"""
        return hashlib.sha1(data.encode()).hexdigest()

    def _write_object(self, data: str, obj_type: str = "blob") -> str:
        """Write object to storage"""
        obj_hash = self._get_hash(data)
        obj_dir = self.objects_path / obj_hash[:2]
        obj_dir.mkdir(exist_ok=True)
        obj_path = obj_dir / obj_hash[2:]
        
        obj_data = f"{obj_type} {len(data)}\0{data}"
        obj_path.write_bytes(obj_data.encode())
        return obj_hash

    def _read_object(self, obj_hash: str) -> Optional[Tuple[str, str]]:
        """Read object from storage"""
        obj_path = self.objects_path / obj_hash[:2] / obj_hash[2:]
        if not obj_path.exists():
            return None
            
        content = obj_path.read_text()
        header, data = content.split('\0', 1)
        obj_type, size = header.split(' ')
        return obj_type, data

    def add(self, file_path: str) -> None:
        """Add file to index"""
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            print(f"File {file_path} does not exist")
            return
            
        content = file_path_obj.read_text()
        blob_hash = self._write_object(content, "blob")
        
        index_path = self.vcs_path / "index"
        index: Dict[str, str] = {}
        if index_path.exists():
            index = json.loads(index_path.read_text())
            
        index[str(file_path)] = blob_hash
        index_path.write_text(json.dumps(index))
        
        print(f"Added {file_path}")

    def commit(self, message: str) -> None:
        """Create a commit"""
        index_path = self.vcs_path / "index"
        if not index_path.exists():
            print("No files in index")
            return
            
        index = json.loads(index_path.read_text())
        
        tree_data = json.dumps(index)
        tree_hash = self._write_object(tree_data, "tree")
        
        commit_data = {
            "tree": tree_hash,
            "parent": self._get_current_commit(),
            "message": message,
            "timestamp": time.time(),
            "author": os.getenv("USER", "unknown")
        }
        
        commit_hash = self._write_object(json.dumps(commit_data), "commit")
        self._update_head(commit_hash)
        
        print(f"Created commit {commit_hash[:8]}: {message}")

    def _get_current_commit(self) -> Optional[str]:
        """Get current commit"""
        if self.head_path.exists():
            head_content = self.head_path.read_text().strip()
            if head_content.startswith("ref:"):
                ref_path = self.vcs_path / head_content[5:]
                if ref_path.exists():
                    return ref_path.read_text().strip()
        return None

    def _update_head(self, commit_hash: str) -> None:
        """Update HEAD reference"""
        head_content = self.head_path.read_text().strip()
        if head_content.startswith("ref:"):
            ref_path = self.vcs_path / head_content[5:]
            ref_path.parent.mkdir(exist_ok=True)
            ref_path.write_text(commit_hash)

    def log(self) -> None:
        """Show commit history"""
        current_commit = self._get_current_commit()
        while current_commit:
            result = self._read_object(current_commit)
            if not result or result[0] != "commit":
                break
                
            commit_type, commit_data = result
            commit_info = json.loads(commit_data)
            timestamp = time.strftime(
                "%Y-%m-%d %H:%M:%S", 
                time.localtime(commit_info["timestamp"])
            )
            
            print(f"commit {current_commit[:8]}")
            print(f"Author: {commit_info['author']}")
            print(f"Date: {timestamp}")
            print(f"    {commit_info['message']}\n")
            
            current_commit = commit_info["parent"]

    def status(self) -> None:
        """Show repository status"""
        print("Repository status:")
        
        index_path = self.vcs_path / "index"
        if not index_path.exists():
            print("No files tracked")
            return
            
        index = json.loads(index_path.read_text())
        for file_path, stored_hash in index.items():
            file_obj = Path(file_path)
            if file_obj.exists():
                current_content = file_obj.read_text()
                current_hash = self._get_hash(current_content)
                if current_hash != stored_hash:
                    print(f"modified: {file_path}")
            else:
                print(f"deleted: {file_path}")