from utils.encoders import decode_base64


def test_decode_base64():
    """
    Test cases for the decode_base64 function.
    """
    assert decode_base64("SGVsbG8gd29ybGQ=") == "Hello world"

    # Test with base64 encoded string with special characters
    assert (
        decode_base64("U3BlY2lhbCBjaGFyYWN0ZXJzOihQCMkJV4mKigp")
        == "Special characters: !@#$%^&*()"
    )
