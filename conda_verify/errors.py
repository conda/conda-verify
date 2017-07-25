from collections import namedtuple


class Error(namedtuple('Error', ['file', 'line_number', 'code', 'message'])):
    """Error class creates error codes to be shown to the user."""

    def __repr__(self):
        """Override namedtuple's __repr__ so that error codes are readable."""
        return '{}:{}: {} {}' .format(self.file, self.line_number, self.code, self.message)
