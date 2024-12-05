"""
This module contains the EmailFetcher class, which is responsible for fetching emails
from an email client and storing them in the database. It implements the
CommandProcessorInterface and uses various repositories to manage users, folders,
and emails in the database.

Classes:
    EmailFetcher: Fetches emails from the email client and stores them in the database.
"""

import traceback

from jsonschema import validate, ValidationError

from config import WORKFLOW_VALIDATION_SCHEMA
from command_processor.command_processor_interface import CommandProcessorInterface
from email_clients.email_client_interface import EmailClientInterface
from logger import get_logger
from repositories.email import EmailRepository
from repositories.user import UserRepository
from repositories.workflow import WorfklowRepository
from utils.parsers import parse_json_file


PROCESSING_BATCH_SIZE = 50
logger = get_logger(__name__)


class WorkflowProcessor(CommandProcessorInterface):
    """
    WorkflowProcessor is responsible for applying the action based on the rules provided.
    """

    _email_client: EmailClientInterface = None

    def __init__(
        self,
        email_client: EmailClientInterface,
    ):
        self._email_client = email_client

    def execute(self, params: dict = None):
        """
        Fetch emails from the email client and store them in the database.
        """
        try:
            if not params.get("workflow_file_path"):
                raise ValueError("Workflow file path is required.")

            self._process_rules(params.get("workflow_file_path"))

            logger.info("Workflow processed successfully.")
        except Exception as e:
            logger.error(
                f"Error occurred while processing the workflow: %s. Error Trace: %s",
                e,
                traceback.print_exc(),
            )

    def _persis_workflow(self, workflow: dict) -> tuple:
        """
        Persists the workflow in the database.
        """
        workflow_repository = WorfklowRepository()
        workflow_id, run_id = workflow_repository.add_workflow_run(workflow)
        return workflow_id, run_id

    def _mark_workflow_as_started(self, run_id: int) -> None:
        """
        Marks a workflow as started.
        Args:
            run_id (int): The ID of the workflow run to mark as started.
        """
        workflow_repository = WorfklowRepository()
        workflow_repository.mark_workflow_run_as_started(run_id)

    def _mark_workflow_as_completed(self, run_id: int, is_successful=True) -> None:
        """
        Marks a workflow as completed.
        Args:
            run_id (int): The ID of the workflow run to mark as completed.
        """
        workflow_repository = WorfklowRepository()
        workflow_repository.mark_workflow_run_as_completed(run_id, is_successful)

    def _add_workflow_run_log(
        self, run_id: int, email_id: int, action_type: str
    ) -> int:
        """
        Adds a log entry for a workflow run.
        Args:
            run_id (int): The ID of the workflow run.
            email_id (int): The ID of the email.
            action_type (str): The action type.
        """
        workflow_repository = WorfklowRepository()
        workflow_repository.add_workflow_run_log(run_id, email_id, action_type)

    def _process_rules(self, workflow_file_path: str) -> int:
        workflow = parse_json_file(workflow_file_path)
        self._validate_rules(workflow)
        user_repository = UserRepository()
        user_email_address = self._email_client.authenticate()
        user = user_repository.get_user_by_email(user_email_address)
        if not user:
            raise ValueError(
                "User is not found. First attempt to fetch emails using the fetch command."
            )
        workflow_id, run_id = self._persis_workflow(workflow)
        try:
            self._mark_workflow_as_started(workflow_id)
            self._apply_rule(workflow, run_id, user.get("id"))
            self._mark_workflow_as_completed(workflow_id)
        except Exception as e:
            self._mark_workflow_as_completed(workflow_id, is_successful=False)
            raise e

    def _apply_rule(self, workflow: dict, run_id: int, user_id: int) -> None:
        """
        Fetch the email matching the rules and apply the action.

        Args:
            workflow (dict): Workflow Definition
            user_id (int): User ID
        """

        email_repository = EmailRepository()
        last_processed_email_id = None
        matching_emails = email_repository.get_emails_by_applying_rules(
            workflow, user_id, None, PROCESSING_BATCH_SIZE
        )

        while matching_emails:
            logger.info(
                f"Found %s emails matching the rules during run (%s).",
                len(matching_emails),
                run_id,
            )
            for email in matching_emails:
                last_processed_email_id = email.get("id")
                self._apply_action(
                    workflow, run_id, email.get("id"), email.get("provider_id")
                )

            matching_emails = email_repository.get_emails_by_applying_rules(
                workflow, user_id, last_processed_email_id, PROCESSING_BATCH_SIZE
            )

    def _apply_action(
        self, workflow: dict, run_id: int, email_id: int, provider_id: int
    ) -> None:
        """
        Apply the action on the email.

        Args:
            workflow (dict): Workflow Definition
            email_id (int): Email ID
            provider_id (str): ID of the email provider
            run_id (int): Workflow Run ID
        """
        try:
            logger.info(
                f"Applying action on the email (%s) during run (%s).",
                email_id,
                run_id,
            )

            email_action = workflow.get("action")
            if email_action == "mark_read":
                self._email_client.mark_as_read(provider_id)
            elif email_action == "move":
                self._email_client.move_to_folder(
                    provider_id, workflow.get("action_target")
                )

            self._add_workflow_run_log(run_id, email_id, email_action)
            logger.info(
                f"Applied action on the email (%s) during run (%s).",
                email_id,
                run_id,
            )
        except Exception as e:
            logger.error(
                f"Error occurred while applying action on the email (%s) during run (%s): %s.",
                email_id,
                run_id,
                e,
            )

    def _validate_rules(self, workflow: dict) -> bool:
        """
        Validate the rules provided by the user.
        """
        workflow_rules_validation_schema = parse_json_file(WORKFLOW_VALIDATION_SCHEMA)
        validate(instance=workflow, schema=workflow_rules_validation_schema)
