from abc import ABC, abstractmethod
from typing import Any, Dict
import argparse

class CommandHandler(ABC):
    """Абстрактный базовый класс для всех команд"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Имя команды (например, 'init', 'add')"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Описание команды для справки"""
        pass
    
    def setup_parser(self, parser: argparse.ArgumentParser):
        """Настройка парсера аргументов для команды"""
        pass
    
    @abstractmethod
    def handle(self, args: argparse.Namespace) -> Any:
        """Обработка команды"""
        pass
    
    def success(self, result: Any) -> str:
        """Форматирование успешного результата"""
        return str(result) if result else "Command completed successfully"
    
    def error(self, exception: Exception) -> str:
        """Форматирование ошибки"""
        return f"Error: {exception}"

class CommandResult:
    """Результат выполнения команды"""
    
    def __init__(self, success: bool, message: str = "", data: Any = None):
        self.success = success
        self.message = message
        self.data = data
    
    def __str__(self):
        return self.message