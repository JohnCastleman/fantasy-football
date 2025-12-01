# FantasyPros K/DST Rankings to Google Sheets Tool

This tool writes FantasyPros rankings TSV output directly to Google Sheets.

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

   The first time you run the script, a browser window will open for OAuth authentication. After authorizing access, credentials are cached in `.config/private/google/token.pickle` for future runs (this file is gitignored).

5. **Configure target sheet:**

   - Edit `kdst-rankings-sheets.json` and set `target_sheet_id` to your destination Google Sheet ID or URL

## Usage

### From TSV file

```bash
# Generate TSV and write to file
node -e "import('./client/dump.js').then(m => m.dumpRosKRankings({outputFile: 'k.tsv'}))"

# Write to Google Sheets
python tools/kdst-rankings/fantasypros-kdst-rankings-to-google-sheets.py --input k.tsv --position K --type ROS
```

### From stdin (pipe)

```bash
# Pipe TSV directly to script
node -e "import('./client/dump.js').then(m => m.dumpRosKRankings())" | python tools/kdst-rankings/fantasypros-kdst-rankings-to-google-sheets.py --position K --type ROS
```

## Arguments

- `--position`, `-p`: Position (`K` or `DST`)
- `--type`, `-t`: Ranking type (`ROS` or `WEEKLY`)
- `--week`, `-w`: Week number (optional, used to update I1 for weekly DST if provided)
- `--input`, `-i`: Input TSV file (optional, defaults to stdin)

## What it does

1. Reads TSV data (from file or stdin)
2. Parses headers and rows
3. Maps TSV columns to sheet columns (rank, name, team, opponent/bye)
4. Writes to the appropriate tab and cell range:
   - **ROS K**: "FantasyPros ROS K/DST rankings", column L, row 3
   - **ROS DST**: "FantasyPros ROS K/DST rankings", column Q, row 3
   - **Weekly K**: "FantasyPros weekly K/DST rankings", column N, row 3
   - **Weekly DST**: "FantasyPros weekly K/DST rankings", column S, row 3

## Weekly Workflow

For each week, run all four rankings dumps:

```bash
# ROS K
node tools/kdst-rankings/dump-ros-k.js 2>$null | python tools/kdst-rankings/fantasypros-kdst-rankings-to-google-sheets.py --position K --type ROS

# ROS DST
node tools/kdst-rankings/dump-ros-dst.js 2>$null | python tools/kdst-rankings/fantasypros-kdst-rankings-to-google-sheets.py --position DST --type ROS

# Weekly K
node tools/kdst-rankings/dump-weekly-k.js 2>$null | python tools/kdst-rankings/fantasypros-kdst-rankings-to-google-sheets.py --position K --type WEEKLY --week 13

# Weekly DST (updates I1 with week number)
node tools/kdst-rankings/dump-weekly-dst.js 2>$null | python tools/kdst-rankings/fantasypros-kdst-rankings-to-google-sheets.py --position DST --type WEEKLY --week 13
```

## Future CLI Integration

Once CLI parameter overrides are implemented in the client/server tools (see `docs/plans/cli-parameter-overrides.md`), the dump scripts (`dump-*.js`) will be replaced by direct CLI calls. The planned CLI interface will support:

- `-d, --dump`: TSV output format
- `-t, --type`: Ranking type (ROS, WEEKLY, DYNASTY, DRAFT)
- `-p, --position`: Position (K, DST, etc.)
- `-o, --output`: Output file or stdout

**Future workflow** (once CLI is implemented):

```bash
# ROS K (example)
npm test -- -d -t ROS -p K | python tools/kdst-rankings/fantasypros-kdst-rankings-to-google-sheets.py --position K --type ROS

# Weekly DST (example)
npm test -- -d -t WEEKLY -p DST | python tools/kdst-rankings/fantasypros-kdst-rankings-to-google-sheets.py --position DST --type WEEKLY --week 13
```

The dump scripts are temporary workarounds until the CLI interface is complete. See `docs/architecture.md` and `docs/development.md` for architectural context and development roadmap.

## Files

- `fantasypros-kdst-rankings-to-google-sheets.py` – Main script
- `kdst-rankings-sheets.json` – Configuration file (gitignored)
- `dump-ros-k.js` – ROS Kicker rankings dump script
- `dump-ros-dst.js` – ROS Defense/Special Teams rankings dump script
- `dump-weekly-k.js` – Weekly Kicker rankings dump script
- `dump-weekly-dst.js` – Weekly Defense/Special Teams rankings dump script
- `README.md` – This file
