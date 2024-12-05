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
    def get_emails(self, batch_size: int, folder: str = None, query: dict = None):
        """
        Fetches the messages based on the query provided.

        Args:
            folder (str): Folder name to fetch the messages from
            batch_size (int): Number of messages to fetch in a single batch
            query (dict, optional): Query . Defaults to {"in": "inbox"}.

        Yields:
            List of message objects containing:
            - id: str
            - subject: str
            - from: Dict[name: str, email: str]
            - received_timestamp: int
            - body: str
            - attachments: List[Dict[name: str, link: str]]
            - message_id: str
            - to: List[Dict[name: str, email: str]]
            - cc: List[Dict[name: str, email: str]]
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

    def mark_as_read(self, message_id: str):
        """
        Marks the message as read.

        Args:
            message_id (str): Message ID to mark as read
        """
        raise NotImplementedError("Subclasses must implement this method")

    def move_to_folder(self, message_id: str, folder: str):
        """
        Moves the message to the specified folder.

        Args:
            message_id (str): Message ID to mark as read
            current_folders (list): List of current folders
            folder (str): Folder name to move the message to
        """
        raise NotImplementedError("Subclasses must implement this method")
