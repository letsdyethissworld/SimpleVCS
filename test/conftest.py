import pytest
import tempfile
import os
from pathlib import Path

@pytest.fixture
def temp_repo():
    """Create a temporary repository for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        yield repo_path

@pytest.fixture
def initialized_repo(temp_repo):
    """Create and initialize a repository"""
    from src.simple_vcs.core import SimpleVCS
    vcs = SimpleVCS(str(temp_repo))
    vcs.init()
    return temp_repo