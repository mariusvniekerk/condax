class CondaxError(Exception):
    """Base class for known condax errors which are to be graciously presented to the user."""

    def __init__(self, exit_code, message: str):
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code
