"""
This module contains the FolderRepository class, which provides methods to interact
with the folders in the database.
"""

from repositories.base import BaseRepository


class FolderRepository(BaseRepository):
    """
    Repository class for handling folder operations in the database.
    """

    def upsert_folder(self, user_id: int, folder: dict):
        """
        Inserts or updates a folder record in the database for a given user.
        If a folder with the same provider ID or name already exists, it updates the existing
        record. Otherwise, it inserts a new record.
        Args:
            user_id (int): The ID of the user to whom the folder belongs.
            folder (dict): A dictionary containing folder details with keys "id",
            "name", and "type".
        Returns:
            None
        """

        db_client = self._get_db_client()
        folder_record_object = {
            "provider_id": folder["id"],
            "name": folder["name"],
            "type": folder["type"],
            "user_id": user_id,
        }
        update_clause = None
        count = db_client.count("folders", {"provider_id": folder["id"]})
        if count != 0:
            update_clause = {"provider_id": folder["id"]}
        else:
            count = db_client.count("folders", {"name": folder["name"]})
            if count != 0:
                update_clause = {"name": folder["name"]}

        if update_clause:
            db_client.update("folders", folder_record_object, update_clause)
        else:
            db_client.insert("folders", folder_record_object)
        db_client.commit_transaction()

    def get_all_folders(self, user_id: int) -> list:
        """
        Retrieve all folders for a given user.
        Args:
            user_id (int): The ID of the user whose folders are to be retrieved.
        Returns:
            list: A list of folders associated with the specified user.
        """

        return self._get_db_client().fetch("folders", {"user_id": user_id})
