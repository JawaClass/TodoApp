import base64
from email.message import EmailMessage
import os
import pathlib
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource


# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
]

module_path = pathlib.Path(__file__).resolve().parent

token_file = module_path / "token.json"

credentials_file = module_path / "credentials.json"


def send_email(message: EmailMessage):
    gmail_service = get_authenticated_gmail_service()

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {"raw": encoded_message}
    sent_message = (
        gmail_service.users()
        .messages()
        .send(userId="me", body=create_message)
        .execute()
    )
    return sent_message


def get_credentials():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception(
                "Credentials not availabled. Run this method: run_get_credentials_flow"
            )
        # Save the credentials for the next run
        with open(token_file, "w") as token:
            token.write(creds.to_json())
    return creds


def get_authenticated_gmail_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = get_credentials()
    service: Resource = build("gmail", "v1", credentials=creds)
    return service


def run_get_credentials_flow():
    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
    creds = flow.run_local_server()
    # Save the credentials for the next run
    with open(token_file, "w") as token:
        token.write(creds.to_json())
