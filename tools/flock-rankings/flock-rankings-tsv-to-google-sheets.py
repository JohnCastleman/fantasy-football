"""Write Flock Fantasy rankings TSV to Google Sheets."""
import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from google_auth_utils import get_credentials

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ModuleNotFoundError as err:
    print('Error: google-api-python-client is not installed.')
    print('Run "pip install google-api-python-client google-auth-oauthlib google-auth"')
    raise SystemExit(1) from err

# Import shared library functions
SCRIPT_DIR = Path(__file__).resolve().parent
TOOLS_DIR = SCRIPT_DIR.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from lib.sheets_utils import ensure_grid_with_boundary, auto_resize_rows, auto_resize_columns, clear_cells_in_range

CONFIG_FILE = SCRIPT_DIR / 'flock-rankings-sheets.json'


def load_config() -> Dict[str, Any]:
    """Load configuration from JSON file."""
    if not CONFIG_FILE.exists():
        print(f"Error: Config file '{CONFIG_FILE.name}' not found.")
        print(f"Create {CONFIG_FILE} with: {{'target_sheet_id': 'YOUR_SHEET_ID'}}")
        raise SystemExit(1)
    
    data = json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
    target_sheet = data.get('target_sheet_id')
    if not target_sheet:
        print(f"Error: '{CONFIG_FILE}' must contain a valid 'target_sheet_id'.")
        raise SystemExit(1)
    
    sheet_id_match = re.search(r'/d/([a-zA-Z0-9_-]+)', target_sheet)
    if sheet_id_match:
        data['target_sheet_id'] = sheet_id_match.group(1)
    elif not re.match(r'^[a-zA-Z0-9_-]+$', target_sheet):
        print(f"Error: Could not extract sheet ID from '{target_sheet}'.")
        raise SystemExit(1)
    
    return data


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


def get_or_create_tab(sheets_service, sheet_id: str, tab_name: str) -> Tuple[int, bool]:
    """Get tab ID by name, or create it if it doesn't exist.
    
    Returns:
        Tuple of (tab_id, was_created) where was_created is True if tab was just created.
    """
    tab_id = get_tab_id_by_name(sheets_service, sheet_id, tab_name)
    if tab_id is not None:
        return tab_id, False
    
    # Tab doesn't exist, create it
    result = sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={'requests': [{'addSheet': {'properties': {'title': tab_name}}}]}
    ).execute()
    
    new_tab_id = result['replies'][0]['addSheet']['properties']['sheetId']
    return new_tab_id, True


def initialize_tab(sheets_service, sheet_id: str, tab_id: int) -> None:
    """Initialize a newly created tab with empty cell A1 (1x1 grid).
    
    Uses shared ensure_grid_with_boundary from waiver-report lib.
    Also minimizes column A and row 1 for raw data tabs.
    """
    ensure_grid_with_boundary(sheets_service, sheet_id, tab_id, data_rows=1, data_cols=1, minimize_a1=True)


def reset_tab(sheets_service, sheet_id: str, tab_name: str) -> None:
    """Reset a tab by clearing all contents and reinitializing to empty 2x2 grid."""
    tab_id = get_tab_id_by_name(sheets_service, sheet_id, tab_name)
    if tab_id is None:
        print(f"Tab '{tab_name}' does not exist. Nothing to reset.")
        return
    
    print(f"Resetting tab '{tab_name}'...")
    clear_tab(sheets_service, sheet_id, tab_id)
    ensure_grid_with_boundary(sheets_service, sheet_id, tab_id, data_rows=1, data_cols=1, minimize_a1=True)
    print(f"Tab '{tab_name}' reset to empty 2x2 grid")


