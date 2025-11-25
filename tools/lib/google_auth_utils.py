import os
import sys
import pickle
from typing import Sequence

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

TOKEN_FILE_DEFAULT = os.path.join(".config", "private", "google", "token.pickle")


def _ensure_token_dir(token_file: str) -> None:
    directory = os.path.dirname(os.path.abspath(token_file))
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def get_credentials(scopes: Sequence[str], token_file: str = TOKEN_FILE_DEFAULT):
    token_file = token_file or TOKEN_FILE_DEFAULT
    _ensure_token_dir(token_file)
    creds = None
    stored_scopes = set()

    if os.path.exists(token_file):
        try:
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
                if creds and creds.scopes:
                    stored_scopes = set(creds.scopes)
        except Exception as e:
            print(f"Warning: Could not load token file: {e}")
            creds = None

    requested_scopes = set(scopes)
    missing_scopes = requested_scopes - stored_scopes

    # If we have valid credentials and all requested scopes are already granted, use them
    if creds and creds.valid and not missing_scopes:
        return creds

    # If token exists but is expired, try to refresh
    if creds and creds.expired and creds.refresh_token:
        try:
            print('Refreshing expired credentials...')
            creds.refresh(Request())
            # After refresh, check if we still need additional scopes
            if creds.valid:
                stored_scopes = set(creds.scopes) if creds.scopes else set()
                missing_scopes = requested_scopes - stored_scopes
                if not missing_scopes:
                    # All scopes are available, save and return
                    with open(token_file, 'wb') as token:
                        pickle.dump(creds, token)
                    return creds
        except Exception as e:
            print(f"Warning: Could not refresh token: {e}")
            creds = None

    # If we need additional scopes or don't have valid credentials, re-authenticate
    client_id = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')

    if not client_id or not client_secret:
        print('Error: GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET must be set')
        print('They should be loaded from Windows Credential Manager')
        print('Make sure your credential-loader script exports them before running these tools')
        sys.exit(1)

    # Combine all scopes (stored + requested) to avoid losing existing permissions
    all_scopes = list(stored_scopes | requested_scopes)
    
    if missing_scopes:
        print(f"Requesting additional scopes: {', '.join(sorted(missing_scopes))}")
        if stored_scopes:
            print(f"Preserving existing scopes: {', '.join(sorted(stored_scopes))}")
    else:
        print('Starting OAuth flow...')

    flow = InstalledAppFlow.from_client_config(
        {
            'installed': {
                'client_id': client_id,
                'client_secret': client_secret,
                'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                'token_uri': 'https://oauth2.googleapis.com/token',
                'redirect_uris': ['http://localhost']
            }
        },
        all_scopes
    )
    creds = flow.run_local_server(port=0)

    # Save the updated credentials with all scopes
    with open(token_file, 'wb') as token:
        pickle.dump(creds, token)

    return creds

