# backend/core/auth_service.py (The Definitive Version)

# backend/core/auth_service.py (The Definitive Version)

import os
import json
import keyring
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# --- CONFIGURATION ---
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT_SECRET_PATH = os.path.join(BASE_DIR, 'client_secret.json')

# --- KEYRING CONFIGURATION ---
KEYRING_SERVICE_NAME = "Aperture"
KEYRING_USERNAME = "google_oauth_token"


class AuthService:
    def get_credentials(self) -> Credentials:
        creds_json = keyring.get_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME)
        creds = Credentials.from_authorized_user_info(json.loads(creds_json), SCOPES) if creds_json else None

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # We use the manual "out-of-band" (oob) flow, which is the
                # standard for CLI tools and cloud dev environments.
                with open(CLIENT_SECRET_PATH, 'r') as secrets_file:
                    client_config = json.load(secrets_file)

                # This configuration explicitly tells Google to show the user a code
                # instead of trying to redirect their browser. This solves all our issues.
                flow = InstalledAppFlow.from_client_config(
                    client_config=client_config,
                    scopes=SCOPES,
                    redirect_uri='urn:ietf:wg:oauth:2.0:oob'
                )

                auth_url, _ = flow.authorization_url(prompt='consent')
                print('--- GOOGLE AUTHENTICATION REQUIRED ---')
                print('Please go to this URL in your browser:')
                print(auth_url)
                print('-----------------------------------------')
                
                auth_code = input('After authorizing, paste the code from your browser here: ')
                flow.fetch_token(code=auth_code)
                creds = flow.credentials

            keyring.set_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME, creds.to_json())
            print(f"Credentials saved to system keyring under service '{KEYRING_SERVICE_NAME}'.")
        
        return creds

auth_service = AuthService()

# They are the public interface to more complex AuthService class.

import googleapiclient.discovery
from typing import Optional

def get_user_credentials() -> Optional[Credentials]:
    """
    Safely loads user credentials from the system keyring if they exist.
    This version does NOT trigger a new authentication flow. It's for checking status.
    """
    creds_json = keyring.get_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME)
    if not creds_json:
        return None

    try:
        creds = Credentials.from_authorized_user_info(json.loads(creds_json), SCOPES)
        if creds and creds.valid:
            return creds
        elif creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            keyring.set_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME, creds.to_json())
            return creds
    except Exception as e:
        print(f"Error loading token from keyring: {e}. Please re-authenticate.")
        return None

    return None

def build_google_service(creds: Credentials) -> googleapiclient.discovery.Resource:
    """Builds the Gmail API service object from a credentials object."""
    return googleapiclient.discovery.build('gmail', 'v1', credentials=creds)

def clear_user_credentials() -> None:
    """Removes the user's credentials from the system keyring."""
    try:
        keyring.delete_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME)
        print("User credentials cleared from keyring.")
    except keyring.errors.PasswordDeleteError:
        print("No credentials found in keyring to clear.")
