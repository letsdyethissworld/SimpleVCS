#!/usr/bin/env python3
"""
Basic usage example for Simple VCS
"""

import os
import tempfile
from pathlib import Path

def main():
    print("=== Simple VCS Basic Usage Example ===")
    
    # Create temporary directory for example
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        print(f"Working in: {tmpdir}")
        
        # Initialize VCS
        os.system("svcs init")
        
        # Create some files
        Path("hello.txt").write_text("Hello, VCS!")
        Path("readme.md").write_text("# My Project\n\nThis is a test project.")
        
        # Add files and commit
        print("\n1. Adding files and creating initial commit:")
        os.system("svcs add hello.txt readme.md")
        os.system('svcs commit -m "Initial commit"')
        
        # Modify a file and create second commit
        print("\n2. Modifying file and creating second commit:")
        Path("hello.txt").write_text("Hello, VCS! This is modified.")
        os.system("svcs add hello.txt")
        os.system('svcs commit -m "Update greeting"')
        
        # Show history
        print("\n3. Commit history:")
        os.system("svcs log")
        
        # Show status
        print("\n4. Current status:")
        os.system("svcs status")
        
        print("\n=== Example completed ===")

if __name__ == "__main__":
    main()