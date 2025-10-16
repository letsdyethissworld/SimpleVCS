import argparse
from typing import List
from pathlib import Path

from .commands import CommandHandler, CommandResult
from ..infrastructure.factories import RepositoryFactory
from ..application.services import (
    InitService, AddService, CommitService, BranchService, 
    LogService, StatusService, CheckoutService, MergeServiceApp,
    RevertServiceApp, DiffServiceApp, ShowService, RestoreService
)

class InitCommand(CommandHandler):
    """Команда инициализации репозитория"""
    
    @property
    def name(self) -> str:
        return "init"
    
    @property
    def description(self) -> str:
        return "Initialize a new repository"
    
    def handle(self, args: argparse.Namespace) -> CommandResult:
        factory = RepositoryFactory()
        service = InitService(
            factory.create_object_repo(),
            factory.create_reference_repo(),
            factory.create_index_repo()
        )
        result = service.execute()
        return CommandResult(True, result)

class AddCommand(CommandHandler):
    """Команда добавления файлов"""
    
    @property
    def name(self) -> str:
        return "add"
    
    @property
    def description(self) -> str:
        return "Add files to index"
    
    def setup_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("files", nargs="+", help="Files to add")
    
    def handle(self, args: argparse.Namespace) -> CommandResult:
        factory = RepositoryFactory()
        service = AddService(
            factory.create_object_repo(),
            factory.create_index_repo(),
            factory.create_worktree_repo(),
            factory.create_hash_service()
        )
        result = service.execute(args.files)
        return CommandResult(True, result)

class CommitCommand(CommandHandler):
    """Команда создания коммита"""
    
    @property
    def name(self) -> str:
        return "commit"
    
    @property
    def description(self) -> str:
        return "Create a new commit"
    
    def setup_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("-m", "--message", required=True, help="Commit message")
    
    def handle(self, args: argparse.Namespace) -> CommandResult:
        factory = RepositoryFactory()
        service = CommitService(
            factory.create_object_repo(),
            factory.create_reference_repo(),
            factory.create_index_repo(),
            factory.create_commit_service()
        )
        commit_hash = service.execute(args.message, "user")
        return CommandResult(True, f"Created commit {commit_hash[:8]}")

class BranchCommand(CommandHandler):
    """Команда работы с ветками"""
    
    @property
    def name(self) -> str:
        return "branch"
    
    @property
    def description(self) -> str:
        return "Branch operations"
    
    def setup_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("name", nargs="?", help="Branch name to create")
        parser.add_argument("-l", "--list", action="store_true", help="List branches")
        parser.add_argument("-d", "--delete", action="store_true", help="Delete branch")
    
    def handle(self, args: argparse.Namespace) -> CommandResult:
        factory = RepositoryFactory()
        service = BranchService(factory.create_reference_repo())
        
        if args.list:
            branches = service.list_branches()
            current = factory.create_reference_repo().get_current_branch()
            message = "Branches:\n" + "\n".join(
                f"{'* ' if branch == current else '  '}{branch}" 
                for branch in branches
            )
            return CommandResult(True, message)
        
        elif args.delete and args.name:
            result = service.delete_branch(args.name)
            return CommandResult(True, result)
        
        elif args.name:
            result = service.create_branch(args.name)
            return CommandResult(True, result)
        
        else:
            # Default to listing
            branches = service.list_branches()
            current = factory.create_reference_repo().get_current_branch()
            message = "Branches:\n" + "\n".join(
                f"{'* ' if branch == current else '  '}{branch}" 
                for branch in branches
            )
            return CommandResult(True, message)

class CheckoutCommand(CommandHandler):
    """Команда переключения веток"""
    
    @property
    def name(self) -> str:
        return "checkout"
    
    @property
    def description(self) -> str:
        return "Checkout branch or commit"
    
    def setup_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("target", help="Branch name or commit hash")
    
    def handle(self, args: argparse.Namespace) -> CommandResult:
        factory = RepositoryFactory()
        service = CheckoutService(
            factory.create_object_repo(),
            factory.create_reference_repo(),
            factory.create_worktree_repo(),
            factory.create_index_repo()
        )
        result = service.execute(args.target)
        return CommandResult(True, result)

class MergeCommand(CommandHandler):
    """Команда слияния веток"""
    
    @property
    def name(self) -> str:
        return "merge"
    
    @property
    def description(self) -> str:
        return "Merge branches"
    
    def setup_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("branch", help="Branch to merge into current")
    
    def handle(self, args: argparse.Namespace) -> CommandResult:
        factory = RepositoryFactory()
        service = MergeServiceApp(
            factory.create_object_repo(),
            factory.create_reference_repo(),
            factory.create_merge_service(),
            factory.create_commit_service()
        )
        result = service.execute(args.branch)
        return CommandResult(True, result)

