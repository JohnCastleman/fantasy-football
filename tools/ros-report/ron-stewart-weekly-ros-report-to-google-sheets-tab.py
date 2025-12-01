import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Determine paths
SCRIPT_DIR = Path(__file__).resolve().parent
TOOLS_DIR = SCRIPT_DIR.parent

# Add script directory to sys.path for local lib imports
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ModuleNotFoundError as err:
    print('Error: google-api-python-client is not installed.')
    print('Run "pip install google-api-python-client google-auth-oauthlib google-auth"')
    raise SystemExit(1) from err

# Import google_auth_utils from editable package
from google_auth_utils import get_credentials

CONFIG_FILE = SCRIPT_DIR / 'ros-report-sheets.json'


def extract_sheet_and_tab_ids(url: str) -> Tuple[str, Optional[int]]:
    """Extract sheet ID and tab ID (gid) from a Google Sheets URL.
    
    Supports URLs with gid as:
    - Query parameter: ?gid=123
    - Fragment: #gid=123
    - Additional query param: &gid=123
    """
    sheet_id_match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if not sheet_id_match:
        raise ValueError(f'Could not extract sheet ID from {url!r}')
    
    sheet_id = sheet_id_match.group(1)
    
    # Match gid as query parameter (?gid=), fragment (#gid=), or additional param (&gid=)
    gid_match = re.search(r'[?#&]gid=(\d+)', url)
    tab_id = int(gid_match.group(1)) if gid_match else None
    
    return sheet_id, tab_id


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


def get_tab_name_by_id(sheets_service, sheet_id: str, tab_id: int) -> Optional[str]:
    """Get the name of a tab by its ID."""
    try:
        spreadsheet = sheets_service.spreadsheets().get(
            spreadsheetId=sheet_id,
            fields='sheets(properties(sheetId,title))'
        ).execute()
    except HttpError as err:
        if err.resp.status == 403:
            raise RuntimeError(
                f"Permission denied accessing source sheet '{sheet_id}'. "
                f"Status: {err.resp.status}\n"
                f"Please ensure your Google account has view access to the source sheet."
            ) from err
        else:
            raise RuntimeError(
                f"Unable to read Google Sheet '{sheet_id}'. Status: {err.resp.status}"
            ) from err

    for sheet in spreadsheet.get('sheets', []):
        props = sheet.get('properties', {})
        if props.get('sheetId') == tab_id:
            return props.get('title')
    
    return None


def find_or_create_tab(sheets_service, sheet_id: str, tab_name: str) -> int:
    """Find existing tab by name or create a new one. Returns tab ID."""
    try:
        spreadsheet = sheets_service.spreadsheets().get(
            spreadsheetId=sheet_id,
            fields='sheets(properties(sheetId,title))'
        ).execute()
    except HttpError as err:
        if err.resp.status == 403:
            raise RuntimeError(
                f"Permission denied accessing target sheet '{sheet_id}'. "
                f"Status: {err.resp.status}\n"
                f"Please ensure:\n"
                f"  1. The sheet ID in ros-report-sheets.json is correct\n"
                f"  2. Your Google account has edit access to the target sheet\n"
                f"  3. The OAuth token has the required permissions"
            ) from err
        else:
            raise RuntimeError(
                f"Unable to read Google Sheet '{sheet_id}'. Status: {err.resp.status}"
            ) from err

    for sheet in spreadsheet.get('sheets', []):
        props = sheet.get('properties', {})
        if props.get('title') == tab_name:
            return props.get('sheetId')

    # Tab doesn't exist, create it
    result = sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={'requests': [{'addSheet': {'properties': {'title': tab_name}}}]}
    ).execute()

    return result['replies'][0]['addSheet']['properties']['sheetId']


