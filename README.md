# Email Auto Operations

Python-based CLI script to manage your inbox based on a defined set of rules.

## Setup

1. **Clone the repository:**
  ```sh
  git clone https://github.com/vigneshraja-sakthivel/email-auto-operations.git
  cd email-auto-operations
  ```

2. **Create a virtual environment and activate it:**
  ```sh
  python3 -m venv venv
  source venv/bin/activate
  ```

3. **Install the required dependencies:**
  ```sh
  pip install --upgrade pip
  pip install -r requirements.txt
  ```

4. **Configure Google OAuth2.** See [Configure Google OAuth2 Application](#configure-google-oauth2-application) for details.

5.

6. **Configure the .env file.** Copy the `.env.sample` and update the requried environment values

## Application Execution

### Fetching Emails

Use the following command to pull the emails:
```sh
python src/index.py fetch
```

Optionally, specify a folder name:
```sh
python src/index.py fetch --folder <folder_name>
```

### Apply Workflows

Define the workflow in a JSON file. Sample workflows can be found in the `sample_rules` folder.

Execute the following command to run the workflow:
```sh
python src/index.py workflow-processor --workflow-file-path <workflow_file_path>
```

## Configure Google OAuth2 Application

To access Gmail APIs, follow these steps:

1. Enable Gmail APIs in the Google Cloud Console.
2. Configure the OAuth Consent Form at [Google Cloud Console](https://console.cloud.google.com/apis/credentials/consent?hl=en).
3. Create an OAuth 2.0 Client ID at [Google Cloud Console](https://console.cloud.google.com/apis/credentials?hl=en).
4. Download the client secrets file and place it at `credentials/client_secrets.json`.

### Note:
* Select "External" for User Type when configuring the OAuth Consent Form.
* Add test users for testing the implementation.
* Enable the scope: `https://www.googleapis.com/auth/gmail.readonly`.

### References:
* [Google Cloud Support](https://support.google.com/cloud/answer/6158849?hl=en)
* [Gmail API Authentication](https://developers.google.com/gmail/api/auth/web-server)

## Contributing
If you wish to contribute, please follow these guidelines:

### Running Test Cases
To run the test cases using pytest, execute the following command:
```sh
pytest tests/
```

### Setting Up Pre-commit Hooks
To set up the pre-commit hooks, use the following command:
```sh
pre-commit install
```
