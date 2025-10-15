#!/usr/bin/env python3
"""
Advanced usage example for Simple VCS
"""

import os
import tempfile
from pathlib import Path

def main():
    print("=== Simple VCS Advanced Usage Example ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        print(f"Working in: {tmpdir}")
        
        # Initialize and create initial commit
        os.system("svcs init")
        Path("main.py").write_text("print('Hello')")
        os.system("svcs add main.py")
        os.system('svcs commit -m "Initial commit"')
        
        # Create and switch to feature branch
        print("\n1. Creating feature branch:")
        os.system("svcs branch feature-new")
        os.system("svcs checkout feature-new")
        
        # Make changes in feature branch
        Path("feature.py").write_text("def new_feature(): pass")
        os.system("svcs add feature.py")
        os.system('svcs commit -m "Add new feature"')
        
        # Switch back to main and merge
        print("\n2. Merging feature branch:")
        os.system("svcs checkout main")
        os.system("svcs merge feature-new")
        
        # Show diff
        print("\n3. Showing differences:")
        os.system("svcs diff")
        
        # Show branch list
        print("\n4. Branch list:")
        os.system("svcs branch -l")
        
        print("\n=== Advanced example completed ===")

if __name__ == "__main__":
    main()