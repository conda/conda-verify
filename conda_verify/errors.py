from collections import namedtuple


class PackageError(Exception):
    """Exception to be raised when user wants to exit on error."""


class RecipeError(Exception):
    """Exception to be raised when user wants to exit on error."""


class Error(namedtuple('Error', ['code', 'message'])):
    """Error class creates error codes to be shown to the user."""

    def __repr__(self):
        """Override namedtuple's __repr__ so that error codes are readable."""
        return '{} {}' .format(self.code, self.message)
