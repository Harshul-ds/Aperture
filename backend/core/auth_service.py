# backend/core/auth_service.py (The Definitive Version)

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# --- CONFIGURATION ---
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT_SECRET_PATH = os.path.join(BASE_DIR, 'client_secret.json')
TOKEN_PATH = os.path.join(BASE_DIR, 'token.json')


class AuthService:
    def get_credentials(self) -> Credentials:
        creds = None
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

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

            with open(TOKEN_PATH, 'w') as token_file:
                token_file.write(creds.to_json())
                print(f"Credentials saved to {TOKEN_PATH}")
        
        return creds

auth_service = AuthService()