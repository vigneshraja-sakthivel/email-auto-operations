"""
This module contains the EmailRepository class, which is responsible for performing
CRUD operations related to emails in the database. It includes methods for upserting
emails, email recipients, folder-email associations, and email attachments.
"""

from datetime import datetime, timezone
from repositories.base import BaseRepository


class EmailRepository(BaseRepository):
    """
    Repository class for handling email-related database operations.
    """

    def upsert_email(self, user_id: int, email: str, folder_ids: list):
        """
        Inserts or updates an email record in the database and handles related operations.
        Args:
            user_id (int): The ID of the user to whom the email belongs.
            email (str): The email data containing subject, body, sender, recipients, etc.
            folder_ids (list): A list of folder IDs where the email should be stored.
        Returns:
            None
        """

        email_record_object = {
            "subject": email.get("subject", ""),
            "provider_id": email.get("id", None),
            "body": email.get("body", ""),
            "received_timestamp": datetime.fromtimestamp(
                email.get("received_timestamp") / 1000, tz=timezone.utc
            ),
            "sender_name": email.get("from", {}).get("name"),
            "sender_email_address": email.get("from", {}).get("email"),
            "user_id": user_id,
        }

        self._get_db_client().insert("emails", email_record_object)
        email_record = self._get_db_client().fetch_one(
            "emails", {"provider_id": email["id"]}
        )
        for to_address in email.get("to", []):
            self._upsert_email_recipient(email_record.get("id"), to_address, "to")

        for cc_address in email.get("cc", []):
            self._upsert_email_recipient(email_record.get("id"), cc_address, "cc")

        for folder_id in folder_ids:
            self._upsert_folder_email(email_record.get("id"), folder_id)

        for attachment in email.get("attachments", []):
            self._upsert_attachment_details(
                email_record.get("id"),
                attachment.get("filename"),
                attachment.get("mime_type"),
            )

        self._get_db_client().commit_transaction()

    def _upsert_email_recipient(
        self, email_id: str, address: dict, recipient_type: str
    ):
        self._get_db_client().insert(
            "email_recipients",
            {
                "email_id": email_id,
                "email_address": address.get("email"),
                "type": recipient_type,
                "name": address.get("name"),
            },
        )

    def _upsert_folder_email(self, email_id: int, folder_id: int):
        self._get_db_client().insert(
            "email_folders",
            {
                "folder_id": folder_id,
                "email_id": email_id,
            },
        )

    def _upsert_attachment_details(self, email_id: int, name: str, mime_type: str):
        self._get_db_client().insert(
            "email_attachments",
            {
                "name": name,
                "mime_type": mime_type,
                "email_id": email_id,
            },
        )
