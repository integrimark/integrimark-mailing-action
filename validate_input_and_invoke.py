import os
import json
import subprocess
import sys


def validate_env_var(env_var_name):
    """
    Validates if an environment variable is set.
    Returns the value if set, None otherwise.
    """
    return os.environ.get(env_var_name)


def main():
    # Environment Variables
    sendgrid_api_key = validate_env_var("SENDGRID_API_KEY")
    service_account_json = validate_env_var("SERVICE_ACCOUNT_JSON")
    smtp_server = validate_env_var("SMTP_SERVER")
    smtp_port = validate_env_var("SMTP_PORT")
    smtp_username = validate_env_var("SMTP_USERNAME")
    smtp_password = validate_env_var("SMTP_PASSWORD")

    # GitHub Action Inputs
    from_email = os.getenv("INPUT_FROM_EMAIL")
    csv_input_file = os.getenv("INPUT_CSV_INPUT_FILE")
    google_spreadsheet_id = os.getenv("INPUT_GOOGLE_SPREADSHEET_ID")
    google_worksheet_index = os.getenv("INPUT_GOOGLE_WORKSHEET_INDEX")
    email_column = os.getenv("INPUT_EMAIL_COLUMN")
    files_column = os.getenv("INPUT_FILES_COLUMN")
    passwords = os.getenv("INPUT_PASSWORDS", "passwords.json")
    template_file = os.getenv("INPUT_TEMPLATE_FILE")
    email_status_file = os.getenv("INPUT_EMAIL_STATUS_FILE", "email-status.json")
    no_send_mode = os.getenv("INPUT_NO_SEND_MODE", "false")

    # Validate required inputs
    if not from_email or not email_column:
        print(
            "Error: Required inputs 'from_email' and 'email_column' must be provided."
        )
        sys.exit(1)

    # Check if service_account_json is a path to a JSON file, or a JSON string (and parse it)
    service_account = None
    if service_account_json:
        if os.path.exists(service_account_json):
            print(f"Reading service account from file '{service_account_json}'")
            with open(service_account_json, "r") as f:
                service_account = json.loads(f.read())
        else:
            print(f"Reading service account from JSON string")
            try:
                service_account = json.loads(service_account_json)
            except:
                print(
                    "Error: 'service_account_json' must be a path to a JSON file, or a JSON string."
                )
                sys.exit(1)

    # Check for at least one input source (CSV or Google Spreadsheet)
    if not csv_input_file and not google_spreadsheet_id:
        print(
            "Error: At least one input source (CSV file or Google Spreadsheet ID) must be provided."
        )
        sys.exit(1)

    if (
        not google_spreadsheet_id
        and csv_input_file is not None
        and not os.path.exists(csv_input_file)
    ):
        print("Error: Specified CSV file does not exist.")
        sys.exit(1)

    # Check for at least one mailing mechanism (SendGrid or SMTP)
    if not sendgrid_api_key and (
        not smtp_server or not smtp_username or not smtp_password
    ):
        print(
            "Error: At least one mailing mechanism (SendGrid or SMTP) must be provided."
        )
        sys.exit(1)

    # Check if the passwords.json file exists
    if not os.path.exists(passwords):
        print(f"Error: Specified passwords file '{passwords}' does not exist.")
        sys.exit(1)

    # Build the command for integrimark mail
    command = ["integrimark", "mail"]
    if sendgrid_api_key:
        command += ["--sendgrid-api-key", sendgrid_api_key]
    if smtp_server:
        command += ["--smtp-server", smtp_server]
    if smtp_port:
        command += ["--smtp-port", str(smtp_port)]
    if smtp_username:
        command += ["--smtp-username", smtp_username]
    if smtp_password:
        command += ["--smtp-password", smtp_password]
    command += ["--from-email", from_email]
    if csv_input_file:
        command += ["--csv-input-file", csv_input_file]
    if google_spreadsheet_id:
        command += ["--google-spreadsheet-id", google_spreadsheet_id]
    if google_worksheet_index:
        command += ["--google-worksheet-index", str(google_worksheet_index)]
    command += ["--email-column", email_column]
    if files_column:
        command += ["--files-column", files_column]
    command += ["--passwords", passwords]
    if template_file:
        command += ["--template-file", template_file]
    command += ["--email-status-file", email_status_file]
    if no_send_mode.lower() == "true":
        command += ["--no-send-mode"]

    # Execute the command
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error executing integrimark mail command:", result.stderr)
        sys.exit(1)

    print("IntegriMark Mailing executed successfully.")


if __name__ == "__main__":
    main()
