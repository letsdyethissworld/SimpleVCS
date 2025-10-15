import pytest
import tempfile
import os
from pathlib import Path
from src.simple_vcs.core import SimpleVCS

class TestSimpleVCS:
    def test_init(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            vcs = SimpleVCS(tmpdir)
            vcs.init()
            
            repo_dir = Path(tmpdir) / ".simple_vcs"
            assert repo_dir.exists()
            assert (repo_dir / "objects").exists()
            assert (repo_dir / "refs").exists()
            assert (repo_dir / "HEAD").exists()
            
            head_content = (repo_dir / "HEAD").read_text()
            assert head_content.startswith("ref: refs/heads/master")

    def test_add_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            vcs = SimpleVCS(tmpdir)
            vcs.init()
            
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("Hello, World!")
            
            vcs.add("test.txt")
            
            index_file = Path(tmpdir) / ".simple_vcs" / "index"
            assert index_file.exists()
            
            index_content = index_file.read_text()
            assert "test.txt" in index_content

    def test_commit(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            vcs = SimpleVCS(tmpdir)
            vcs.init()
            
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("Hello, World!")
            
            vcs.add("test.txt")
            vcs.commit("Initial commit")
            
            # Check that objects were created
            objects_dir = Path(tmpdir) / ".simple_vcs" / "objects"
            assert any(objects_dir.rglob("*"))