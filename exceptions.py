class AppError(Exception):
    """Base class for application exceptions."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class DatabaseError(AppError):
    """Raised when a database operation fails."""

    pass


class NotFoundError(AppError):
    """Raised when a resource is not found."""

    pass


class ValidationError(AppError):
    """Raised when input validation fails."""

    pass
