"""
This module provides utility functions for parsing email addresses and extracting plain text
from HTML content.

Functions:
  parse_address_field(address: str) -> dict:
    Extracts the name and email from a single address field.

  parse_multiple_address_field(addresses: str) -> list:
    Extracts the name and email from multiple address fields.

  extract_plain_text_from_html(html_content: str) -> str:
"""

import re
import json
import os
from bs4 import BeautifulSoup


def parse_address_field(address: str) -> dict:
    """
    Extracts the name and email from the address field (e.g. Name <name@example.com>)
    If the address string has only an email address, it returns None for the name.
    If the address string has only a name, it returns None for the email.

    Args:
      address (str): Address string in the format "Name <name@example.com>"

    Returns:
      dict: A dict with the name (str) and email (str).
    """
    address = address.strip()
    name = None
    email = None

    match = re.match(r"(.*?)\s*<([^>]+)>", address.strip())
    if match:
        name = match.group(1).strip() if match.group(1) else None
        email = match.group(2).strip()
    elif re.match(r"<([^>]+)>", address.strip()):
        email = re.search(r"<([^>]+)>", address.strip()).group(1).strip()
    elif re.match(r"^[^@\s<>]+@[^@\s<>]+\.[^@\s<>]+$", address.strip()):
        email = address.strip()
    else:
        name = address.strip()

    return {
        "name": name,
        "email": email,
    }


def parse_multiple_address_field(addresses: str) -> list:
    """
    Extracts the name and email from the address field having multiple addresses
    (e.g. Abc<abc@example.com, XYZ<xyz@example.com>).
    If the address string has only an email address, it returns None for the name.
    If the address string has only a name, it returns None for the email.

    Args:
      addresses (str): Addresses string in the format "Name <name@example.com>"

    Returns:
      list: A list of dict with the name (str) and email (str).
    """
    if not addresses:
        return []
    all_addresses = addresses.split(",")
    return [parse_address_field(address) for address in all_addresses]


def extract_plain_text_from_html(html_content):
    """
    Extracts plain text from the HTML content using BeautifulSoup.

    Args:
      html_content (str): HTML content

    Returns:
      str: Plain text extracted from the HTML content.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text()


def parse_json_file(file_path: str) -> dict | list:
    """
    Parses a JSON file and returns the data in the json file.
    Args:
        rule_file (str): The path to the rule file to be parsed.
    Returns:
        list: A list of rules parsed from the JSON file.
    Raises:
        FileNotFoundError: If the rule file does not exist.
        ValueError: If there is an error parsing the JSON from the rule file.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Rule file {file_path} not found.")

    with open(file_path, "r") as file:
        try:
            rules = json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON from rule file {file_path}: {e}")

    return rules
