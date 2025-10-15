#!/usr/bin/env python3
"""
Basic usage example for Simple VCS
"""

import os
import tempfile
from pathlib import Path
from src.simple_vcs.core import SimpleVCS

def main():
    print("=== Simple VCS Basic Usage Example ===")
    
    # Create temporary directory for example
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        print(f"Working in: {tmpdir}")
        
        # Initialize repository
        vcs = SimpleVCS()
        vcs.init()
        
        # Create some files
        Path("hello.txt").write_text("Hello, VCS!")
        Path("readme.md").write_text("# My Project\n\nThis is a test project.")
        
        # Add files to index
        print("\n1. Adding files to index:")
        vcs.add("hello.txt")
        vcs.add("readme.md")
        
        # Create first commit
        print("\n2. Creating first commit:")
        vcs.commit("Initial commit with basic files")
        
        # Modify a file
        print("\n3. Modifying hello.txt:")
        Path("hello.txt").write_text("Hello, VCS! This is modified.")
        vcs.add("hello.txt")
        vcs.commit("Update greeting message")
        
        # Show history
        print("\n4. Commit history:")
        vcs.log()
        
        # Show status
        print("\n5. Current status:")
        vcs.status()
        
        print("\n=== Example completed ===")

if __name__ == "__main__":
    main()