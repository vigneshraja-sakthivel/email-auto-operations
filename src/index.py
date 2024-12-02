import argparse
from logger import get_logger


logger = get_logger(__name__)


def _add_email_argument(parser: argparse.ArgumentParser):
    """
    Adds an email argument to the given parser.

    This function configures the parser to accept an email address as input. The
    email argument is marked as required and expects a valid string.

    Args:
        parser (argparse.ArgumentParser): The argument parser to which the email
                                          argument will be added.
    """
    parser.add_argument(
        "--email", type=str, required=True, help="Specify an email address"
    )


def main():
    """
    Main function to parse the command line arguments and trigger the respective parser
    """
    parser = argparse.ArgumentParser(
        description="CLI Utlity to process the email messages based on the defined set of rules"
    )
    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Command to be executed"
    )

    fetch_email_process_parser = subparsers.add_parser(
        "fetch", help="Pulls the email messages for the given email address"
    )
    apply_rules_process_parser = subparsers.add_parser(
        "apply-rules", help="Pulls the email messages for the given email address"
    )
    _add_email_argument(fetch_email_process_parser)
    _add_email_argument(apply_rules_process_parser)

    # Parse the arguments
    parser.parse_args()
    logger.info("Arguments parsed successfully. Implement the logic here.")


if __name__ == "__main__":
    main()
