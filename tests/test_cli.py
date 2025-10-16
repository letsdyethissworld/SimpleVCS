# test_cli.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from simple_vcs.presentation.cli import SimpleVcsCli

if __name__ == "__main__":
    cli = SimpleVcsCli()
    cli.run()