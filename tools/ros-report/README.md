# Ron Stewart Weekly ROS Report Tool

This tool copies Rest of Season (ROS) rankings from a source Google Sheet tab to a destination Google Sheet tab, preserving formatting and clearing outdated data.

## Setup

1. **Install dependencies:**

   ```bash
   pip install google-api-python-client google-auth-oauthlib google-auth
   pip install -e ../google-auth-utils
   ```

2. **Configure OAuth credentials:**

   - Follow the [Managing Secrets Using Windows Credential Manager gist](https://gist.github.com/JohnCastleman/2818eb5127b64ff6d4791b985dbf17fe) to set up the stored credentials registry system.
   - Verify Google OAuth credentials are registered in `%LOCALAPPDATA%\StoredCredentials\stored-credentials.json`.
   - See `../../docs/google-oauth-credential-setup.md` for a quick reference.

3. **Launch Cursor with stored credentials:**

   - If `%LOCALAPPDATA%\StoredCredentials\` exists, the Cursor launcher has likely already been set up. The design principle (discussed in the gist) is to copy `cursor-with-stored-credentials.ps1` to a location collocated with your Cursor shortcut and edit the shortcut to call it or to otherwise start Cursor with a copy of the launcher.
   - This automatically loads `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` environment variables.

4. **First run authentication:**

   The first time you run the script, a browser window will open for OAuth authentication. After authorizing access, credentials are cached in `%APPDATA%/fantasy-football-tools/token.pickle` (Windows) or `~/.config/fantasy-football-tools/token.pickle` (Linux/Mac) for future runs.

## Usage

```bash
python ron-stewart-weekly-ros-report-to-google-sheets-tab.py <source_tab_url>
```

**Example:**

```bash
python ron-stewart-weekly-ros-report-to-google-sheets-tab.py "https://docs.google.com/spreadsheets/d/1A9DKH-slOE-G4qZHA7n9mC4hdLnWvld6KTon8YGmtww/edit?gid=430386019#gid=430386019"
```

## What the script does

1. **Reads source tab:**
   - Extracts sheet ID and tab ID (gid) from the provided URL
   - Gets the source tab name

2. **Finds or creates target tab:**
   - Looks for a tab with the same name as the source tab in the destination sheet
   - Creates the tab if it doesn't exist

3. **Updates A1 cell:**
   - Copies A1 from source to target
   - Adds a line break before " week {weeknumber}" text

4. **Copies data range:**
   - Finds the data range starting at A4 (QB rank 1) and ending at the bottom-right of the Top 150 Position column
   - Copies this range to the target sheet, shifted one column to the right (starting at B4)
   - Preserves cell formatting but converts formulas to values (to avoid overwriting formulas in adjacent columns)

5. **Clears outdated data:**
   - Clears any cells below the pasted range in the Top 150 columns
   - Preserves formulas in columns to the right of the pasted data

## Configuration (`ros-report-sheets.json`)

The script reads the target sheet ID from `ros-report-sheets.json` (in this `tools/ros-report/` directory). Populate it with your target Google Sheet ID or URL:

```json
{
  "target_sheet_id": "https://docs.google.com/spreadsheets/d/1A2B3CExampleSheetID456DEF"
}
```

Provide either the bare ID (`1A2B3CExampleSheetID456DEF`) or the root Sheets URL (without any `#gid` tab suffix).

## Files

- `ron-stewart-weekly-ros-report-to-google-sheets-tab.py` – Main script that copies ROS report from source to destination sheet
- `ros-report-sheets.json` – Configuration file (auto-created, gitignored, lives alongside the script)
- `lib/__init__.py` – Package marker

## Notes

- The script copies values only, not formulas, to avoid overwriting formulas in adjacent columns
- Cell formatting (bold, italic, colors, etc.) is preserved
- The data range is automatically detected by finding the last non-empty row in columns A-X
- Cells below the pasted range are cleared to remove outdated rankings

## Troubleshooting

**Authentication errors:**

- Verify that `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` are exported by your launcher profile or script
- Delete `%APPDATA%/fantasy-football-tools/token.pickle` (Windows) or `~/.config/fantasy-football-tools/token.pickle` (Linux/Mac) and rerun to trigger a fresh OAuth flow if the cached token becomes invalid
- Ensure google-api-python-client, google-auth-oauthlib, and google-auth python libraries are installed

**Config errors:**

- Ensure `tools/ros-report/ros-report-sheets.json` exists and contains a valid `target_sheet_id`

**Range detection errors:**

- The script expects data to start at A4 (QB rank 1)
- Ensure the source tab has data in columns A-X (Top 150 Position column)
