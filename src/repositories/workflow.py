"""
This module contains the WorfklowRepository class which handles operations related to
workflow data in the database.
"""

import json
from datetime import datetime
from repositories.base import BaseRepository
from utils.encoders import hash


class WorfklowRepository(BaseRepository):
    """
    UserRepository class handles operations related to user data in the database.
    """

    def add_workflow_run(self, workflow: dict) -> int:
        """
        Inserts a new user with the given email address if it does not already exist,
        and returns the user's ID.
        Args:
            email_address (str): The email address of the user to upsert.
        Returns:
            int: The ID of the upserted or existing user.
        """

        content = json.dumps(workflow)
        content_hash = hash(content)
        workflow = self._get_db_client().fetch_one("workflow", {"hash": content_hash})
        workflow_id = workflow.get("id") if workflow else None

        if not workflow_id:
            workflow_id = self._get_db_client().insert(
                "workflow", {"hash": content_hash, "content": content}
            )

        run_id = self._get_db_client().insert(
            "workflow_run", {"workflow_id": workflow_id, "status": "yet_to_start"}
        )
        self._get_db_client().commit_transaction()
        return workflow_id, run_id

    def mark_workflow_run_as_started(self, run_id: int) -> None:
        """
        Marks a workflow run as started.
        Args:
            run_id (int): The ID of the workflow run to mark as completed.
        """
        self._get_db_client().update(
            "workflow_run",
            {"status": "running", "started_at": datetime.now()},
            {"id": run_id},
        )
        self._get_db_client().commit_transaction()

    def mark_workflow_run_as_completed(self, run_id: int, is_successful=True) -> None:
        """
        Marks a workflow run as completed.
        Args:
            run_id (int): The ID of the workflow run to mark as completed.
        """
        status = "completed" if is_successful else "failed"
        self._get_db_client().update(
            "workflow_run",
            {"status": status, "completed_at": datetime.now()},
            {"id": run_id},
        )
        self._get_db_client().commit_transaction()

    def add_workflow_run_log(
        self, run_id: int, email_id: str, action_type: str
    ) -> None:
        """
        Adds a log entry for a workflow run.
        Args:
            workflow_id (int): The ID of the workflow run.
            log (str): The log entry.
        """
        self._get_db_client().insert(
            "workflow_run_activity",
            {"run_id": run_id, "email_id": email_id, "action_type": action_type},
        )
        self._get_db_client().commit_transaction()
