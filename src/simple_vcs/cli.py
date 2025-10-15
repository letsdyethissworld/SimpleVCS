import argparse
import sys
from .commands import init, add, commit, log, status

def main():
    parser = argparse.ArgumentParser(description="Simple Version Control System")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
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
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "init":
            init()
        elif args.command == "add":
            add(args.files)
        elif args.command == "commit":
            commit(args.message)
        elif args.command == "log":
            log()
        elif args.command == "status":
            status()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()