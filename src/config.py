"""
Utility module for encoding and decoding data.

This module provides functions to handle various encoding/decoding operations:
- Base64 decoding for Gmail API responses
- URL-safe base64 decoding
- UTF-8 string conversion

Functions:
    decode_base64: Decodes base64 encoded strings to UTF-8 text
"""

import os

APP_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
CREDENTIALS_DIRECTOR = f"{APP_PATH}/credentials"
TMP_DIRECTORY = f"{APP_PATH}/temp"
GMAIL_CONFIGURATIONS = {
    "credentials_path": f"{CREDENTIALS_DIRECTOR}/google_credentials.json",
    "token_path": f"{TMP_DIRECTORY}/gmail_token.json",
}
