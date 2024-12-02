"""
Utility module for encoding and decoding data.
"""

import base64


def decode_base64(data: str) -> str:
    """
    Decode base64 encoded data.

    Args:
        data (string): Encoded String to be decoded
    Returns:
        _type_: Decoded String
    """

    return base64.urlsafe_b64decode(data).decode("utf-8")
