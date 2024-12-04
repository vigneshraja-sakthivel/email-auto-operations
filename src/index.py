import argparse
import os

from config import DB_CONFIGURATIONS, GMAIL_CONFIGURATIONS, TMP_DIRECTORY
from command_processor.email_fetcher import EmailFetcher
from command_processor.command_processor_interface import CommandProcessorInterface
from db.db_client import DbClient
from email_clients.email_client_interface import EmailClientInterface
from email_clients.gmail.gmail_client import GmailClient
from logger import get_logger


logger = get_logger(__name__)


def _get_email_client() -> EmailClientInterface:
    """
    Returns the email client based on the configuration
    """
    return GmailClient(GMAIL_CONFIGURATIONS)


def _get_db_client() -> DbClient:
    """
    Returns the db client based on the configuration
    """
    return DbClient(DB_CONFIGURATIONS)


def _get_processor() -> CommandProcessorInterface:
    """
    Returns the processor based on the configuration
    """
    return EmailFetcher(_get_email_client(), _get_db_client())


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


def _init_app():
    """
    Initializes the application by creating the required directories
    """
    for directory in [TMP_DIRECTORY]:
        if not os.path.exists(directory):
            os.makedirs(directory)

    logger.info("Application initialized successfully")


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
    logger.info("Initializing the application")
    _init_app()
    logger.info("Initialied the application successfully")
    _get_processor().execute()


if __name__ == "__main__":
    main()
