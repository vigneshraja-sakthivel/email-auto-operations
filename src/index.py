import argparse
import os

from config import DB_CONFIGURATIONS, GMAIL_CONFIGURATIONS, TMP_DIRECTORY
from command_processor.command_processor_interface import CommandProcessorInterface
from command_processor.email_fetcher import EmailFetcher
from command_processor.workflow_processor import WorkflowProcessor
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


def _get_processor_and_arguments(command_details) -> CommandProcessorInterface:
    """
    Returns the processor based on the configuration
    """
    if command_details.command == "fetch":
        return EmailFetcher(_get_email_client()), {
            "folder": command_details.folder,
        }
    if command_details.command == "workflow-processor":
        return WorkflowProcessor(_get_email_client()), {
            "workflow_file_path": command_details.workflow_file_path,
        }


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

    email_fetcher = subparsers.add_parser(
        "fetch", help="Pulls the email messages for the given email address"
    )

    email_fetcher.add_argument(
        "--folder",
        type=str,
        required=False,
        help="Specify the folder name to fetch the emails",
    )

    workflow_process_parser = subparsers.add_parser(
        "workflow-processor",
        help="Pulls the email messages for the given email address",
    )

    workflow_process_parser.add_argument(
        "--workflow-file-path",
        type=str,
        required=True,
        help="Specify the path of the workflow rule file",
    )

    # Parse the arguments
    command_details = parser.parse_args()
    logger.info("Arguments parsed successfully. Implement the logic here.")
    logger.info("Initializing the application")
    _init_app()
    logger.info("Initialied the application successfully")
    processor, arguments = _get_processor_and_arguments(command_details)
    print(arguments)
    processor.execute(arguments)


if __name__ == "__main__":
    main()
