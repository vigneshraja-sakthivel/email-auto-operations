import re


def extract_name_and_email_from_sender_string(sender):
    """
    Extracts the name and email from the sender string (e.g. Name <name@example.com>)
    If the sender string has only an email address, it returns None for the name.
    If the sender string has only a name, it returns None for the email.

    Args:
      sender (str): Sender string in the format "Name <name@example.com>"

    Returns:
      tuple: A tuple containing the name (str) and email (str). If the sender string
      is not in the correct format, returns (None, None).
    """
    match = re.match(r"(.*)<(.*)>", sender)
    if match:
        name = match.group(1).strip() or None
        email = match.group(2).strip()
        return name, email
    if "@" in sender:
        return None, sender.strip()

    return sender, None
