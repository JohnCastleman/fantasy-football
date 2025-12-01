import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Determine paths
SCRIPT_DIR = Path(__file__).resolve().parent
TOOLS_DIR = SCRIPT_DIR.parent

# Import google_auth_utils from editable package
from google_auth_utils import get_credentials

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ModuleNotFoundError as err:
    print('Error: google-api-python-client is not installed.')
    print('Run "pip install google-api-python-client google-auth-oauthlib google-auth"')
    raise SystemExit(1) from err

CONFIG_FILE = SCRIPT_DIR / 'kdst-rankings-sheets.json'

# Paste target mappings based on exploration
PASTE_TARGETS = {
    'ROS': {
        'K': {'tab': 'FantasyPros ROS K/DST rankings', 'start_col': 11, 'start_row': 3, 'num_cols': 4},  # L3 (rank, name, team, bye)
        'DST': {'tab': 'FantasyPros ROS K/DST rankings', 'start_col': 16, 'start_row': 3, 'num_cols': 4}  # Q3 (rank, name, team, bye)
    },
    'WEEKLY': {
        'K': {'tab': 'FantasyPros weekly K/DST rankings', 'start_col': 13, 'start_row': 3, 'num_cols': 4},  # N3 (rank, name, team, opp)
        'DST': {'tab': 'FantasyPros weekly K/DST rankings', 'start_col': 18, 'start_row': 3, 'num_cols': 4}  # S3 (rank, name, team, opp)
    }
}


def load_config() -> Dict[str, Any]:
    config_path = CONFIG_FILE
    if not config_path.exists():
        print(f"Warning: Config file '{config_path.name}' not found in {config_path.parent}.")
        print("Creating placeholder config. Please populate 'target_sheet_id' and rerun.")
        config_path.write_text(json.dumps({'target_sheet_id': 'TARGET_SHEET_ID_HERE'}, indent=2), encoding='utf-8')
        raise SystemExit(1)

    data = json.loads(config_path.read_text(encoding='utf-8'))
    target_sheet = data.get('target_sheet_id')
    if not target_sheet or target_sheet == 'TARGET_SHEET_ID_HERE':
        print(f"Error: '{config_path}' must contain a valid 'target_sheet_id'.")
        raise SystemExit(1)

    sheet_id_match = re.search(r'/d/([a-zA-Z0-9_-]+)', target_sheet)
    if sheet_id_match:
        data['target_sheet_id'] = sheet_id_match.group(1)
    elif re.match(r'^[a-zA-Z0-9_-]+$', target_sheet):
        data['target_sheet_id'] = target_sheet
    else:
        print(f"Error: Could not extract sheet ID from '{target_sheet}'.")
        raise SystemExit(1)

    return data


def parse_tsv(input_stream) -> Tuple[List[str], List[Dict[str, str]]]:
    """Parse TSV from stdin or file. Returns (headers, rows)."""
    reader = csv.DictReader(input_stream, delimiter='\t')
    headers = reader.fieldnames or []
    rows = list(reader)
    return headers, rows


def get_tab_id_by_name(sheets_service, sheet_id: str, tab_name: str) -> Optional[int]:
    """Get tab ID by name."""
    try:
        spreadsheet = sheets_service.spreadsheets().get(
            spreadsheetId=sheet_id,
            fields='sheets(properties(sheetId,title))'
        ).execute()
    except HttpError as err:
        raise RuntimeError(
            f"Unable to read Google Sheet '{sheet_id}'. Status: {err.resp.status}"
        ) from err

    for sheet in spreadsheet.get('sheets', []):
        props = sheet.get('properties', {})
        if props.get('title') == tab_name:
            return props.get('sheetId')
    
    return None


