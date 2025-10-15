import pytest
import tempfile
from pathlib import Path
from src.simple_vcs.repository import find_repo_root, ensure_repo_initialized

class TestRepository:
    def test_find_repo_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create repo in root
            repo_dir = tmpdir_path / ".simple_vcs"
            repo_dir.mkdir()
            
            # Create subdirectory
            subdir = tmpdir_path / "subdir"
            subdir.mkdir()
            
            found_root = find_repo_root(str(subdir))
            assert found_root == tmpdir_path

    def test_ensure_repo_initialized(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Should raise error when no repo
            with pytest.raises(RuntimeError):
                ensure_repo_initialized(str(tmpdir))
            
            # Create repo
            repo_dir = tmpdir_path / ".simple_vcs"
            repo_dir.mkdir()
            
            # Should not raise
            root = ensure_repo_initialized(str(tmpdir))
            assert root == tmpdir_path