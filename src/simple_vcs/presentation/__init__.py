"""
Presentation layer - user interfaces (CLI, web, etc.)
"""

from .cli import SimpleVcsCli, main
from .commands import CommandHandler, CommandResult
from .command_handlers import (
    InitCommand, AddCommand, CommitCommand, BranchCommand,
    CheckoutCommand, MergeCommand, RevertCommand, DiffCommand,
    LogCommand, StatusCommand, ShowCommand, RestoreCommand
)

__all__ = [
    "SimpleVcsCli", "main",
    "CommandHandler", "CommandResult",
    "InitCommand", "AddCommand", "CommitCommand", "BranchCommand",
    "CheckoutCommand", "MergeCommand", "RevertCommand", "DiffCommand", 
    "LogCommand", "StatusCommand", "ShowCommand", "RestoreCommand"
]