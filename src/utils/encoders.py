"""
Utility module for encoding and decoding data.
"""

import base64
import hashlib


def decode_base64(data: str) -> str:
    """
    Decode base64 encoded data.

    Args:
        data (string): Encoded String to be decoded
    Returns:
        _type_: Decoded String
    """

    return base64.urlsafe_b64decode(data).decode("utf-8")


def hash(data: str) -> str:
    """
    Hash the data using base64 encoding.

    Args:
        data (string): String to be hashed
    Returns:
        str: Hashed String
    """
    hash_object = hashlib.sha256(data.encode("utf-8"))
    hashed_data = base64.urlsafe_b64encode(hash_object.digest()).decode("utf-8")
    return hashed_data
