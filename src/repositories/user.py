"""
This module contains the UserRepository class which handles operations related to
user data in the database.
"""

from repositories.base import BaseRepository


class UserRepository(BaseRepository):
    """
    UserRepository class handles operations related to user data in the database.
    """

    def upsert_user(self, email_address: str) -> int:
        """
        Inserts a new user with the given email address if it does not already exist,
        and returns the user's ID.
        Args:
            email_address (str): The email address of the user to upsert.
        Returns:
            int: The ID of the upserted or existing user.
        """

        db_client = self._get_db_client()
        user_record_object = {
            "email_address": email_address,
        }
        count = db_client.count("users", {"email_address": email_address})

        if count == 0:
            db_client.insert("users", user_record_object)
            db_client.commit_transaction()

        user = db_client.fetch_one("users", {"email_address": email_address})
        return user["id"]