def clear_tab(sheets_service, sheet_id: str, tab_id: int) -> None:
    """Clear all contents of a tab using the values().clear() API (faster than writing empty values)."""
    # Get the sheet name from tab_id (needed for values().clear() which uses A1 notation)
    try:
        spreadsheet = sheets_service.spreadsheets().get(
            spreadsheetId=sheet_id,
            fields='sheets(properties(sheetId,title,gridProperties(rowCount,columnCount)))'
        ).execute()
    except HttpError as err:
        print(f'Warning: Could not read sheet properties for clearing: {err}')
        return
    
    sheet_name = None
    for sheet in spreadsheet.get('sheets', []):
        props = sheet.get('properties', {})
        if props.get('sheetId') == tab_id:
            sheet_name = props.get('title')
            break
    
    if not sheet_name:
        print(f'Warning: Could not find tab with ID {tab_id}')
        return
    
    # Use values().clear() which is much faster than writing empty values
    # Clear all cells using A1 notation (up to a reasonable limit)
    try:
        sheets_service.spreadsheets().values().clear(
            spreadsheetId=sheet_id,
            range=f"'{sheet_name}'!A1:ZZZ10000"  # Clear up to column ZZZ, row 10000 (should cover most cases)
        ).execute()
    except HttpError as err:
        print(f'Warning: Could not clear tab: {err}')


def get_paste_location(ranking_type: str, position: Optional[str] = None) -> Dict[str, Any]:
    """Get paste location for rankings data.
    
    Maintains same locations as before to facilitate future migration back to main tabs.
    - ROS: Column L (12), Row 3 (stats in row 1, headers in row 2, data starts row 3)
    - WEEKLY: Position-specific columns (position labels in row 2, headers in row 2, data starts row 3)
    """
    if ranking_type == 'ROS':
        return {
            'start_row': 3,  # Data starts at row 3 (stats in row 1, headers in row 2)
            'start_col': 12,  # Column L
            'num_cols': 7  # Rank+Name, Pos+Rank, Team, Snap%, PPR FPs, Pos Rank, Rank
        }
    else:  # WEEKLY
        position_cols = {
            'QB': 7,   # Column G
            'RB': 24,  # Column X
            'WR': 40,  # Column AN
            'TE': 51   # Column AY
        }
        
        if not position:
            raise ValueError("Position required for WEEKLY rankings")
        
        start_col = position_cols.get(position)
        if not start_col:
            raise ValueError(f"Unknown position: {position}")
        
        return {
            'start_row': 3,  # Data starts at row 3 (position label and headers in row 2)
            'start_col': start_col,
            'num_cols': 2  # Rank+Name, Opponent
        }


def parse_tsv(input_stream) -> Tuple[List[str], List[List[str]]]:
    """Parse TSV from stdin or file. Returns (headers, rows)."""
    reader = csv.reader(input_stream, delimiter='\t')
    headers = next(reader, [])
    rows = list(reader)
    return headers, rows


def find_last_row_in_range(
    sheets_service,
    sheet_id: str,
    tab_name: str,
    start_row: int,
    start_col: int,
    num_cols: int,
    max_rows_to_check: int = 1000
) -> int:
    """Find the last row with data in a specific column range.
    Returns the last row index (1-indexed) that has data, or start_row - 1 if none found.
    """
    # Convert column indices to A1 notation (1-indexed columns to letters)
    # Simple approach for columns A-Z (0-25) and AA-AZ (26-51), etc.
    def col_to_letter(col_idx_1based: int) -> str:
        """Convert 1-indexed column to letter(s). Column 1 = A, Column 27 = AA."""
        col_idx = col_idx_1based - 1  # Convert to 0-indexed
        if col_idx < 26:
            return chr(65 + col_idx)
        else:
            return f'{chr(65 + (col_idx - 26) // 26)}{chr(65 + (col_idx - 26) % 26)}'
    
    start_col_letter = col_to_letter(start_col)  # start_col is 1-indexed
    end_col = start_col + num_cols - 1
    end_col_letter = col_to_letter(end_col)
    
    range_name = f"'{tab_name}'!{start_col_letter}{start_row}:{end_col_letter}{start_row + max_rows_to_check - 1}"
    
    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=range_name,
            majorDimension='ROWS'
        ).execute()
    except HttpError as err:
        print(f'Warning: Could not read range to find last row: {err}')
        return start_row - 1
    
    values = result.get('values', [])
    if not values:
        return start_row - 1
    
    # Find the last row that has any non-empty cell in the range
    last_row_offset = -1  # Will be 0-indexed offset from start_row
    for i, row in enumerate(values):
        # Check if any cell in this row has content
        if any(cell and str(cell).strip() for cell in row):
            last_row_offset = i
    
    # If no data found, return start_row - 1 (so clearing won't happen)
    if last_row_offset == -1:
        return start_row - 1
    
    # Convert back to 1-indexed absolute row number
    return start_row + last_row_offset


