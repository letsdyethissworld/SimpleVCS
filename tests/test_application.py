import pytest
from unittest.mock import Mock

from src.simple_vcs.application.services import AddService, CommitService

class TestAddService:
    def test_add_files_success(self, mock_repositories):
        mock_repo = mock_repositories
        mock_repo['worktree_repo'].file_exists.return_value = True
        mock_repo['worktree_repo'].read_file.return_value = "file content"
        mock_repo['index_repo'].get_index.return_value = Mock(entries={})
        
        service = AddService(
            mock_repo['object_repo'],
            mock_repo['index_repo'], 
            mock_repo['worktree_repo'],
            Mock()
        )
        
        result = service.execute(["test.txt"])
        
        assert "Added 1 files" in result
        mock_repo['object_repo'].save_blob.assert_called_once_with("file content")
        mock_repo['index_repo'].save_index.assert_called_once()

class TestCommitService:
    def test_commit_creation(self, mock_repositories):
        mock_repo = mock_repositories
        mock_repo['index_repo'].get_index.return_value = Mock(entries={"file.txt": "abc123"})
        mock_repo['reference_repo'].get_current_branch.return_value = "master"
        mock_repo['reference_repo'].get_branch_commit.return_value = "parent123"
        mock_repo['object_repo'].save_tree.return_value = "tree456"
        mock_repo['commit_service'].create_commit.return_value = "commit789"
        
        service = CommitService(
            mock_repo['object_repo'],
            mock_repo['reference_repo'],
            mock_repo['index_repo'],
            mock_repo['commit_service']
        )
        
        result = service.execute("Test message", "user")
        
        assert result == "commit789"
        mock_repo['object_repo'].save_tree.assert_called_once_with({"file.txt": "abc123"})