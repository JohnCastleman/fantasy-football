# Google OAuth Credential Setup

This project uses the stored credentials registry system described in the [Managing Secrets Using Windows Credential Manager gist](https://gist.github.com/JohnCastleman/2818eb5127b64ff6d4791b985dbf17fe).

## Quick Setup

1. **Check if already configured**: If `%LOCALAPPDATA%\StoredCredentials\` exists and contains `cursor-with-stored-credentials.ps1`, the Cursor launcher has likely already been set up. Check that your Cursor shortcut points to a copy of this launcher (typically collocated with the shortcut) or that you run Cursor with this launcher or a copy of it.

2. **If not set up yet**: Follow the complete setup process in the [gist](https://gist.github.com/JohnCastleman/2818eb5127b64ff6d4791b985dbf17fe). This includes:
   - Installing credential management scripts to `%LOCALAPPDATA%\StoredCredentials\`
   - Setting up Google OAuth credentials using the credentials registry
   - Generating a Cursor launcher with stored credentials
   - Copying the launcher to a location collocated with your Cursor shortcut and updating the shortcut to call it

3. **Verify configuration**: Check `%LOCALAPPDATA%\StoredCredentials\stored-credentials.json` to confirm Google OAuth credentials are registered. The Cursor launcher will automatically load them when Cursor launches.

## How It Works

- Credentials are stored encrypted in Windows Credential Manager
- The credentials registry file (`stored-credentials.json`) declares which credentials exist
- The launcher script (like the one located in `%LOCALAPPDATA%\StoredCredentials\` or a copy of it collocated with the Cursor shortcut) loads credentials and sets environment variables before launching Cursor
- All tools in this workspace that need them read credentials from these environment variables

## Token Cache

OAuth refresh tokens are cached in `.config/private/google/token.pickle` (gitignored). This file is automatically created on first authentication and reused for subsequent runs.

## For More Details

See the [complete gist](https://gist.github.com/JohnCastleman/2818eb5127b64ff6d4791b985dbf17fe) for:

- Detailed setup instructions
- Adding new credentials
- Troubleshooting
- Script reference