def update_week_cell(
    sheets_service,
    sheet_id: str,
    tab_name: str,
    tab_id: int,
    week: int
) -> bool:
    """Update the week number cell if H1 contains 'WEEK:'."""
    # Read H1 to check if it contains "WEEK:"
    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"'{tab_name}'!H1"
        ).execute()
        
        h1_value = result.get('values', [['']])[0][0] if result.get('values') else ''
        
        if 'WEEK:' in str(h1_value).upper():
            # Update I1 (column 8, row 0, 0-indexed)
            requests = [{
                'updateCells': {
                    'range': {
                        'sheetId': tab_id,
                        'startRowIndex': 0,  # Row 1 (0-indexed)
                        'endRowIndex': 1,
                        'startColumnIndex': 8,  # Column I (0-indexed)
                        'endColumnIndex': 9
                    },
                    'rows': [{
                        'values': [{
                            'userEnteredValue': {
                                'numberValue': float(week)
                            }
                        }]
                    }],
                    'fields': 'userEnteredValue'
                }
            }]
            
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body={'requests': requests}
            ).execute()
            return True
    except Exception as e:
        print(f'Warning: Could not check/update week cell: {e}')
        return False
    
    return False


def ensure_sheet_has_rows(
    sheets_service,
    sheet_id: str,
    tab_id: int,
    required_rows: int
) -> None:
    """Ensure the sheet has at least the required number of rows."""
    try:
        spreadsheet = sheets_service.spreadsheets().get(
            spreadsheetId=sheet_id,
            fields='sheets(properties(sheetId,gridProperties(rowCount)))'
        ).execute()
    except HttpError as err:
        raise RuntimeError(
            f"Unable to read sheet properties for '{sheet_id}'. Status: {err.resp.status}"
        ) from err
    
    current_row_count = 1000  # Default
    for sheet in spreadsheet.get('sheets', []):
        props = sheet.get('properties', {})
        if props.get('sheetId') == tab_id:
            grid_props = props.get('gridProperties', {})
            current_row_count = grid_props.get('rowCount', 1000)
            break
    
    if current_row_count >= required_rows:
        return  # Already has enough rows
    
    # Insert rows to expand the sheet
    requests = [{
        'insertDimension': {
            'range': {
                'sheetId': tab_id,
                'dimension': 'ROWS',
                'startIndex': current_row_count,
                'endIndex': required_rows
            },
            'inheritFromBefore': True
        }
    }]
    
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={'requests': requests}
    ).execute()


def write_rows_to_sheet(
    sheets_service,
    sheet_id: str,
    tab_id: int,
    rows: List[Dict[str, str]],
    start_row: int,
    start_col: int,
    num_cols: int,
    headers: List[str]
) -> None:
    """Write TSV rows to Google Sheets starting at specified cell."""
    # Map TSV headers to column order
    # Expected: rank, name, team (and optionally opponent/bye)
    column_order = []
    for col_name in ['rank', 'name', 'team', 'opponent', 'opp', 'bye']:
        if col_name in headers:
            column_order.append(col_name)
    
    # Ensure we have the right number of columns
    if len(column_order) != num_cols:
        print(f"Warning: Expected {num_cols} columns but found {len(column_order)} in TSV")
        print(f"  Headers: {headers}")
        print(f"  Mapped columns: {column_order}")
    
    # Build cell values
    cell_values = []
    for row in rows:
        cell_row = []
        for col_name in column_order[:num_cols]:
            value = row.get(col_name, '')
            # Skip empty values to ensure blank cells (not empty string cells)
            if not value or value.strip() == '':
                cell_row.append({})  # Empty cell
            # Convert rank and bye to numbers if possible
            elif col_name == 'rank' or col_name == 'bye':
                try:
                    cell_row.append({'userEnteredValue': {'numberValue': float(value)}})
                except (ValueError, TypeError):
                    cell_row.append({'userEnteredValue': {'stringValue': str(value)}})
            else:
                cell_row.append({'userEnteredValue': {'stringValue': str(value)}})
        
        # Pad to num_cols if needed
        while len(cell_row) < num_cols:
            cell_row.append({'userEnteredValue': {'stringValue': ''}})
        
        cell_values.append(cell_row)
    
    if not cell_values:
        print('Warning: No data rows to write')
        return
    
    # Write to sheet
    # start_row is 1-indexed (row 3 = start_row 3), convert to 0-indexed for API
    start_row_index = start_row - 1
    requests = [{
        'updateCells': {
            'range': {
                'sheetId': tab_id,
                'startRowIndex': start_row_index,
                'endRowIndex': start_row_index + len(cell_values),
                'startColumnIndex': start_col,
                'endColumnIndex': start_col + num_cols
            },
            'rows': [{'values': row} for row in cell_values],
            'fields': 'userEnteredValue'
        }
    }]
    
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={'requests': requests}
    ).execute()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Write FantasyPros rankings TSV to Google Sheets'
    )
    parser.add_argument(
        '--input', '-i',
        help='Input TSV file (default: read from stdin)'
    )
    parser.add_argument(
        '--position', '-p',
        required=True,
        choices=['K', 'DST'],
        help='Position: K (Kicker) or DST (Defense/Special Teams)'
    )
    parser.add_argument(
        '--type', '-t',
        required=True,
        choices=['ROS', 'WEEKLY'],
        help='Ranking type: ROS (Rest of Season) or WEEKLY'
    )
    parser.add_argument(
        '--week', '-w',
        type=int,
        help='Week number (optional, used to update I1 for weekly DST if provided)'
    )
    return parser.parse_args()


