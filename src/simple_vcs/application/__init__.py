from .services import (
    InitService, AddService, CommitService, 
    BranchService, LogService, StatusService,
    CheckoutService, MergeServiceApp, RevertServiceApp, DiffServiceApp,
    ShowService, RestoreService  # добавляем новые сервисы
)

__all__ = [
    "InitService", "AddService", "CommitService", 
    "BranchService", "LogService", "StatusService",
    "CheckoutService", "MergeServiceApp", "RevertServiceApp", "DiffServiceApp",
    "ShowService", "RestoreService"  # добавляем новые сервисы
]