def find_data_range(sheets_service, sheet_id: str, tab_id: int) -> Tuple[int, int, int, int]:
    """Find the data range starting at A4 and ending at the bottom-right of Top 150 Position column.
    Returns (start_row, start_col, end_row, end_col) where A4 = (3, 0) (0-indexed).
    """
    # Get tab name to construct proper range reference
    try:
        spreadsheet = sheets_service.spreadsheets().get(
            spreadsheetId=sheet_id,
            fields='sheets(properties(sheetId,title))'
        ).execute()
    except HttpError as err:
        raise RuntimeError(
            f"Unable to read sheet metadata for '{sheet_id}'. Status: {err.resp.status}"
        ) from err
    
    tab_name = None
    for sheet in spreadsheet.get('sheets', []):
        props = sheet.get('properties', {})
        if props.get('sheetId') == tab_id:
            tab_name = props.get('title')
            break
    
    if not tab_name:
        raise RuntimeError(f"Could not find tab with ID {tab_id} in sheet '{sheet_id}'")
    
    # Read a large range to find the actual data extent
    # Start from A4 (row index 3) and read down to row 200, across columns A-X (0-23)
    range_name = f"'{tab_name}'!A4:X200"
    
    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=range_name,
            majorDimension='ROWS'
        ).execute()
    except HttpError as err:
        raise RuntimeError(
            f"Unable to read data range '{range_name}' from sheet '{sheet_id}'. Status: {err.resp.status}"
        ) from err

    values = result.get('values', [])
    if not values:
        raise RuntimeError("No data found starting at A4")

    # Find the last non-empty row
    end_row = 3  # Start at row 4 (0-indexed: 3)
    for i, row in enumerate(values):
        # Check if any cell in columns A-X (0-23) has content
        if any(cell and str(cell).strip() for cell in (row[:24] if len(row) > 24 else row)):
            end_row = 3 + i
    
    # Find the rightmost column with data (within A-X, i.e., columns 0-23)
    end_col = 0
    for row in values[:end_row - 3 + 1]:
        for col_idx in range(min(24, len(row))):
            if row[col_idx] and str(row[col_idx]).strip():
                end_col = max(end_col, col_idx)

    # Return: start_row=3 (A4), start_col=0 (A), end_row, end_col
    return 3, 0, end_row, end_col


def modify_a1_cell(cell_value: str) -> str:
    """Add a line break before ' week {weeknumber}' in A1 cell."""
    # Match pattern like " week 13" or " WEEK 13" (case insensitive)
    pattern = r'(\s+week\s+\d+)'
    match = re.search(pattern, cell_value, re.IGNORECASE)
    if match:
        # Insert newline before the matched text
        return cell_value[:match.start()] + '\n' + cell_value[match.start():]
    return cell_value


def copy_cell_data(source_cell: Dict[str, Any]) -> Dict[str, Any]:
    """Copy a cell's data, preserving values and basic formatting."""
    cell_data: Dict[str, Any] = {}
    
    # Copy value
    if 'userEnteredValue' in source_cell:
        cell_data['userEnteredValue'] = source_cell['userEnteredValue']
    
    # Copy formatting (but not formulas - we'll handle formulas separately)
    if 'userEnteredFormat' in source_cell:
        cell_data['userEnteredFormat'] = source_cell['userEnteredFormat']
    
    # Copy text format runs if present
    if 'textFormatRuns' in source_cell:
        cell_data['textFormatRuns'] = source_cell['textFormatRuns']
    
    return cell_data


