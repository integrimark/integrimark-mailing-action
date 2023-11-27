import csv
import os
import json
import logging
import subprocess
import sys
import tempfile


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

logger.info("🚀 Starting IntegriMark Mailing...")


def is_valid_json(s):
    """
    Checks if a string is valid JSON.
    """
    try:
        json.loads(s)
    except json.JSONDecodeError:
        return False
    return True


def is_valid_csv_file(filename):
    """
    Checks if a file is a valid CSV file.
    """
    try:
        with open(filename, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                pass  # We don't do anything with the row here, we just check if we can read it
    except csv.Error:
        return False
    return True


def validate_env_var(env_var_name):
    """
    Validates if an environment variable is set.
    Returns the value if set, None otherwise.
    """
    logger.debug(
        f"Validating environment variable '{env_var_name}': {os.environ.get(env_var_name)}"
    )
    return os.environ.get(env_var_name)


def main():
    # CHECK EXISTENCE OF INPUTS

    logger.info("🔍 Validating inputs...")

    # Environment Variables
    sendgrid_api_key = validate_env_var("SENDGRID_API_KEY")
    service_account_json_input = validate_env_var("SERVICE_ACCOUNT_JSON")
    smtp_server = validate_env_var("SMTP_SERVER")
    smtp_port = validate_env_var("SMTP_PORT") or "587"
    smtp_username = validate_env_var("SMTP_USERNAME")
    smtp_password = validate_env_var("SMTP_PASSWORD")

    # GitHub Action Inputs
    from_email = os.getenv("INPUT_FROM_EMAIL")
    csv_input_file = os.getenv("INPUT_CSV_INPUT_FILE")
    google_spreadsheet_id = os.getenv("INPUT_GOOGLE_SPREADSHEET_ID")
    google_worksheet_index = os.getenv("INPUT_GOOGLE_WORKSHEET_INDEX")
    email_column = os.getenv("INPUT_EMAIL_COLUMN")
    files_column = os.getenv("INPUT_FILES_COLUMN")
    passwords = os.getenv("INPUT_PASSWORDS") or "passwords.json"
    template_file = os.getenv("INPUT_TEMPLATE_FILE")
    email_status_file = os.getenv("INPUT_EMAIL_STATUS_FILE") or "email-status.json"
    no_send_mode = os.getenv("INPUT_NO_SEND_MODE", "false")

    # CHECK CONSISTENCY OF INPUTS

    logger.info("🧠 Examining consistency of input parameters...")

    # Validate required inputs
    if not from_email or not email_column:
        if not from_email:
            logger.error(
                "❌ Error: 'from_email' is a required input. It is the email address from which all emails will be sent."
            )
        if not email_column:
            logger.error(
                "❌ Error: 'email_column' is a required input. It is the column in the CSV or Google Spreadsheet that contains the email addresses of the recipients."
            )
        sys.exit(1)

    # Check if service_account_json is a path to a JSON file, or a JSON string (and parse it)
    service_account_json_path = None

    if service_account_json_input is not None:
        logger.debug(
            f"Validating service account JSON input: {service_account_json_input}"
        )

        is_valid_path = os.path.exists(service_account_json_input)
        is_valid_json = is_valid_json(service_account_json_input)

        logger.debug(f"is_valid_path: {is_valid_path}; is_valid_json: {is_valid_json}")

        if is_valid_path:
            # OPTION 1: the argument is a file path

            logger.debug("service_account_json_input is a path to a JSON file.")

            file_contents = open(service_account_json_input).read()
            is_file_valid_json = is_valid_json(file_contents)
            logger.debug(
                f"is_file_valid_json: {is_file_valid_json} (file contents: {file_contents})"
            )
            if not is_file_valid_json:
                logger.error(
                    f"⚠️ Error: Specified service account JSON file '{service_account_json_input}' is not valid JSON."
                )
                sys.exit(1)

            # Set the path to the file
            service_account_json_path = service_account_json_input

        elif is_valid_json:
            # OPTION 2: the argument is a JSON string

            logger.debug("service_account_json_input is a JSON string.")

            # Create a temporary file to store the JSON string
            temp_file = tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            )
            temp_file.write(service_account_json_input)
            temp_file.close()

            # Set the path to the temporary file
            service_account_json_path = temp_file.name

        logger.info(f"Using service account JSON file: {service_account_json_path}")
        logger.debug(
            f"Contents of service account JSON file: {open(service_account_json_path).read()}"
        )

    # Check for at least one input source (CSV or Google Spreadsheet)
    if not csv_input_file and not google_spreadsheet_id:
        logger.error(
            "❌ Error: At least one input source (CSV file or Google Spreadsheet ID) must be provided."
        )
        sys.exit(1)

    # Validate CSV file
    if google_spreadsheet_id is None and csv_input_file is not None:
        if not os.path.exists(csv_input_file):
            logger.error(
                f"❌ Error: Specified CSV file does not exist: {csv_input_file}"
            )
            sys.exit(1)

        if not is_valid_csv_file(csv_input_file):
            logger.error(f"❌ Error: Specified CSV file is not valid: {csv_input_file}")
            logger.debug(f"Contents of CSV file: {open(csv_input_file).read()}")
            sys.exit(1)

    # Check for at least one mailing mechanism (SendGrid or SMTP)
    if not sendgrid_api_key and (
        not smtp_server or not smtp_username or not smtp_password
    ):
        logger.error(
            "❌ Error: At least one mailing mechanism (SendGrid or SMTP) must be provided."
        )
        sys.exit(1)

    # Check if the passwords.json file exists
    if not os.path.exists(passwords):
        logger.error(f"❌ Error: Specified passwords file '{passwords}' does not exist.")
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
    result = subprocess.run(command, capture_output=True, text=True, shell=False)
    if result.returncode != 0:
        logger.error("❌  Error executing integrimark mail command:", result.stderr)
        sys.exit(1)

    logger.info("🎉 IntegriMark Mailing executed successfully.")


if __name__ == "__main__":
    main()
