class SimpleVCSError(Exception):
    """Base exception for Simple VCS errors"""
    pass

class NotARepositoryError(SimpleVCSError):
    """Raised when not in a repository"""
    pass

class ObjectNotFoundError(SimpleVCSError):
    """Raised when an object is not found"""
    pass

class InvalidObjectError(SimpleVCSError):
    """Raised when an object is invalid"""
    pass