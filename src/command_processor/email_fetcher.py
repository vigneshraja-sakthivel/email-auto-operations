"""
This module contains the EmailFetcher class, which is responsible for fetching emails
from an email client and storing them in the database. It implements the
CommandProcessorInterface and uses various repositories to manage users, folders,
and emails in the database.

Classes:
    EmailFetcher: Fetches emails from the email client and stores them in the database.
"""

from logging import getLogger
from command_processor.command_processor_interface import CommandProcessorInterface
from email_clients.email_client_interface import EmailClientInterface
from db.db_client import DbClient
from repositories.email import EmailRepository
from repositories.folder import FolderRepository
from repositories.user import UserRepository

logger = getLogger(__name__)


class EmailFetcher(CommandProcessorInterface):
    """
    EmailFetcher is responsible for fetching emails from an email client
    and storing them in the database.
    """

    _email_client: EmailClientInterface = None
    _db_client: DbClient = None

    def __init__(
        self,
        email_client: EmailClientInterface,
        db_client: DbClient,
    ):
        self._email_client = email_client
        self._db_client = db_client

    def execute(self, params):
        """
        Fetch emails from the email client and store them in the database.
        """
        user_email_address = self._email_client.authenticate()
        user_id = self._process_user(user_email_address)
        self._process_folders(user_id)
        self._process_emails(user_id)

    def _process_user(self, email_address: str) -> int:
        """
        Upsert the user in the database.

        Args:
            email_address (str): Email address of the user

        Returns:
            int: User ID
        """
        user_repository = UserRepository()
        return user_repository.upsert_user(email_address)

    def _process_emails(self, user_id: int, folder: str = None):
        """
        Fetch emails from the email client and store them in the database.

        Args:
            user_id (int): User ID
            folder (str, optional): Folder name. Defaults to None.
        """
        folder_repository = FolderRepository()
        folders = folder_repository.get_all_folders(user_id)
        folder_map = {folder["name"]: folder["id"] for folder in folders}
        for messages in self._email_client.get_emails(folder):
            for message in messages:
                self._process_email(user_id, message, folder_map)

    def _process_folders(self, user_id: int):
        """
        Fetch folders from the email client and store them in the database.

        Args:
            user_id (int): User ID
        """
        folders = self._email_client.get_folders()
        folder_repository = FolderRepository()
        for folder in folders:
            folder_repository.upsert_folder(user_id, folder)

    def _process_email(self, user_id: int, message: dict, folder_map: dict):
        """
        Process an email message and store it in the database.

        Args:
            user_id (int): User ID
            message (dict): Details of the email message
            folder_map (dict): Dictionary mapping folder names to folder IDs
        """
        try:
            email_repository = EmailRepository()
            folder_ids = [
                folder_map[folder_name]
                for folder_name in message["folders"]
                if folder_name in folder_map
            ]
            email_repository.upsert_email(user_id, message, folder_ids)
        except Exception as e:
            logger.error("Error processing email: %s, Message ID: %s", e, message["id"])
