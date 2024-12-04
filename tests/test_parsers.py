from utils.parsers import parse_address_field


def test_extract_name_and_email_from_sender_string():
    """
    Test cases for the extract_name_and_email_from_sender_string function.
    """
    # Test with name and email
    assert parse_address_field("John Doe <john.doe@example.com>") == {
        "name": "John Doe",
        "email": "john.doe@example.com",
    }

    # Test with only email
    assert parse_address_field("<john.doe@example.com>") == {
        "name": None,
        "email": "john.doe@example.com",
    }

    # Test with only name
    assert parse_address_field("John Doe") == {"name": "John Doe", "email": None}

    # Test with empty string
    assert parse_address_field("") == {"name": "", "email": None}

    # Test with extra spaces
    assert parse_address_field("  John Doe  <  john.doe@example.com  >  ") == {
        "name": "John Doe",
        "email": "john.doe@example.com",
    }

    # Test with no name and malformed email
    assert parse_address_field("<john.doe@example.com>") == {
        "name": None,
        "email": "john.doe@example.com",
    }

    # Test with only email
    assert parse_address_field("john.doe@example.com") == {
        "name": None,
        "email": "john.doe@example.com",
    }

    # Test with only email having special characters
    assert parse_address_field("john-doe=@example.com") == {
        "name": None,
        "email": "john-doe=@example.com",
    }
