# Ron Stewart Weekly Waiver Report Toolkit

This repository provides a two-step workflow for capturing Ron Stewart's weekly waiver report in a JSON intermediary format and publishing it to a Google Sheet tab with rich formatting, plus an optional HTML preview generator.

## Setup

1. **Install dependencies:**

   ```bash
   pip install google-api-python-client google-auth-oauthlib google-auth
   ```

2. **Configure OAuth credentials:**

   - Follow the [Managing Secrets Using Windows Credential Manager gist](https://gist.github.com/JohnCastleman/2818eb5127b64ff6d4791b985dbf17fe) to set up the stored credentials registry system.
   - Verify Google OAuth credentials are registered in `%LOCALAPPDATA%\StoredCredentials\stored-credentials.json`.
   - See `../../docs/google-oauth-credential-setup.md` for a quick reference.

3. **Launch Cursor with stored credentials:**

   - If `%LOCALAPPDATA%\StoredCredentials\` exists, the Cursor launcher has likely already been set up. The design principle (discussed in the gist) is to copy `cursor-with-stored-credentials.ps1` to a location collocated with your Cursor shortcut and edit the shortcut to call it or to otherwise start Cursor with a copy of the launcher.
   - This automatically loads `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` environment variables.

4. **First run authentication:**

   The first time you run either script, a browser window will open for OAuth authentication. After authorizing access, credentials are cached in `.config/private/google/token.pickle` for future runs (this file is gitignored).

## Workflow Overview

1. **Fetch and archive the report as JSON:**

   ```bash
   python ron-stewart-weekly-waiver-report-to-json.py <source_doc_id_or_url>
   # Append --html to emit an HTML preview alongside the JSON
   ```

   This downloads the Google Doc, processes the content (including inferred formatting and player-section structure), and writes a JSON file under `docs/waiver-reports/` named after the eventual tab (e.g., `W10 waivers.json`).

2. **Publish the JSON report to Google Sheets:**

   ```bash
   python waiver-report-json-to-google-sheets-tab.py docs/waiver-reports/W10 waivers.json
   ```

   This script reads the JSON payload, creates a temporary tab in the target Google Sheet, writes the processed rows (with per-line formatting preserved), and finally renames the tab to the intended week title.

3. **Optional – render the JSON report as HTML:**

   ```bash
   python waiver-report-json-to-html.py docs/waiver-reports/W10 waivers.json
   ```

   This produces an HTML file with a table that mirrors the future sheet layout (useful for quick previews or distribution outside Google Sheets).

## Input Examples

```bash
# Using document ID
python ron-stewart-weekly-waiver-report-to-json.py 1mylGAHOaVpuEiSXOE51iW6McNUa2WfNl_qsvxyffN5s

# Using full URL
python ron-stewart-weekly-waiver-report-to-json.py https://docs.google.com/document/d/1mylGAHOaVpuEiSXOE51iW6McNUa2WfNl_qsvxyffN5s
```

For Sheets publication the target sheet ID is read from `waiver-report-sheets.json` (described below).

## What the scripts accomplish

- **Reader (Doc → JSON):**
  1. Downloads the source Google Doc.
  2. Infers week/tab name (e.g., `W10 waivers`).
  3. Normalizes player rows (merging bullet points beneath each player into a single multi-line segment) while keeping bold on the header line and regular text on subordinate lines.
  4. Serializes the structured rows into a JSON document (with metadata and row segments) for downstream consumers.

- **Writer (JSON → Sheets):**
  1. Loads the JSON payload from the report file.
  2. Creates a temporary tab such as `weekly waivers 1a2b3c4d` to verify write permissions.
  3. Writes every row to column A, preserving multi-line layout and partial formatting via `textFormatRuns` (player headers remain bold, subordinate bullet lines remain regular, notes italic, etc.).
  4. Auto-resizes rows for readability, ensures a minimal boundary row/column, and finally renames the tab to the week name (e.g., `W10 waivers`).

- **HTML renderer (JSON → HTML):**
  1. Loads the JSON report.
  2. Renders a simple HTML page containing a table that mirrors the Google Sheets layout (bold/italic/line breaks preserved).

## Configuration (`waiver-report-sheets.json`)

The writer script auto-creates `waiver-report-sheets.json` (in this `tools/waiver-report/` directory) with placeholder content if it does not exist. Populate it with your target Google Sheet ID or URL:

```json
{
  "target_sheet_id": "https://docs.google.com/spreadsheets/d/1A2B3CExampleSheetID456DEF"
}
```

Provide either the bare ID (`1A2B3CExampleSheetID456DEF`) or the root Sheets URL (without any `#gid` tab suffix). The writer validates access through the Google Sheets API when it attempts to create the temporary tab.

## Files

- `ron-stewart-weekly-waiver-report-to-json.py` – Fetches the Google Doc and writes the JSON intermediary file.
- `waiver-report-json-to-google-sheets-tab.py` – Reads a JSON report and publishes it to a Google Sheets tab.
- `waiver-report-json-to-html.py` – Optional HTML preview generator from the JSON payload.
- `lib/waiver_processing.py` – Shared helpers for parsing content and serializing/deserializing report rows.
- `lib/sheets_utils.py` – Shared Google Sheets helpers (grid setup, temp tab management).
- `lib/google_auth_utils.py` – Shared OAuth helper.
- `waiver-report-sheets.json` – Writer configuration (auto-created, gitignored, lives alongside these scripts).
- `docs/google-oauth-credential-setup.md` – Notes for storing credentials and exporting them before running the tools.
- `.config/private/google/token.pickle` – Cached OAuth token (auto-generated in a private directory, gitignored).

## Notes

- The reader merges player bullets beneath each player header into a single cell with line breaks, preserving bold for the header line only.
- Default JSON files are named after the detected tab (e.g., `W10 waivers.json`). Temporary files use `weekly waivers <uuid>` during processing.
- A temporary tab is always used to validate access; it is renamed to the final week name only after the write succeeds.
- Row heights are auto-sized after insertion, and a one-row/one-column boundary is kept at the bottom/right (2px) for visual framing.
- The HTML renderer mirrors the layout for quick previews but is optional.
- The workflow preserves italicized notes (e.g., WR section notes, drop list notes) and bullet styling throughout.

## Troubleshooting

**Authentication errors:**

- Verify that `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` are exported by your launcher profile or script (see `docs/google-oauth-credential-setup.md`).
- Delete `.config/private/google/token.pickle` and rerun to trigger a fresh OAuth flow if the cached token becomes invalid.
- ensure google-api-python-client, google-auth-oauthlib, and google-auth python libraries are loaded (see below reference link here)

**Config errors (writer step):**

- Ensure `tools/waiver-report/waiver-report-sheets.json` exists and contains a valid sheet ID or URL.

## Dependencies

  ```bash
  pip install google-api-python-client google-auth-oauthlib google-auth
  ```

- First reader run:

  ```bash
  python tools/waiver-report/ron-stewart-weekly-waiver-report-to-json.py <doc_id_or_url>
  ```

  This writes `docs/waiver-reports/<tab name>.json`; if the file exists, a numbered suffix is appended.

- First writer run (after editing `tools/waiver-report/waiver-report-sheets.json` with the real sheet ID):

  ```bash
  python tools/waiver-report/waiver-report-json-to-google-sheets-tab.py docs/waiver-reports/<tab name>.json
  ```

  The script creates a temporary tab, populates it, then renames it to the target week once successful.