def write_rows_to_sheet(
    sheets_service,
    sheet_id: str,
    tab_id: int,
    tab_name: str,
    rows: List[List[str]],
    headers: List[str],
    start_row: int,
    start_col: int,
    num_cols: int,
    ranking_type: str,
    position: Optional[str] = None
) -> None:
    """Write headers and rows to Google Sheets.
    
    Note: Headers and stats/position labels are rewritten each time to ensure they're up to date.
    """
    if not rows and not headers:
        print('Warning: No data rows or headers to write')
        return
    
    # Find the current last row in this range before writing (to clean up old data if new data is shorter)
    old_last_row = find_last_row_in_range(
        sheets_service,
        sheet_id,
        tab_name,
        start_row,  # Start from data row (headers are above)
        start_col,
        num_cols
    )
    
    # Header row is one row before data rows
    # For ROS: headers in row 2 (data starts row 3)
    # For WEEKLY: headers in row 2 (data starts row 3)
    header_row = start_row - 1
    
    # Ensure grid is large enough to accommodate headers and data
    end_row_needed = start_row + len(rows) - 1 if rows else header_row
    end_col_needed = start_col + num_cols - 1
    # For WEEKLY, don't minimize boundary row/col (they may contain other positions' data)
    minimize_boundary = ranking_type == 'ROS'
    ensure_grid_with_boundary(sheets_service, sheet_id, tab_id, data_rows=end_row_needed, data_cols=end_col_needed, minimize_a1=True, minimize_boundary=minimize_boundary)
    
    # Check if headers/stats/position labels already exist (by checking if header row has content)
    def check_cell_has_content(sheets_service, sheet_id: str, tab_name: str, row: int, col: int) -> bool:
        """Check if a specific cell has content. Returns True if cell exists and has non-empty content."""
        def col_to_letter(col_idx_1based: int) -> str:
            """Convert 1-indexed column to letter(s)."""
            col_idx = col_idx_1based - 1
            if col_idx < 26:
                return chr(65 + col_idx)
            else:
                return f'{chr(65 + (col_idx - 26) // 26)}{chr(65 + (col_idx - 26) % 26)}'
        
        cell_ref = f"'{tab_name}'!{col_to_letter(col)}{row}"
        try:
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=cell_ref
            ).execute()
            values = result.get('values', [])
            return len(values) > 0 and len(values[0]) > 0 and bool(str(values[0][0]).strip())
        except HttpError:
            return False
    
    # Check if headers already exist (check first header cell)
    headers_exist = False
    if headers:
        headers_exist = check_cell_has_content(sheets_service, sheet_id, tab_name, header_row, start_col)
    
    # Check if stats cell exists (for ROS)
    stats_exists = False
    if ranking_type == 'ROS' and start_col == 12:
        stats_exists = check_cell_has_content(sheets_service, sheet_id, tab_name, 1, 15)  # O1
    
    # Check if position label exists (for WEEKLY)
    position_label_exists = False
    if ranking_type == 'WEEKLY' and position:
        position_labels_cols = {
            'QB': 7,   # G
            'RB': 24,  # X
            'WR': 40,  # AN
            'TE': 51   # AY
        }
        if position in position_labels_cols:
            position_label_exists = check_cell_has_content(sheets_service, sheet_id, tab_name, 1, position_labels_cols[position])
    
    requests = []
    
    # Write headers if provided and they don't already exist
    if headers and not headers_exist:
        header_cells = []
        for i, header in enumerate(headers[:num_cols]):
            header_cells.append({
                'userEnteredValue': {'stringValue': str(header).strip()},
                'userEnteredFormat': {'wrapStrategy': 'WRAP'}
            })
        while len(header_cells) < num_cols:
            header_cells.append({})
        
        requests.append({
            'updateCells': {
                'range': {
                    'sheetId': tab_id,
                    'startRowIndex': header_row - 1,
                    'endRowIndex': header_row,
                    'startColumnIndex': start_col - 1,
                    'endColumnIndex': start_col - 1 + num_cols
                },
                'rows': [{'values': header_cells}],
                'fields': 'userEnteredValue,userEnteredFormat.wrapStrategy'
            }
        })
        
        # For ROS, add merged "stats" cell spanning O1:R1 (columns 15-18, row 1) if it doesn't exist
        if ranking_type == 'ROS' and start_col == 12 and not stats_exists:  # ROS starts at column L (12)
            stats_row = 1  # Row 1 (1-indexed)
            stats_start_col = 15  # Column O (15)
            stats_end_col = 19    # Column R+1 (19, exclusive)
            requests.append({
                'mergeCells': {
                    'range': {
                        'sheetId': tab_id,
                        'startRowIndex': stats_row - 1,  # Convert to 0-indexed (row 1 = index 0)
                        'endRowIndex': stats_row,  # Row 2 (0-indexed exclusive, so index 1)
                        'startColumnIndex': stats_start_col - 1,
                        'endColumnIndex': stats_end_col - 1
                    },
                    'mergeType': 'MERGE_ALL'
                }
            })
            requests.append({
                'updateCells': {
                    'range': {
                        'sheetId': tab_id,
                        'startRowIndex': stats_row - 1,
                        'endRowIndex': stats_row,
                        'startColumnIndex': stats_start_col - 1,
                        'endColumnIndex': stats_start_col
                    },
                    'rows': [{'values': [{
                        'userEnteredValue': {'stringValue': 'stats'},
                        'userEnteredFormat': {'horizontalAlignment': 'CENTER', 'wrapStrategy': 'WRAP'}
                    }]}],
                    'fields': 'userEnteredValue,userEnteredFormat.horizontalAlignment,userEnteredFormat.wrapStrategy'
                }
            })
        
        # For WEEKLY, add merged position label cell (e.g., "QB" in G1:H1) if it doesn't exist
        if ranking_type == 'WEEKLY' and position and not position_label_exists:
            position_labels = {
                'QB': (7, 9),   # Columns G-H (7-8, exclusive end 9)
                'RB': (24, 26), # Columns X-Y (24-25, exclusive end 26)
                'WR': (40, 42), # Columns AN-AO (40-41, exclusive end 42)
                'TE': (51, 53)  # Columns AY-AZ (51-52, exclusive end 53)
            }
            
            if position in position_labels:
                pos_start_col, pos_end_col = position_labels[position]
                position_row = 1  # Row 1 (1-indexed)
                requests.append({
                    'mergeCells': {
                        'range': {
                            'sheetId': tab_id,
                            'startRowIndex': position_row - 1,  # Convert to 0-indexed (row 1 = index 0)
                            'endRowIndex': position_row,  # Row 2 (0-indexed exclusive, so index 1)
                            'startColumnIndex': pos_start_col - 1,
                            'endColumnIndex': pos_end_col - 1
                        },
                        'mergeType': 'MERGE_ALL'
                    }
                })
                requests.append({
                    'updateCells': {
                        'range': {
                            'sheetId': tab_id,
                            'startRowIndex': position_row - 1,
                            'endRowIndex': position_row,
                            'startColumnIndex': pos_start_col - 1,
                            'endColumnIndex': pos_start_col
                        },
                        'rows': [{'values': [{
                            'userEnteredValue': {'stringValue': position},
                            'userEnteredFormat': {'horizontalAlignment': 'CENTER', 'wrapStrategy': 'WRAP'}
                        }]}],
                        'fields': 'userEnteredValue,userEnteredFormat.horizontalAlignment,userEnteredFormat.wrapStrategy'
                    }
                })
    
    # Write data rows if provided
    if rows:
        # Determine which columns are numeric based on headers
        # ROS: snap%, PPR FPs, FPs pos rk, FPs rk are numeric (indices 3, 4, 5, 6)
        # WEEKLY: no numeric columns (all are text)
        numeric_column_indices = set()
        if headers and ranking_type == 'ROS':
            for i, header in enumerate(headers[:num_cols]):
                # Stat columns are numeric
                if header in ['snap%', 'PPR FPs', 'FPs pos rk', 'FPs rk']:
                    numeric_column_indices.add(i)
        
        cell_values = []
        for row in rows:
            cell_row = []
            for i, value in enumerate(row[:num_cols]):
                value_str = str(value).strip()
                if not value_str:
                    cell_row.append({})
                elif i in numeric_column_indices:
                    # Try to convert to number
                    try:
                        # Try float first (for decimals like snap% and PPR FPs)
                        num_value = float(value_str)
                        cell_row.append({'userEnteredValue': {'numberValue': num_value}})
                    except (ValueError, TypeError):
                        # If conversion fails, fall back to string
                        cell_row.append({'userEnteredValue': {'stringValue': value_str}})
                else:
                    # Text columns (rank+name, pos+rk, tm, opp)
                    cell_row.append({'userEnteredValue': {'stringValue': value_str}})
            
            while len(cell_row) < num_cols:
                cell_row.append({})
            cell_values.append(cell_row)
        
        requests.append({
            'updateCells': {
                'range': {
                    'sheetId': tab_id,
                    'startRowIndex': start_row - 1,
                    'endRowIndex': start_row - 1 + len(cell_values),
                    'startColumnIndex': start_col - 1,
                    'endColumnIndex': start_col - 1 + num_cols
                },
                'rows': [{'values': row} for row in cell_values],
                'fields': 'userEnteredValue'
            }
        })
    
    if requests:
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body={'requests': requests}
        ).execute()
    
    # Calculate the new last row (1-indexed)
    new_last_row = start_row + len(rows) - 1 if rows else start_row - 1
    
    # Clear cells below the new data if the new range is shorter than the old range
    # old_last_row will be start_row - 1 if no old data was found
    if old_last_row >= start_row and new_last_row < old_last_row:
        clear_cells_in_range(
            sheets_service,
            sheet_id,
            tab_id,
            new_last_row + 1,  # Start clearing from row after new data (1-indexed, inclusive)
            old_last_row,      # Clear up to and including old last row (1-indexed, inclusive)
            start_col,
            num_cols
        )
        print(f'Cleared {old_last_row - new_last_row} rows of old data below pasted range')
    
    # Auto-resize the pasted range (rows and columns, including header if present)
    # Only auto-resize if dimensions need to grow (see auto_resize_rows/columns for grow-only logic)
    if rows:
        end_row = start_row + len(rows)
    elif headers:
        end_row = header_row + 1
    else:
        end_row = start_row
    
    # Include header row in auto-resize if headers were written
    resize_start_row = header_row if headers else start_row
    auto_resize_rows(sheets_service, sheet_id, tab_id, resize_start_row, end_row)
    
    # Auto-resize row 1 if it contains merged cells (stats for ROS, position labels for WEEKLY)
    if ranking_type == 'ROS' and start_col == 12:
        auto_resize_rows(sheets_service, sheet_id, tab_id, 1, 2)
    elif ranking_type == 'WEEKLY' and position:
        auto_resize_rows(sheets_service, sheet_id, tab_id, 1, 2)
    
    auto_resize_columns(sheets_service, sheet_id, tab_id, start_col, start_col + num_cols)
    
    if rows:
        print(f"Wrote {len(rows)} rows to {start_row}, col {start_col}")
    if headers:
        print(f"Wrote headers to row {header_row}, col {start_col}")


