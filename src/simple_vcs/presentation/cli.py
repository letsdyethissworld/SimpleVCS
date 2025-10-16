import argparse
import sys
from typing import Dict, Type

from .commands import CommandHandler, CommandResult
from .command_handlers import (
    InitCommand, AddCommand, CommitCommand, BranchCommand,
    CheckoutCommand, MergeCommand, RevertCommand, DiffCommand,
    LogCommand, StatusCommand, ShowCommand, RestoreCommand
)

class CommandRegistry:
    """Реестр всех доступных команд"""
    
    def __init__(self):
        self._commands: Dict[str, CommandHandler] = {}
        self._register_commands()
    
    def _register_commands(self):
        """Регистрация всех команд"""
        commands = [
            InitCommand(), AddCommand(), CommitCommand(), BranchCommand(),
            CheckoutCommand(), MergeCommand(), RevertCommand(), DiffCommand(),
            LogCommand(), StatusCommand(), ShowCommand(), RestoreCommand()
        ]
        
        for command in commands:
            self._commands[command.name] = command
    
    def get_command(self, name: str) -> CommandHandler:
        """Получить команду по имени"""
        return self._commands.get(name)
    
    def list_commands(self) -> Dict[str, str]:
        """Получить список всех команд с описаниями"""
        return {name: handler.description for name, handler in self._commands.items()}

class SimpleVcsCli:
    """Упрощенный CLI с использованием Command Handlers"""
    
    def __init__(self):
        self.registry = CommandRegistry()
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Создание главного парсера аргументов"""
        parser = argparse.ArgumentParser(
            description="Simple Version Control System",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=self._create_epilog()
        )
        
        subparsers = parser.add_subparsers(
            dest="command",
            title="available commands",
            metavar="command"
        )
        
        # Динамически создаем подпарсеры для каждой команды
        for command_name, command_handler in self.registry._commands.items():
            subparser = subparsers.add_parser(
                command_name,
                help=command_handler.description
            )
            command_handler.setup_parser(subparser)
        
        return parser
    
    def _create_epilog(self) -> str:
        """Создание эпилога с примерами использования"""
        examples = [
            "Examples:",
            "  svcs init",
            "  svcs add file1.txt file2.py", 
            "  svcs commit -m 'Initial commit'",
            "  svcs branch feature-new",
            "  svcs checkout feature-new",
            "  svcs merge main",
            "  svcs diff",
            "  svcs revert abc123def",
            "  svcs show main.py",
            "  svcs restore main.py --staged"
        ]
        return "\n".join(examples)
    
    def run(self):
        """Запуск CLI"""
        args = self.parser.parse_args()
        
        if not args.command:
            self.parser.print_help()
            return
        
        command_handler = self.registry.get_command(args.command)
        if not command_handler:
            print(f"Unknown command: {args.command}")
            self.parser.print_help()
            sys.exit(1)
        
        try:
            # Выполняем команду
            result = command_handler.handle(args)
            
            # Обрабатываем результат
            if result.success:
                if result.message:
                    print(result.message)
            else:
                print(f"Error: {result.message}")
                sys.exit(1)
                
        except Exception as e:
            # Обрабатываем исключения
            error_message = command_handler.error(e)
            print(error_message)
            sys.exit(1)

def main():
    """Точка входа для консольной команды"""
    cli = SimpleVcsCli()
    cli.run()

if __name__ == "__main__":
    main()