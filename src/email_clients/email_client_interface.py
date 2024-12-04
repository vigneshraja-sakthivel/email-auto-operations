"""
Email client interface defining standard email operations.
"""

from abc import ABC, abstractmethod


class EmailClientInterface(ABC):
    """Interface for email client implementations."""

    @abstractmethod
    def __init__(self, config: dict) -> None:
        """
        Initialize email client with configuration.

        Args:
            config: Dictionary containing client configuration
                   Required keys: credentials_path, token_path

        Raises:
            ValueError: If required config is missing
            FileNotFoundError: If credential file not found
        """
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def authenticate(self, params: dict = None):
        """
        Authenticate with email service.

        Args:
            params: Dictionary containing parameters required for authentication
        """
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def get_emails(self, folder: str = None, query: dict = None):
        """
        Fetch messages matching query criteria.

        Args:
            query: Dictionary of search criteria
                  Supported keys: from, to, subject, in, before, after
                  Default: {"in": "inbox"}

        Yields:
            List of message objects containing:
            - subject: str
            - from: Dict[name: str, email: str]
            - timestamp: int
            - body: str
        """
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def get_folders(self):
        """
        Fetch list of folders in the email account.

        Returns:
            List of folder objects containing:
                - name: str
                - folder_id: str
                - type: str
        """
        raise NotImplementedError("Subclasses must implement this method")
