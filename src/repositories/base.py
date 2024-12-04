"""
This module defines the BaseRepository class which serves as an abstract base class
for repository implementations.
"""

from abc import ABC
from db.db_client import DbClient
from config import DB_CONFIGURATIONS


class BaseRepository(ABC):
    """
    A base repository class that implements the Singleton pattern to ensure
    only one instance of the class is created.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _get_db_client(self) -> DbClient:
        return DbClient(DB_CONFIGURATIONS)
