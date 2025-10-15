"""Simple VCS - A simple version control system"""

__version__ = "0.1.0"
__author__ = "Your Name"

from .core import SimpleVCS
from .commands import add, commit, init, log, status

__all__ = ["SimpleVCS", "add", "commit", "init", "log", "status"]