def main():
    config = load_config()
    target_sheet_id = config['target_sheet_id']
    
    args = parse_args()
    
    # Get paste target configuration
    if args.type not in PASTE_TARGETS:
        print(f'Error: Unknown ranking type: {args.type}')
        raise SystemExit(1)
    
    if args.position not in PASTE_TARGETS[args.type]:
        print(f'Error: Position {args.position} not supported for {args.type} rankings')
        raise SystemExit(1)
    
    target_config = PASTE_TARGETS[args.type][args.position]
    tab_name = target_config['tab']
    start_col = target_config['start_col']
    start_row = target_config['start_row']
    num_cols = target_config['num_cols']
    
    # Read TSV
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            headers, rows = parse_tsv(f)
    else:
        headers, rows = parse_tsv(sys.stdin)
    
    if not rows:
        print('Error: No data rows found in TSV input')
        raise SystemExit(1)
    
    print(f'Read {len(rows)} rows from TSV')
    print(f'Headers: {headers}')
    
    # Authenticate and get sheet service
    creds = get_credentials(['https://www.googleapis.com/auth/spreadsheets'], app_name='fantasy-football-tools')
    sheets_service = build('sheets', 'v4', credentials=creds)
    
    # Get tab ID
    tab_id = get_tab_id_by_name(sheets_service, target_sheet_id, tab_name)
    if tab_id is None:
        print(f'Error: Tab "{tab_name}" not found in sheet')
        raise SystemExit(1)
    
    print(f'Target: Sheet "{target_sheet_id}", Tab "{tab_name}" (ID: {tab_id})')
    col_letter = chr(65 + start_col) if start_col < 26 else f'A{chr(65 + (start_col-26))}'
    print(f'Writing to: {col_letter}{start_row} ({num_cols} columns)')
    
    # Ensure sheet has enough rows (API doesn't auto-expand like UI does)
    required_rows = start_row + len(rows) - 1  # start_row is 1-indexed
    ensure_sheet_has_rows(sheets_service, target_sheet_id, tab_id, required_rows)
    
    # Write data
    write_rows_to_sheet(
        sheets_service,
        target_sheet_id,
        tab_id,
        rows,
        start_row,
        start_col,
        num_cols,
        headers
    )
    print(f'Wrote {len(rows)} rows successfully')
    
    # Update week number if --week is provided and H1 contains "WEEK:"
    if args.week is not None:
        if update_week_cell(sheets_service, target_sheet_id, tab_name, tab_id, args.week):
            print(f'Updated week number to {args.week}')
    
    print('Done! View the sheet at:')
    print(f'https://docs.google.com/spreadsheets/d/{target_sheet_id}')


if __name__ == '__main__':
    main()



