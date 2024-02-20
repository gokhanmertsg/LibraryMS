class NotFoundException(ValueError):
    pass

class InvalidPassword(ValueError):
    pass

class ForbiddenError(ValueError):
    """Raise when user doesn't have access for given entity."""

    def __init__(self, message="Forbidden"):
        """Initialize the class."""
        self.message = message
        super().__init__(self.message)