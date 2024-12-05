# Developer Notes

## Fetching Emails

1. **Authorization**: Gmail API is used for user authorization.
2. **OAuth2**: Server-side OAuth2 is implemented. The script opens a browser for the user to provide access.
3. **Credential Validation**: User credentials are validated.
4. **Email Fetching**:
   - Email list is pulled, returning a list of `threadId` and `messageId`.
   - Email details are fetched using the Get Message API.
5. **Body Processing**: Email body is converted to plain text using `bs4` and stored in a separate field to support future workflow rules.
6. **Stored Email Data**: The following details are saved in the database:
   - Message ID
   - Body
   - Plain Text Body
   - Subject
   - From
   - To
   - CC
   - Attachments
   - Received Date and Time.

### Performance Consideration
- Batch requests are utilized to fetch email details efficiently ([Batch Requests Guide](https://developers.google.com/gmail/api/guides/batch)).

---

## Workflow Processing

1. **JSON Validation**: Workflow JSON is validated using JSON Schema.
2. **SQL Querying**: SQL queries are built to fetch emails matching the rules.
3. **Workflow Storage**:
   - Since workflows are not persisted in the database, they are stored as JSON for future reference.
   - Workflow uniqueness is determined using a hash of the workflow file content.
4. **Run and Action Logging**: Workflow runs and actions taken are recorded in the database for future reference.

### Performance Consideration
- `tsvector` and `tsquery` are used for subject field search. This can be extended to the body field in the future.

---

## Library Usage

- **Code Formatting & Linting**: `black`, `pre_commit`, `pylint`.
- **Testing**: `pytest`.
- **API Client**: `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`.
- **Database**: `psycopg2-binary`.
- **Utilities**: `bs4`, `jsonschema`.

---

## Folder Structure

- **`credentials`**: Stores Google OAuth2 Client credentials.
- **`docs`**:
  - `NOTES.md`: Development notes.
- **`sample_rules`**: Contains sample rules for testing.
- **`src`**:
  - `command_processor`: Python classes for command implementations.
  - `db`: Database client/connection manager.
  - `email_clients`: Python classes for supported email providers.
  - `exception`: Custom error implementations.
  - `repositories`: Repository classes for database queries.
  - `utils`: Utility methods.
  - `config.py`: Configuration settings.
  - `index.py`: Entry point.
  - `logger.py`: Logger creation and management.
- **`env.sample`**: Sample `.env` file for environment variables.
- **`.pre-commit-config.yaml`**: Pre-commit hook validation rules.
- **`.pylintrc`**: Pylint validation rules.
- **`schema.sql`**: Database schema definition.

## KNOWN ISSUES
1. **Retry Mechanism**: Needs to be implemented to handle transient failures and ensure robustness.
2. **Magic Constants**: Replace hardcoded values with descriptive constants for better readability and maintainability.
3. **Batch Processing**: Consider implementing batch operations when applying actions to improve efficiency and reduce API calls.
4. **Database Update**: The email entity in the database is not updated after performing actions, causing potential inconsistencies.
5. **Folder Validation**: Validate folder inputs in command arguments and workflow rules to ensure correctness.
6. **Testing**: Unit tests and integration tests are required to validate functionality and ensure system reliability.
7. **Email Filtering**: Improve the filtering mechanism to exclude already pulled emails more efficiently.
8. **Configuring `setup.py`**:
   - A `setup.py` file should be properly configured to package the project for distribution.
   - This includes defining metadata like project name, version, description, author details, dependencies, and entry points for the scripts.
   - Configuring `setup.py` ensures the application can be installed and used across environments with ease using `pip install`.

9. **Making the Scripts Standalone**:
   - Refactor scripts to work as standalone executables by defining appropriate entry points in `setup.py`.
   - Use tools like `console_scripts` in the `entry_points` section to create command-line executable scripts.
   - This ensures that users can run the scripts without explicitly invoking Python, enhancing usability.
   - Example: After installation, a command like `email-auto-fetch` could be directly used instead of `python src/index.py fetch`.
