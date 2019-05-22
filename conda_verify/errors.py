from collections import namedtuple


class PackageError(Exception):
    """Exception to be raised when user wants to exit on error."""


class RecipeError(Exception):
    """Exception to be raised when user wants to exit on error."""


class Error(namedtuple("Error", ["file", "code", "message"])):
    """Error class creates error codes to be shown to the user."""

    def __str__(self):
        """Override namedtuple's __str__ so that error codes are readable."""
        return u"{}: {} {}".format(self.file, self.code, self.message)
