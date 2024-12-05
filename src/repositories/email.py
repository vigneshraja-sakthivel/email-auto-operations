"""
This module contains the EmailRepository class, which is responsible for performing
CRUD operations related to emails in the database. It includes methods for upserting
emails, email recipients, folder-email associations, and email attachments.
"""

from datetime import datetime, timezone

from logger import get_logger
from repositories.base import BaseRepository

logger = get_logger(__name__)

FILTER_FIELDS_MAPPING = {
    "subject": {
        "type": "string",
        "field_name": "subject",
    },
    "from": {
        "type": "string",
        "field_name": "CONCAT(sender_email_address, ' ', sender_name)",
    },
    "to": {
        "type": "string",
        "field_name": "CONCAT(er.email_address, ' ', er.name)",
    },
    "date_received": {
        "type": "timestamp",
        "field_name": "received_timestamp",
    },
}

FULL_TEXT_SEARCH_FIELDS = ["subject"]

STRING_OPERATORS = {
    "equals": "{field_name} = '{value}'",
    "not_equals": "{field_name} != '{value}'",
    "contains_tsvechor": "to_tsvector('english', {field_name}) @@ plainto_tsquery('{value}')",
    "does_not_contains_tsvechor": (
        "NOT to_tsvector('english', {field_name}) @@ plainto_tsquery('{value}')"
    ),
    "contains": "{field_name} ILIKE '%{value}%'",
    "does_not_contains": "{field_name} NOT ILIKE '%{value}%'",
}

TIMESTAMP_OPERATORS = {
    "greater_than": "{field_name} > NOW() + interval '{value} {value_type}'",
    "less_than": "{field_name} < NOW() - interval '{value} {value_type}'",
}


