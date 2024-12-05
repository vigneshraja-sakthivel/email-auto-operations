"""
Gmail API client module for email operations.

This module provides a client interface to interact with Gmail API for:
- Authentication with OAuth2
- Fetching emails with query filters
- Parsing email messages and attachments
- Batch processing of messages

Usage:
    client = GmailClient(config)
    messages = client.get_emails({"in": "inbox"})
"""

import os
from datetime import datetime
from functools import wraps
from typing import Callable, Any

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource

from email_clients.email_client_interface import EmailClientInterface
from exceptions.error import AuthenticationError, ConfigError
from logger import get_logger
from utils.encoders import decode_base64
from utils.parsers import (
    parse_address_field,
    parse_multiple_address_field,
)

logger = get_logger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
]
EMAIL_FETCH_LIMIT = 50
MESSAGE_STATUS_LABELS = ["SENT", "STARRED", "UNREAD", "IMPORTANT"]


def require_auth(func: Callable) -> Callable:
    """
    Decorator to ensure authentication before method execution.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:
        self.validate_authentication()
        return func(self, *args, **kwargs)

    return wrapper


class GmailClient(EmailClientInterface):
    """
    Client for interacting with Gmail API.

    This class handles:
    - OAuth2 authentication flow
    - Token management and refresh
    - Message retrieval and parsing
    - Batch operations for efficiency

    Attributes:
        credentials_path (str): Path to OAuth2 credentials file
        token_path (str): Path to store/retrieve OAuth tokens
    """

    _token_path: str = None
    _credentials_path: str = None
    _service: Resource = None

    def __init__(self, config: dict):
        """
        Initialize the Gmail Client with the given configuration.

        Args:
            config (dict): Holds the path of credentials and token for the Gmail Client

        Raises:
            ValueError: If credentials and token path are not provided
            FileNotFoundError: If credentials file is not found
        """
        if not config.get("credentials_path") or not config.get("token_path"):
            raise ConfigError("Credentials and token path are required")

        if not os.path.exists(config.get("credentials_path")):
            raise ConfigError("Credentials file is not found")

        self._credentials_path = config.get("credentials_path")
        self._token_path = config.get("token_path")

    def authenticate(self, params=None) -> str:
        """
        Initiates the Authentication process for the User.

        Returns:
            Returns the user email address if authentication is successful
        """
        creds = None
        if os.path.exists(self._token_path):
            creds = Credentials.from_authorized_user_file(self._token_path, SCOPES)

        if not creds:
            creds = self._get_credentials()

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        with open(self._token_path, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

        self._service = build("gmail", "v1", credentials=creds)
        user = self._service.users().getProfile(userId="me").execute()

        return user.get("emailAddress")

    @require_auth
    def get_emails(self, batch_size: int, folder: str = None, query: dict = None):
        """
        Fetches the messages based on the query provided.

        Args:
            folder (str): Folder name to fetch the messages from
            batch_size (int): Number of messages to fetch in a single batch
            query (dict, optional): Query . Defaults to {"in": "inbox"}.

        Yields:
            list: List of messages
        """
        if query is None:
            query = {}

        if folder:
            query["in"] = folder.lower()

        try:
            all_messages = []
            query_string = self._build_query(query)

            current_messages, next_page_token = self._do_get_messages(
                query_string, batch_size
            )
            yield current_messages

            while next_page_token:
                logger.info("Next Page Token: %s", next_page_token)
                current_messages, next_page_token = self._do_get_messages(
                    query_string, batch_size, next_page_token
                )
                all_messages.extend(current_messages)
                logger.info(
                    "Total messages fetched: %d. Last message timestamp: %s",
                    len(all_messages),
                    all_messages[-1].get("timestamp"),
                )

                yield current_messages
        except Exception as error:
            logger.error("An error occurred while getting messages: %s", error)
            return []

    @require_auth
    def get_folders(self) -> list:
        """
        Fetches the list of folders in the user's Gmail account.

        Returns:
            list: List of folder names
        """
        results = (
            self._service.users()
            .labels()
            .list(
                userId="me",
            )
            .execute()
        )
        return [
            {key: label.get(key, "") for key in ("id", "name", "type")}
            for label in results.get("labels", [])
            if self._is_folder(label.get("name"))
        ]

    def validate_authentication(self) -> bool:
        """
        Helper function to check if the user is authenticated.

        Returns:
            bool: True if authenticated, False otherwise
        """
        if not os.path.exists(self._token_path):
            raise AuthenticationError("Email Authentication is not performed")

    def mark_as_read(self, message_id: str):
        """
        Marks the message as read.

        Args:
            message_id (str): Message ID to mark as read
        """
        self._service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"removeLabelIds": ["UNREAD"]},
        ).execute()

    def move_to_folder(self, message_id: str, folder: str):
        """
        Moves the message to the specified folder.

        Args:
            message_id (str): Message ID to mark as read
            current_folders (list): List of current folders
            folder (str): Folder name to move the message to
        """
        maessage = self._get_messages_details([message_id])
        current_folders = []
        if maessage and maessage[0]:
            current_folders = maessage[0].get("folders", [])

        self._service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"addLabelIds": [folder], "removeLabelIds": current_folders},
        ).execute()

    def _get_credentials(self) -> Credentials:
        """
        Initiates the OAuth2 flow to get the credentials.

        Returns:
            Credentials: A Credentials object with the required token.
        """
        flow = InstalledAppFlow.from_client_secrets_file(
            self._credentials_path,
            SCOPES,
        )
        creds = flow.run_local_server(port=0)
        return creds

    @require_auth
    def _do_get_messages(
        self,
        query: str,
        max_results: int,
        next_page_token=None,
    ):
        """
        Fetches the messages based on the query provided.

        Args:
            service (_type_): Gmail Service Object
            query (str): Query to filter the messages
            max_results (int): Maximum number of results to fetch
            next_page_token (str, optional): Next page token. Defaults to None.

        Returns:
            tuple: list of message details and next page token
        """
        logger.info(
            "Fetching messages with query: %s, pageToken: %s max_results: %s",
            query,
            next_page_token,
            max_results,
        )

        results = (
            self._service.users()
            .messages()
            .list(
                userId="me",
                q=query,
                maxResults=max_results,
                pageToken=next_page_token,
            )
            .execute()
        )
        messages = results.get("messages", [])
        message_ids = [message["id"] for message in messages]
        return self._get_messages_details(message_ids), results.get("nextPageToken")

    @require_auth
    def _get_messages_details(self, message_ids: list):
        """
        Pulls the message details for the given message ids.
        Uses the batch processing to fetch the details for multiple messages.

        Args:
            message_ids (list): Message IDs to fetch the details for

        Returns:
            list: List of message details
        """
        try:
            results = []

            def callback(request_id, response, exception):
                if exception:
                    logger.error(
                        "Error in batch request for %s: %s", request_id, exception
                    )
                else:
                    results.append(self._parse_message(response))

            batch = self._service.new_batch_http_request(callback=callback)
            for message_id in message_ids:
                batch.add(
                    self._service.users()
                    .messages()
                    .get(userId="me", id=message_id, format="full")
                )

            batch.execute()
            return results
        except Exception as error:
            logger.error("An error occurred during batch processing: %s", error)
            return []

    def _parse_message(self, message):
        """
        Parses the message and extracts the required details.

        Args:
            message: Message object

        Returns:
            dict: Extracted message details containitng subject, from, timestamp, body, to and cc
        """
        payload = message.get("payload", {})
        headers = payload.get("headers", [])
        body, attachments = self._parse_body(payload)
        message_details = {}
        allowed_message_details = ["subject", "from", "cc", "to", "date"]
        for header in headers:
            if header["name"].lower() in allowed_message_details:
                message_details[header["name"].lower()] = header["value"]

        timestamp = int(message.get("internalDate", 0))
        logger.info("Message Details: %s", message_details)

        return {
            "subject": message_details.get("subject", ""),
            "from": parse_address_field(message_details.get("from")),
            "received_timestamp": timestamp,
            "body": body,
            "to": parse_multiple_address_field(message_details.get("to", "")),
            "cc": parse_multiple_address_field(message_details.get("cc", "")),
            "id": message.get("id", None),
            "folders": [
                label for label in message.get("labelIds", []) if self._is_folder(label)
            ],
            "attachments": attachments,
        }

    def _parse_body(self, payload) -> str:
        """
        Helper function to extract the message body string.

        Args:
            payload (dict): Message Body Payload

        Returns:
            str: Extracted message body
        """
        body = ""
        attachments = []
        try:
            if payload.get("body", {}).get("data"):
                body = decode_base64(payload.get("body").get("data"))

            if payload.get("parts"):
                body, plain_body, attachments = self._parse_part(payload.get("parts"))

            return body, attachments
        except Exception as error:
            logger.error("An error occurred while extracting the body: %s", error)
            raise error

    def _parse_part(self, parts: dict | list) -> tuple:
        """
        Parse the message part and return the body and attachments.

        Args:
            part (dict): _description_

        Returns:
            tupe: _description_
        """
        body = ""
        plain_body = ""
        attachments = []

        if isinstance(parts, list):
            for part in parts:
                current_body, current_plain_body, current_attachments = (
                    self._parse_part(part)
                )
                attachments.extend(current_attachments)
                body = current_body if current_body else body
                plain_body = current_plain_body if current_plain_body else plain_body

        elif isinstance(parts, dict) and parts.get("parts"):
            body, plain_body, attachments = self._parse_part(parts.get("parts"))
        elif isinstance(parts, dict):
            if not parts.get("filename") == "":
                attachments.append(
                    {
                        "filename": parts.get("filename", ""),
                        "mime_type": parts.get("mimeType", ""),
                    }
                )

            if parts.get("mimeType") == "text/html" and parts.get("body", {}).get(
                "data"
            ):
                body = decode_base64(parts["body"]["data"])

            if parts.get("mimeType") == "text/plan" and parts.get("body", {}).get(
                "data"
            ):
                plain_body = decode_base64(parts["body"]["data"])

        return body, plain_body, attachments

    def _build_query(self, query: dict) -> str:
        """
        Helper function to build the query string based on the provided dictionary.

        Args:
            query (dict): Query dictionary containing the key-value pairs
        """
        supported_keys = ["from", "to", "subject", "in", "before", "after", "in"]
        supported_keys_query = {
            key: value for key, value in query.items() if key in supported_keys
        }

        date_query_fields = ["before", "after", "-before", "-after"]
        for field in date_query_fields:
            if not query.get(field):
                continue

            if not isinstance(query.get(field), datetime):
                raise ValueError(f"{field} should be a datetime object")

            supported_keys_query[field] = int(round(query.get(field).timestamp()))

        return " ".join(
            [f"{key}:{value}" for key, value in supported_keys_query.items()]
        )

    def _is_folder(self, label: str) -> str:
        """
        Helper function to filter the labels and get the folder name.

        Args:
            labels (str): Label name

        Returns:
            boolean: True if the label is a folder, False otherwise
        """
        return label not in MESSAGE_STATUS_LABELS and not label.startswith("CATEGORY_")

    def __del__(self):
        """
        Destructor to remove the token file if it exists
        """
        if os.path.exists(self._token_path):
            # os.remove(self._token_path)
            pass