def generate_mock_tsv(ranking_type: str, position: Optional[str] = None, num_players: int = 10) -> Tuple[List[str], List[List[str]]]:
    """Generate mock TSV data for testing.
    
    Mock data follows realistic patterns:
    - Rankings are sequential (1, 2, 3...)
    - pos+rank is unique per position (QB1, QB2... RB1, RB2...)
    - No duplicate position+team combinations
    - Statistical columns: snap% and FP-per-game descending (bigger is better)
    - Statistical columns: pos-rank and rank ascending (1 is best)
    """
    import random
    
    if ranking_type == 'ROS':
        headers = ['rank + name', 'pos + rk', 'tm', 'snap%', 'PPR FPs', 'FPs pos rk', 'FPs rk']
        positions = ['QB', 'RB', 'WR', 'TE']
        teams = ['BUF', 'SF', 'DAL', 'KC', 'PHI', 'BAL', 'DET', 'CIN', 'GB', 'LAR', 'MIN', 'NO', 'ATL', 'TB', 'CAR', 'SEA']
        
        # Track position counts and used position+team combos
        pos_counts = {'QB': 0, 'RB': 0, 'WR': 0, 'TE': 0}
        used_combos = set()
        
        rows = []
        for overall_rank in range(1, num_players + 1):
            # Cycle through positions to intermingle them
            pos = positions[(overall_rank - 1) % len(positions)]
            pos_counts[pos] += 1
            pos_rank = pos_counts[pos]
            
            # Find a team for this position that hasn't been used yet
            available_teams = [t for t in teams if (pos, t) not in used_combos]
            if not available_teams:
                # If all combos used, allow repeats but prefer unused teams
                available_teams = teams
            team = random.choice(available_teams)
            used_combos.add((pos, team))
            
            # Statistical values: descending for snap% and FP-per-game (bigger is better)
            # Starting high and decreasing as rank increases
            snap_pct = max(50.0, 95.0 - (overall_rank * 2.5))
            fp_per_game = max(8.0, 25.0 - (overall_rank * 0.8))
            
            rows.append([
                f"{overall_rank}. {pos}{pos_rank} Player Name",
                f"{pos}{pos_rank}",
                team,
                snap_pct,  # Number, not string
                fp_per_game,  # Number, not string
                pos_rank,  # Number, not string (Pos Rank: ascending 1, 2, 3... per position)
                overall_rank  # Number, not string (Rank: ascending 1, 2, 3... across all)
            ])
        return headers, rows
    else:  # WEEKLY
        if not position:
            raise ValueError("Position required for WEEKLY rankings")
        headers = ['rank + name', 'opp']
        opponents = ['DET', 'GB', 'CHI', 'MIN', 'NO', 'ATL', 'TB', 'CAR', 'SEA', 'LAR', 'NYG', 'WAS', 'PHI', 'DAL', 'NYJ', 'NE']
        
        rows = []
        for rank in range(1, num_players + 1):
            opponent = opponents[(rank - 1) % len(opponents)]
            rows.append([
                f"{rank}. {position}{rank} Player Name",
                opponent
            ])
        return headers, rows