class EmailRepository(BaseRepository):
    """
    Repository class for handling email-related database operations.
    """

    def upsert_email(self, user_id: int, email: str, folder_ids: list):
        """
        Inserts or updates an email record in the database and handles related operations.
        Args:
            user_id (int): The ID of the user to whom the email belongs.
            email (str): The email data containing subject, body, sender, recipients, etc.
            folder_ids (list): A list of folder IDs where the email should be stored.
        Returns:
            None
        """

        count = self._get_db_client().count(
            "emails",
            {
                "provider_id": email.get("id"),
                "user_id": user_id,
            },
        )

        if count > 0:
            return

        email_record_object = {
            "subject": email.get("subject", ""),
            "provider_id": email.get("id", None),
            "body": email.get("body", ""),
            "body_plain_text": email.get("body_plain_text", ""),
            "received_timestamp": datetime.fromtimestamp(
                email.get("received_timestamp") / 1000, tz=timezone.utc
            ),
            "sender_name": email.get("from", {}).get("name"),
            "sender_email_address": email.get("from", {}).get("email"),
            "user_id": user_id,
        }

        email_id = self._get_db_client().insert("emails", email_record_object)

        for to_address in email.get("to", []):
            self._upsert_email_recipient(email_id, to_address, "to")

        for cc_address in email.get("cc", []):
            self._upsert_email_recipient(email_id, cc_address, "cc")

        for folder_id in folder_ids:
            self._upsert_folder_email(email_id, folder_id)

        for attachment in email.get("attachments", []):
            self._upsert_attachment_details(
                email_id,
                attachment.get("filename"),
                attachment.get("mime_type"),
            )

        self._get_db_client().commit_transaction()

    def get_emails_by_applying_rules(
        self, workflow: dict, user_id: int, last_processed_id: int, batch_size: int
    ):
        """
        Retrieve emails by applying specified workflow rules.
        Args:
            workflow (dict): A dictionary containing the workflow rules to apply.
            user_id (int): The ID of the user for whom to retrieve emails.
            last_processed_id (int): The ID of the last processed email to continue from.
            batch_size (int): The number of emails to retrieve in this batch.
        Returns:
            list: A list of emails that match the specified workflow rules.
        """
        query = self._build_apply_filter_query(
            workflow, user_id, last_processed_id, batch_size
        )
        return self._get_db_client().query(query)

    def get_email_timestamp_extremes(self, user_id: int, folder: str = None):
        """
        Retrieve the timestamp of the latest email received by the user and the
        timestamp of the oldest email received by the user.
        Args:
            user_id (int): The ID of the user for whom to retrieve the email timestamps.

        Returns:
            tuple: The timestamps of the latest and oldest emails received by the user.
        """
        query = ""
        if not folder:
            query = f"""
                SELECT
                    MAX(received_timestamp) AS latest_email_timestamp,
                    MIN(received_timestamp) AS oldest_email_timestamp
                FROM emails
                WHERE user_id = {user_id}
            """
        else:
            query = f"""
                SELECT
                    MAX(received_timestamp) AS latest_email_timestamp,
                    MIN(received_timestamp) AS oldest_email_timestamp
                FROM emails e
                JOIN email_folders ef ON e.id = ef.email_id
                JOIN folders f ON ef.folder_id = f.id
                WHERE e.user_id = {user_id} AND LOWER(f.name) = LOWER('{folder}')
            """

        result = self._get_db_client().query(query)

        if result and result[0]:
            return (
                result[0]["latest_email_timestamp"],
                result[0]["oldest_email_timestamp"],
            )

        return None, None

    def _build_apply_filter_query(
        self, workflow: dict, user_id: int, last_processed_id: int, batch_size: int
    ):
        """
        Builds an SQL query to apply filters based on the provided workflow rules.
        Args:
            workflow (dict): A dictionary containing the workflow rules and conditions.
            user_id (int): The ID of the user for whom the query is being built.
            last_processed_id (int): The ID of the last processed email, used to filter
                out already processed emails.
            batch_size (int): The number of records to fetch in the query.
        Returns:
            str: The constructed SQL query string.
        """
        query = "SELECT emails.id, emails.provider_id FROM emails"
        condition_where_clause_conditions = []
        where_clause_concat_condition = (
            "AND" if workflow.get("condition", "all") == "all" else "OR"
        )

        default_where_clause_conditions = [f"emails.user_id = {user_id}"]
        if last_processed_id:
            default_where_clause_conditions.append(f"emails.id < {last_processed_id}")

        for rule in workflow.get("rules", []):
            field_name = FILTER_FIELDS_MAPPING[rule.get("field_name")]["field_name"]
            field_type = FILTER_FIELDS_MAPPING[rule.get("field_name")]["type"]
            predicate = rule.get("predicate")
            value = rule.get("value")
            value_type = rule.get("value_unit", None)

            if rule.get("field_name") == "to" and "email_recipients" not in query:
                query += " JOIN email_recipients er ON emails.id = er.email_id AND er.type = 'to'"

            if field_type == "string":
                if (
                    rule.get("field_name") in FULL_TEXT_SEARCH_FIELDS
                    and "contains" not in query
                ):
                    predicate = predicate + "_tsvechor"
                condition_where_clause_conditions.append(
                    self._apply_string_condition(field_name, predicate, value)
                )
            elif field_type == "timestamp":
                condition_where_clause_conditions.append(
                    self._apply_timestamp_condition(
                        field_name, predicate, value, value_type
                    )
                )

        default_where_clause = " AND ".join(default_where_clause_conditions)
        search_where_clause = (f" {where_clause_concat_condition} ").join(
            condition_where_clause_conditions
        )

        query += f" WHERE {default_where_clause} AND ({search_where_clause})"

        query += f" ORDER BY emails.id DESC LIMIT {batch_size}"
        logger.info("Filter query: %s", query)
        return query

    def _apply_string_condition(self, field_name, operator, value):
        """
        Apply a string condition to a field based on the specified operator and value.

        Args:
            field_name (str): The name of the field to which the condition is applied.
            operator (str): The operator to use for the condition. Must be one of the
            keys in STRING_OPERATORS.
            value (str): The value to compare the field against.

        Returns:
            str: A formatted string representing the condition.

        Raises:
            ValueError: If the operator is not supported.
        """

        if operator in STRING_OPERATORS:
            return STRING_OPERATORS[operator].format(field_name=field_name, value=value)

        raise ValueError(f"Unsupported operator: {operator}")

    def _apply_timestamp_condition(self, field_name, operator, value, value_type):
        """
        Apply a timestamp condition to a field based on the given operator and value.
        Args:
            field_name (str): The name of the field to apply the condition to.
            operator (str): The operator to use for the condition (e.g., '=', '>', '<').
            value (str): The value to compare the field against.
            value_type (str): The type of the value (e.g., 'timestamp', 'date').
        Returns:
            str: A formatted string representing the condition.
        Raises:
            ValueError: If the operator is not supported.
        """

        if operator in TIMESTAMP_OPERATORS:
            return TIMESTAMP_OPERATORS[operator].format(
                field_name=field_name, value=value, value_type=value_type
            )

        raise ValueError(f"Unsupported operator: {operator}")

    def _upsert_email_recipient(
        self, email_id: str, address: dict, recipient_type: str
    ):
        """
        Inserts or updates an email recipient in the database.
        Args:
            email_id (str): The unique identifier of the email.
            address (dict): A dictionary containing the recipient's email address and name.
            Example: {"email": "recipient@example.com", "name": "Recipient Name"}
            recipient_type (str): The type of recipient (e.g., "to", "cc", "bcc").
        Returns:
            None
        """
        self._get_db_client().insert(
            "email_recipients",
            {
                "email_id": email_id,
                "email_address": address.get("email"),
                "type": recipient_type,
                "name": address.get("name"),
            },
        )

    def _upsert_folder_email(self, email_id: int, folder_id: int):
        """
        Upserts an email into a folder in the database.
        If the email already exists in the folder, it will be updated.
        Otherwise, a new entry will be created.
        Args:
            email_id (int): The ID of the email to be upserted.
            folder_id (int): The ID of the folder where the email will be upserted.
        Returns:
            None
        """
        self._get_db_client().insert(
            "email_folders",
            {
                "folder_id": folder_id,
                "email_id": email_id,
            },
        )

    def _upsert_attachment_details(self, email_id: int, name: str, mime_type: str):
        """
        Inserts or updates the details of an email attachment in the database.
        Args:
            email_id (int): The ID of the email to which the attachment belongs.
            name (str): The name of the attachment.
            mime_type (str): The MIME type of the attachment.
        Returns:
            None
        """
        self._get_db_client().insert(
            "email_attachments",
            {
                "name": name,
                "mime_type": mime_type,
                "email_id": email_id,
            },
        )
