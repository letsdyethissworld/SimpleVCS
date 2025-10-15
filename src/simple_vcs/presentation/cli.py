import argparse
import sys
from pathlib import Path

from ..infrastructure.factories import RepositoryFactory
from ..application.services import (
    InitService, AddService, CommitService, 
    BranchService, LogService, StatusService,
    CheckoutService, MergeServiceApp, RevertServiceApp, DiffServiceApp
)

class CLI:
    """Командный интерфейс Simple VCS"""
    
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Simple Version Control System",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  svcs init
  svcs add file1.txt file2.py
  svcs commit -m "Initial commit"
  svcs branch feature-new
  svcs checkout feature-new
  svcs merge main
  svcs diff
  svcs revert abc123def
            """
        )
        self.setup_parser()
    
    def setup_parser(self):
        """Настройка парсера аргументов командной строки"""
        subparsers = self.parser.add_subparsers(
            dest="command", 
            title="available commands",
            metavar="command"
        )
        
        # init command
        subparsers.add_parser("init", help="Initialize a new repository")
        
        # add command
        add_parser = subparsers.add_parser("add", help="Add files to index")
        add_parser.add_argument("files", nargs="+", help="Files to add")
        
        # commit command
        commit_parser = subparsers.add_parser("commit", help="Create a new commit")
        commit_parser.add_argument("-m", "--message", required=True, help="Commit message")
        
        # log command
        subparsers.add_parser("log", help="Show commit history")
        
        # status command
        subparsers.add_parser("status", help="Show repository status")
        
        # branch command
        branch_parser = subparsers.add_parser("branch", help="Branch operations")
        branch_parser.add_argument("name", nargs="?", help="Branch name to create")
        branch_parser.add_argument("-l", "--list", action="store_true", help="List branches")
        branch_parser.add_argument("-d", "--delete", action="store_true", help="Delete branch")
        
        # checkout command
        checkout_parser = subparsers.add_parser("checkout", help="Checkout branch or commit")
        checkout_parser.add_argument("target", help="Branch name or commit hash")
        
        # merge command
        merge_parser = subparsers.add_parser("merge", help="Merge branches")
        merge_parser.add_argument("branch", help="Branch to merge into current")
        
        # revert command
        revert_parser = subparsers.add_parser("revert", help="Revert a commit")
        revert_parser.add_argument("commit", help="Commit hash to revert")
        
        # diff command
        diff_parser = subparsers.add_parser("diff", help="Show changes")
        diff_parser.add_argument("--staged", action="store_true", help="Show staged changes")
        diff_parser.add_argument("commit1", nargs="?", help="First commit for comparison")
        diff_parser.add_argument("commit2", nargs="?", help="Second commit for comparison")
    
    def run(self):
        """Запуск CLI"""
        args = self.parser.parse_args()
        
        if not args.command:
            self.parser.print_help()
            return
        
        try:
            factory = RepositoryFactory()
            
            if args.command == "init":
                service = InitService(
                    factory.create_object_repo(),
                    factory.create_reference_repo(),
                    factory.create_index_repo()
                )
                result = service.execute()
                print(result)
                
            elif args.command == "add":
                service = AddService(
                    factory.create_object_repo(),
                    factory.create_index_repo(),
                    factory.create_worktree_repo(),
                    factory.create_hash_service()
                )
                result = service.execute(args.files)
                print(result)
                
            elif args.command == "commit":
                service = CommitService(
                    factory.create_object_repo(),
                    factory.create_reference_repo(),
                    factory.create_index_repo(),
                    factory.create_commit_service()
                )
                commit_hash = service.execute(args.message, "user")
                print(f"Created commit {commit_hash[:8]}")
                
            elif args.command == "branch":
                service = BranchService(factory.create_reference_repo())
                if args.list:
                    branches = service.list_branches()
                    current = factory.create_reference_repo().get_current_branch()
                    print("Branches:")
                    for branch in branches:
                        prefix = "* " if branch == current else "  "
                        print(f"{prefix}{branch}")
                elif args.delete and args.name:
                    result = service.delete_branch(args.name)
                    print(result)
                elif args.name:
                    result = service.create_branch(args.name)
                    print(result)
                else:
                    # Default to listing branches
                    branches = service.list_branches()
                    current = factory.create_reference_repo().get_current_branch()
                    print("Branches:")
                    for branch in branches:
                        prefix = "* " if branch == current else "  "
                        print(f"{prefix}{branch}")
                        
            elif args.command == "checkout":
                service = CheckoutService(
                    factory.create_object_repo(),
                    factory.create_reference_repo(),
                    factory.create_worktree_repo(),
                    factory.create_index_repo()
                )
                result = service.execute(args.target)
                print(result)
                
            elif args.command == "merge":
                service = MergeServiceApp(
                    factory.create_object_repo(),
                    factory.create_reference_repo(),
                    factory.create_merge_service(),
                    factory.create_commit_service()
                )
                result = service.execute(args.branch)
                print(result)
                
            elif args.command == "revert":
                service = RevertServiceApp(
                    factory.create_object_repo(),
                    factory.create_reference_repo(),
                    factory.create_revert_service(),
                    factory.create_commit_service()
                )
                result = service.execute(args.commit)
                print(result)
                
            elif args.command == "diff":
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
                    # Diff between commit and current state
                    current_branch = factory.create_reference_repo().get_current_branch()
                    if current_branch:
                        current_commit = factory.create_reference_repo().get_branch_commit(current_branch)
                        if current_commit:
                            service.execute_commit_diff(args.commit1, current_commit)
                        else:
                            print("No current commit")
                    else:
                        print("Not on any branch")
                else:
                    # Default to worktree diff
                    service.execute_worktree_diff()
                    
            elif args.command == "log":
                service = LogService(
                    factory.create_object_repo(),
                    factory.create_reference_repo()
                )
                service.execute()
                
            elif args.command == "status":
                service = StatusService(
                    factory.create_object_repo(),
                    factory.create_index_repo(),
                    factory.create_worktree_repo()
                )
                service.execute()
                
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

def main():
    """Точка входа для консольной команды"""
    cli = CLI()
    cli.run()

if __name__ == "__main__":
    main()