def main():
    parser = argparse.ArgumentParser(description='Write Flock Fantasy TSV to Google Sheets')
    parser.add_argument('--input', '-i', type=Path, help='TSV input file (required unless --mock)')
    parser.add_argument('--type', type=str.upper, choices=['ROS', 'WEEKLY'], required=True, help='Ranking type (case-insensitive)')
    parser.add_argument('--position', type=str.upper, choices=['QB', 'RB', 'WR', 'TE'], help='Position (required for WEEKLY, case-insensitive)')
    parser.add_argument('--week', type=int, help='Week number (optional, not used by script but accepted to keep things flowing)')
    parser.add_argument('--mock', action='store_true', help='Generate and write mock data instead of reading from file')
    parser.add_argument('--mock-players', type=int, default=10, help='Number of mock players to generate (default: 10)')
    parser.add_argument('--reset', action='store_true', help='Reset tab (clear and reinitialize) without writing data')
    args = parser.parse_args()
    
    if args.type == 'WEEKLY' and not args.position and not args.reset:
        parser.error("--position is required for WEEKLY type")
    
    # Warn if --week or --position provided for ROS (not needed, but harmless - only read during ROS processing to keep things flowing)
    if args.type == 'ROS':
        if args.week:
            print(f"Warning: --week is not needed for ROS rankings (ignoring week {args.week})", file=sys.stderr)
        if args.position:
            print(f"Warning: --position is not needed for ROS rankings (ignoring position {args.position})", file=sys.stderr)
    
    # Validate required arguments (allow stdin when --input not provided, for piping)
    if args.reset:
        if args.input or args.mock:
            parser.error("--reset cannot be used with --input or --mock")
    # else: no validation needed - will read from stdin if no --input/--mock provided (for piping)
    
    config = load_config()
    sheet_id = config['target_sheet_id']
    
    creds = get_credentials(['https://www.googleapis.com/auth/spreadsheets'], app_name='fantasy-football-tools')
    service = build('sheets', 'v4', credentials=creds)
    
    # Determine tab name based on type
    if args.type == 'ROS':
        tab_name = 'Flock ROS raw data'
    else:  # WEEKLY
        tab_name = 'Flock weekly raw data'
    
    # Handle reset mode
    if args.reset:
        reset_tab(service, sheet_id, tab_name)
        print(f"Done! https://docs.google.com/spreadsheets/d/{sheet_id}")
        return
    
    # Get or create tab
    print(f"Getting or creating tab '{tab_name}'...")
    tab_id, was_created = get_or_create_tab(service, sheet_id, tab_name)
    
    # Get paste location
    # Note: position is only used/read during WEEKLY processing (ignored for ROS to keep things flowing)
    paste_loc = get_paste_location(args.type, args.position if args.type == 'WEEKLY' else None)
    
    if was_created:
        print(f"Created new tab '{tab_name}'")
        initialize_tab(service, sheet_id, tab_id)
    else:
        print(f"Found existing tab '{tab_name}'")
        # For ROS, clear entire tab. For WEEKLY, only clear the specific position's range
        if args.type == 'ROS':
            print(f"Clearing tab contents...")
            clear_tab(service, sheet_id, tab_id)
        # For WEEKLY, don't clear before writing - just write over old data, then clear excess below
        # (same approach as kdst-rankings tool)
    
    # Get data (from file, stdin, or mock)
    if args.mock:
        # Note: position is only used/read during WEEKLY processing (ignored for ROS to keep things flowing)
        print(f"Generating mock data for {args.type} {'(' + args.position + ')' if args.type == 'WEEKLY' and args.position else ''} with {args.mock_players} players...")
        headers, rows = generate_mock_tsv(args.type, args.position if args.type == 'WEEKLY' else None, args.mock_players)
        print(f"Generated {len(rows)} rows of mock data")
    else:
        # Read TSV (from file or stdin)
        if args.input:
            with args.input.open('r', encoding='utf-8') as f:
                headers, rows = parse_tsv(f)
        else:
            print("Reading TSV from stdin...", file=sys.stderr)
            headers, rows = parse_tsv(sys.stdin)
        print(f"Read {len(rows)} rows from TSV")
    
    # Write to sheet (with headers)
    write_rows_to_sheet(
        service,
        sheet_id,
        tab_id,
        tab_name,
        rows,
        headers,
        paste_loc['start_row'],
        paste_loc['start_col'],
        paste_loc['num_cols'],
        args.type,
        args.position if args.type == 'WEEKLY' else None  # Note: position is only used/read during WEEKLY processing (ignored for ROS to keep things flowing)
    )
    
    print(f"Done! https://docs.google.com/spreadsheets/d/{sheet_id}")


if __name__ == '__main__':
    main()





