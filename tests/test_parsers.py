from utils.parsers import extract_name_and_email_from_sender_string


def test_extract_name_and_email_from_sender_string():
    """
    Test cases for the extract_name_and_email_from_sender_string function.
    """
    # Test with name and email
    assert extract_name_and_email_from_sender_string(
        "John Doe <john.doe@example.com>"
    ) == ("John Doe", "john.doe@example.com")

    # Test with only email
    assert extract_name_and_email_from_sender_string("john.doe@example.com") == (
        None,
        "john.doe@example.com",
    )

    # Test with only name
    assert extract_name_and_email_from_sender_string("John Doe") == ("John Doe", None)

    # Test with empty string
    assert extract_name_and_email_from_sender_string("") == ("", None)

    # Test with extra spaces
    assert extract_name_and_email_from_sender_string(
        "  John Doe  <  john.doe@example.com  >  "
    ) == ("John Doe", "john.doe@example.com")

    # Test with no name and malformed email
    assert extract_name_and_email_from_sender_string("<john.doe@example.com>") == (
        None,
        "john.doe@example.com",
    )