class RevertCommand(CommandHandler):
    """Команда отката коммита"""
    
    @property
    def name(self) -> str:
        return "revert"
    
    @property
    def description(self) -> str:
        return "Revert a commit"
    
    def setup_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("commit", help="Commit hash to revert")
    
    def handle(self, args: argparse.Namespace) -> CommandResult:
        factory = RepositoryFactory()
        service = RevertServiceApp(
            factory.create_object_repo(),
            factory.create_reference_repo(),
            factory.create_revert_service(),
            factory.create_commit_service()
        )
        result = service.execute(args.commit)
        return CommandResult(True, result)

class DiffCommand(CommandHandler):
    """Команда показа различий"""
    
    @property
    def name(self) -> str:
        return "diff"
    
    @property
    def description(self) -> str:
        return "Show changes"
    
    def setup_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("--staged", action="store_true", help="Show staged changes")
        parser.add_argument("commit1", nargs="?", help="First commit for comparison")
        parser.add_argument("commit2", nargs="?", help="Second commit for comparison")
    
    def handle(self, args: argparse.Namespace) -> CommandResult:
        factory = RepositoryFactory()
        service = DiffServiceApp(
            factory.create_object_repo(),
            factory.create_reference_repo(),
            factory.create_index_repo(),
            factory.create_worktree_repo(),
            factory.create_diff_service()
        )
        
        if args.staged:
            service.execute_staged_diff()
        elif args.commit1 and args.commit2:
            service.execute_commit_diff(args.commit1, args.commit2)
        elif args.commit1:
            current_branch = factory.create_reference_repo().get_current_branch()
            if current_branch:
                current_commit = factory.create_reference_repo().get_branch_commit(current_branch)
                if current_commit:
                    service.execute_commit_diff(args.commit1, current_commit)
                else:
                    return CommandResult(False, "No current commit")
            else:
                return CommandResult(False, "Not on any branch")
        else:
            service.execute_worktree_diff()
        
        return CommandResult(True, "")

class LogCommand(CommandHandler):
    """Команда показа истории"""
    
    @property
    def name(self) -> str:
        return "log"
    
    @property
    def description(self) -> str:
        return "Show commit history"
    
    def handle(self, args: argparse.Namespace) -> CommandResult:
        factory = RepositoryFactory()
        service = LogService(
            factory.create_object_repo(),
            factory.create_reference_repo()
        )
        service.execute()
        return CommandResult(True, "")

class StatusCommand(CommandHandler):
    """Команда показа статуса"""
    
    @property
    def name(self) -> str:
        return "status"
    
    @property
    def description(self) -> str:
        return "Show repository status"
    
    def handle(self, args: argparse.Namespace) -> CommandResult:
        factory = RepositoryFactory()
        service = StatusService(
            factory.create_object_repo(),
            factory.create_index_repo(),
            factory.create_worktree_repo()
        )
        service.execute()
        return CommandResult(True, "")

class ShowCommand(CommandHandler):
    """Команда показа содержимого файлов или коммитов"""
    
    @property
    def name(self) -> str:
        return "show"
    
    @property
    def description(self) -> str:
        return "Show file content or commit information"
    
    def setup_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("target", help="File path or commit hash")
        parser.add_argument("commit", nargs="?", help="Commit hash (for files)")
    
    def handle(self, args: argparse.Namespace) -> CommandResult:
        factory = RepositoryFactory()
        service = ShowService(
            factory.create_object_repo(),
            factory.create_reference_repo()
        )
        
        # Упрощенная и более надежная логика
        try:
            # Сначала пробуем как коммит
            result = service.execute_commit(args.target)
            return CommandResult(True, result)
        except ValueError:
            # Если не коммит, пробуем как файл
            try:
                content = service.execute_file(args.target, args.commit)
                return CommandResult(True, content)
            except ValueError as e:
                return CommandResult(False, f"Error: {e}")

class RestoreCommand(CommandHandler):
    """Команда восстановления файлов"""
    
    @property
    def name(self) -> str:
        return "restore"
    
    @property
    def description(self) -> str:
        return "Restore files from repository"
    
    def setup_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("file", help="File path to restore")
        parser.add_argument("commit", nargs="?", help="Commit hash (default: HEAD)")
        parser.add_argument("--staged", action="store_true", help="Restore from index")
    
    def handle(self, args: argparse.Namespace) -> CommandResult:
        factory = RepositoryFactory()
        service = RestoreService(
            factory.create_object_repo(),
            factory.create_reference_repo(),
            factory.create_worktree_repo(),
            factory.create_index_repo()
        )
        result = service.execute(args.file, args.commit, args.staged)
        return CommandResult(True, result)