def copy_range_to_target(
    sheets_service,
    source_sheet_id: str,
    source_tab_id: int,
    source_tab_name: str,
    target_sheet_id: str,
    target_tab_id: int,
    source_start_row: int,
    source_start_col: int,
    source_end_row: int,
    source_end_col: int,
    target_start_row: int,
    target_start_col: int
) -> None:
    """Copy a range from source to target, preserving formatting but not formulas."""
    # Read source cells with formatting - use tab name for range reference
    source_range = f"'{source_tab_name}'!{chr(65 + source_start_col)}{source_start_row + 1}:{chr(65 + source_end_col)}{source_end_row + 1}"
    
    try:
        source_data = sheets_service.spreadsheets().get(
            spreadsheetId=source_sheet_id,
            ranges=[source_range],
            includeGridData=True
        ).execute()
    except HttpError as err:
        raise RuntimeError(
            f"Unable to read source range '{source_range}'. Status: {err.resp.status}"
        ) from err

    source_sheet = source_data.get('sheets', [{}])[0]
    source_rows = source_sheet.get('data', [{}])[0].get('rowData', [])

    if not source_rows:
        raise RuntimeError(f"No data found in source range '{source_range}'")

    # Build batch update requests
    requests: List[Dict[str, Any]] = []
    
    num_rows = source_end_row - source_start_row + 1
    num_cols = source_end_col - source_start_col + 1
    
    for row_idx in range(num_rows):
        if row_idx >= len(source_rows):
            break
        
        source_row = source_rows[row_idx]
        source_cells = source_row.get('values', [])
        
        target_cells = []
        for col_idx in range(num_cols):
            if col_idx < len(source_cells):
                source_cell = source_cells[col_idx]
                # Only copy if it's not a formula (we want to preserve formulas in target)
                if 'userEnteredValue' in source_cell:
                    value = source_cell['userEnteredValue']
                    # Skip formulas - we'll copy values only
                    if 'formulaValue' not in value:
                        target_cells.append(copy_cell_data(source_cell))
                    else:
                        # For formulas, copy as value if it has an evaluated value
                        if 'effectiveValue' in source_cell:
                            eval_value = source_cell['effectiveValue']
                            cell_copy = {}
                            if 'numberValue' in eval_value:
                                cell_copy['userEnteredValue'] = {'numberValue': eval_value['numberValue']}
                            elif 'stringValue' in eval_value:
                                cell_copy['userEnteredValue'] = {'stringValue': eval_value['stringValue']}
                            elif 'boolValue' in eval_value:
                                cell_copy['userEnteredValue'] = {'boolValue': eval_value['boolValue']}
                            if 'userEnteredFormat' in source_cell:
                                cell_copy['userEnteredFormat'] = source_cell['userEnteredFormat']
                            target_cells.append(cell_copy)
                        else:
                            # Empty cell if formula has no evaluated value
                            target_cells.append({})
                else:
                    target_cells.append({})
            else:
                target_cells.append({})
        
        requests.append({
            'updateCells': {
                'range': {
                    'sheetId': target_tab_id,
                    'startRowIndex': target_start_row + row_idx,
                    'endRowIndex': target_start_row + row_idx + 1,
                    'startColumnIndex': target_start_col,
                    'endColumnIndex': target_start_col + num_cols
                },
                'rows': [{'values': target_cells}],
                'fields': 'userEnteredValue,userEnteredFormat,textFormatRuns'
            }
        })

    if requests:
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=target_sheet_id,
            body={'requests': requests}
        ).execute()


def delete_rows_below(
    sheets_service,
    target_sheet_id: str,
    target_tab_id: int,
    end_row: int,
    delete_to_row: int = 1000
) -> None:
    """Delete all rows below the pasted range."""
    if end_row >= delete_to_row:
        return
    
    num_rows_to_delete = delete_to_row - end_row - 1
    
    if num_rows_to_delete <= 0:
        return
    
    # Get the actual row count of the sheet to know how many rows exist
    try:
        spreadsheet = sheets_service.spreadsheets().get(
            spreadsheetId=target_sheet_id,
            fields='sheets(properties(sheetId,gridProperties(rowCount)))'
        ).execute()
    except HttpError as err:
        raise RuntimeError(
            f"Unable to read sheet properties for '{target_sheet_id}'. Status: {err.resp.status}"
        ) from err
    
    # Find the tab and get its row count
    actual_row_count = delete_to_row  # Default fallback
    for sheet in spreadsheet.get('sheets', []):
        props = sheet.get('properties', {})
        if props.get('sheetId') == target_tab_id:
            grid_props = props.get('gridProperties', {})
            actual_row_count = grid_props.get('rowCount', delete_to_row)
            break
    
    # Only delete rows that actually exist
    if end_row + 1 >= actual_row_count:
        return
    
    # Delete rows below the pasted range
    delete_end = min(actual_row_count, delete_to_row)
    
    requests = [{
        'deleteDimension': {
            'range': {
                'sheetId': target_tab_id,
                'dimension': 'ROWS',
                'startIndex': end_row + 1,
                'endIndex': delete_end
            }
        }
    }]
    
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=target_sheet_id,
        body={'requests': requests}
    ).execute()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Copy ROS report from source Google Sheet tab to destination tab'
    )
    parser.add_argument(
        'source_url',
        help='Google Sheets tab URL (e.g., https://docs.google.com/spreadsheets/d/SHEET_ID/edit?gid=TAB_ID)'
    )
    return parser.parse_args()


