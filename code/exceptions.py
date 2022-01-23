class EntryNotFound(Exception):
    """Raised when a requested entry is not found in the database."""

    def __init__(self, message):
        super().__init__(message)

        self.message = message


class EntryAlreadyExists(Exception):
    """Raised when a requested entry already exists in the database."""

    def __init__(self, message):
        super().__init__(message)

        self.message = message
