#!/usr/bin/env python3
"""
Development environment setup script for Simple VCS
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description=None):
    """Run a shell command with description"""
    if description:
        print(f"\n=== {description} ===")
    print(f"Running: {command}")
    
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Error running: {command}")
        return False
    return True

def main():
    print("Setting up Simple VCS development environment...")
    
    # Get project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Install in development mode
    if not run_command("pip install -e .", "Installing package in development mode"):
        sys.exit(1)
    
    # Install development dependencies
    if not run_command('pip install -e ".[dev]"', "Installing development dependencies"):
        sys.exit(1)
    
    # Run tests to verify installation
    if not run_command("pytest tests/ -v", "Running tests to verify installation"):
        print("Warning: Tests failed, but installation completed")
    
    print("\n=== Development environment setup complete! ===")
    print("\nYou can now:")
    print("1. Run tests: pytest tests/")
    print("2. Use the CLI: svcs --help")
    print("3. Try examples: python examples/basic_usage.py")

if __name__ == "__main__":
    main()