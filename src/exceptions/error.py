"""
This module defines custom exception classes for the email-auto-operations package.
"""


class ConfigError(Exception):
    """
    Exception raised for errors in the authentication process.
    """

    def __init__(self, message="Authentication failed"):
        self.message = message
        super().__init__(self.message)


class AuthenticationError(Exception):
    """
    Exception raised for errors in the authentication process.
    """

    def __init__(self, message="Authentication failed"):
        self.message = message
        super().__init__(self.message)