def main():
    config = load_config()
    target_sheet_id = config['target_sheet_id']

    args = parse_args()
    
    try:
        source_sheet_id, source_tab_id = extract_sheet_and_tab_ids(args.source_url)
    except ValueError as err:
        print(f'Error: {err}')
        raise SystemExit(1)

    if source_tab_id is None:
        print('Error: Source URL must include both sheet ID and tab ID (gid parameter).')
        print('Example: https://docs.google.com/spreadsheets/d/SHEET_ID/edit?gid=TAB_ID')
        print(f'Received URL: {args.source_url}')
        raise SystemExit(1)

    creds = get_credentials(['https://www.googleapis.com/auth/spreadsheets'], app_name='fantasy-football-tools')
    sheets_service = build('sheets', 'v4', credentials=creds)

    # Get source tab name
    source_tab_name = get_tab_name_by_id(sheets_service, source_sheet_id, source_tab_id)
    if not source_tab_name:
        print(f'Error: Could not find tab with ID {source_tab_id} in source sheet.')
        raise SystemExit(1)

    print(f'Source tab: "{source_tab_name}"')

    # Find or create target tab
    target_tab_id = find_or_create_tab(sheets_service, target_sheet_id, source_tab_name)
    print(f'Target tab: "{source_tab_name}" (ID: {target_tab_id})')

    # Read and modify A1
    try:
        a1_result = sheets_service.spreadsheets().values().get(
            spreadsheetId=source_sheet_id,
            range='A1'
        ).execute()
        a1_value = a1_result.get('values', [[None]])[0][0] if a1_result.get('values') else None
        
        # Also get A1 with formatting
        a1_data = sheets_service.spreadsheets().get(
            spreadsheetId=source_sheet_id,
            ranges=['A1'],
            includeGridData=True
        ).execute()
        
        a1_cell_data = {}
        if a1_data.get('sheets', [{}])[0].get('data', [{}])[0].get('rowData', [{}])[0].get('values', [{}])[0]:
            a1_cell_data = a1_data['sheets'][0]['data'][0]['rowData'][0]['values'][0]
        
        if a1_value:
            modified_a1 = modify_a1_cell(str(a1_value))
            
            # Update A1 in target
            a1_update = copy_cell_data(a1_cell_data)
            a1_update['userEnteredValue'] = {'stringValue': modified_a1}
            
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=target_sheet_id,
                body={'requests': [{
                    'updateCells': {
                        'range': {
                            'sheetId': target_tab_id,
                            'startRowIndex': 0,
                            'endRowIndex': 1,
                            'startColumnIndex': 0,
                            'endColumnIndex': 1
                        },
                        'rows': [{'values': [a1_update]}],
                        'fields': 'userEnteredValue,userEnteredFormat,textFormatRuns'
                    }
                }]}
            ).execute()
            print('Updated A1 cell')
    except HttpError as err:
        print(f'Warning: Could not read/update A1: {err}')

    # Find data range
    source_start_row, source_start_col, source_end_row, source_end_col = find_data_range(
        sheets_service, source_sheet_id, source_tab_id
    )
    print(f'Source data range: A{source_start_row + 1}:{chr(65 + source_end_col)}{source_end_row + 1}')

    # Copy data range to target (shifted one column right: B4 instead of A4)
    target_start_row = source_start_row  # Same row (4)
    target_start_col = source_start_col + 1  # Shifted right (B instead of A)
    target_end_row = source_end_row
    target_end_col = target_start_col + (source_end_col - source_start_col)
    
    print(f'Copying to target range: {chr(65 + target_start_col)}{target_start_row + 1}:{chr(65 + target_end_col)}{target_end_row + 1}')
    
    copy_range_to_target(
        sheets_service,
        source_sheet_id,
        source_tab_id,
        source_tab_name,
        target_sheet_id,
        target_tab_id,
        source_start_row,
        source_start_col,
        source_end_row,
        source_end_col,
        target_start_row,
        target_start_col
    )
    print('Data copied successfully')

    # Delete all rows below the pasted range
    delete_rows_below(
        sheets_service,
        target_sheet_id,
        target_tab_id,
        target_end_row
    )
    print('Deleted outdated rows below pasted range')

    print('Done! View the sheet at:')
    print(f'https://docs.google.com/spreadsheets/d/{target_sheet_id}')


if __name__ == '__main__':
    main()

