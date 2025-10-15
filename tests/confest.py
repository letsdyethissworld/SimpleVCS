import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock

@pytest.fixture
def temp_repo():
    """Создать временный репозиторий для тестирования"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_repositories():
    """Создать моки всех репозиториев"""
    return {
        'object_repo': Mock(),
        'reference_repo': Mock(),
        'index_repo': Mock(),
        'worktree_repo': Mock()
    }