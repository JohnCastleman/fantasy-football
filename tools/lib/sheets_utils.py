"""ABOUTME: Shared Google Sheets utility functions for tools.
ABOUTME: Functions for managing Google Sheets tabs and grids."""
from typing import Any, Dict, List, Optional, Tuple

from googleapiclient.errors import HttpError


def ensure_grid_with_boundary(sheets_service, sheet_id: str, tab_id: int, data_rows: int, data_cols: int, minimize_a1: bool = False, minimize_boundary: bool = True) -> None:
    """Ensure grid has at least (data_rows + 1) x (data_cols + 1) dimensions.
    
    Args:
        minimize_a1: If True, also sets column A and row 1 to minimal size (2 pixels).
                     Useful for raw data tabs where all unused dimensions should be minimized.
        minimize_boundary: If True, sets the boundary row/column (after data) to minimal size (2 pixels).
                           Set to False when writing to overlapping ranges (e.g., multiple positions in same sheet)
                           where the boundary row/column might contain data from other ranges.
    """
    data_rows = max(1, data_rows)
    data_cols = max(1, data_cols)

    desired_row_count = data_rows + 1
    desired_col_count = data_cols + 1

    try:
        spreadsheet = sheets_service.spreadsheets().get(
            spreadsheetId=sheet_id,
            fields='sheets(properties(sheetId,gridProperties(rowCount,columnCount)))'
        ).execute()
    except HttpError as err:
        raise RuntimeError(
            f"Unable to inspect Google Sheet '{sheet_id}'. Status: {err.resp.status}"
        ) from err

    sheet_props: Optional[Dict[str, Any]] = None
    for sheet in spreadsheet.get('sheets', []):
        props = sheet.get('properties', {})
        if props.get('sheetId') == tab_id:
            sheet_props = props
            break

    if sheet_props is None:
        raise RuntimeError(f"Could not locate tab ID {tab_id} in sheet '{sheet_id}'.")

    grid_props = sheet_props.get('gridProperties', {})
    current_rows = grid_props.get('rowCount', desired_row_count)
    current_cols = grid_props.get('columnCount', desired_col_count)

    requests: List[Dict[str, Any]] = []
    grid_updates: Dict[str, Any] = {}
    update_fields: List[str] = []

    # Only expand grid, never shrink it (to avoid deleting adjacent data)
    if current_rows < desired_row_count:
        grid_updates['rowCount'] = desired_row_count
        update_fields.append('gridProperties.rowCount')
    if current_cols < desired_col_count:
        grid_updates['columnCount'] = desired_col_count
        update_fields.append('gridProperties.columnCount')

    if update_fields:
        requests.append({
            'updateSheetProperties': {
                'properties': {
                    'sheetId': tab_id,
                    'gridProperties': grid_updates
                },
                'fields': ','.join(update_fields)
            }
        })

    # Only minimize boundary row/column if requested (skip for overlapping ranges like WEEKLY positions)
    if minimize_boundary:
        requests.append({
            'updateDimensionProperties': {
                'range': {
                    'sheetId': tab_id,
                    'dimension': 'ROWS',
                    'startIndex': data_rows,
                    'endIndex': data_rows + 1
                },
                'properties': {
                    'pixelSize': 2
                },
                'fields': 'pixelSize'
            }
        })

        requests.append({
            'updateDimensionProperties': {
                'range': {
                    'sheetId': tab_id,
                    'dimension': 'COLUMNS',
                    'startIndex': data_cols,
                    'endIndex': data_cols + 1
                },
                'properties': {
                    'pixelSize': 2
                },
                'fields': 'pixelSize'
            }
        })
    
    # If minimize_a1 is True, also set column A (index 0) and row 1 (index 0) to minimal size
    if minimize_a1:
        requests.append({
            'updateDimensionProperties': {
                'range': {
                    'sheetId': tab_id,
                    'dimension': 'ROWS',
                    'startIndex': 0,
                    'endIndex': 1
                },
                'properties': {
                    'pixelSize': 2
                },
                'fields': 'pixelSize'
            }
        })
        
        requests.append({
            'updateDimensionProperties': {
                'range': {
                    'sheetId': tab_id,
                    'dimension': 'COLUMNS',
                    'startIndex': 0,
                    'endIndex': 1
                },
                'properties': {
                    'pixelSize': 2
                },
                'fields': 'pixelSize'
            }
        })

    if requests:
        try:
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body={'requests': requests}
            ).execute()
        except HttpError as err:
            raise RuntimeError(
                f"Unable to update grid for tab {tab_id} in sheet '{sheet_id}'. Status: {err.resp.status}"
            ) from err


def auto_resize_rows(sheets_service, sheet_id: str, tab_id: int, start_row: int, end_row: int) -> None:
    """Auto-resize specific rows in a tab.
    
    Args:
        start_row: 1-indexed start row (inclusive)
        end_row: 1-indexed end row (exclusive)
    """
    if start_row >= end_row:
        return

    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={'requests': [{
            'autoResizeDimensions': {
                'dimensions': {
                    'sheetId': tab_id,
                    'dimension': 'ROWS',
                    'startIndex': start_row - 1,  # Convert to 0-indexed
                    'endIndex': end_row - 1  # Convert to 0-indexed, exclusive
                }
            }
        }]}
    ).execute()


def clear_cells_in_range(
    sheets_service,
    sheet_id: str,
    tab_id: int,
    start_row: int,
    end_row: int,
    start_col: int,
    num_cols: int
) -> None:
    """Clear cells in a specific range (set them to empty).
    Uses updateCells API to clear only the exact range specified (same approach as kdst-rankings).
    start_row and end_row are 1-indexed, inclusive.
    start_col is 1-indexed (column 1 = A, column 7 = G, etc.)
    """
    if end_row < start_row:
        return  # Nothing to clear (allow end_row == start_row to clear that single row)
    
    # Get current sheet row count to ensure we don't try to clear beyond it
    try:
        spreadsheet = sheets_service.spreadsheets().get(
            spreadsheetId=sheet_id,
            fields='sheets(properties(sheetId,gridProperties(rowCount)))'
        ).execute()
    except HttpError as err:
        print(f'Warning: Could not read sheet properties for clearing: {err}')
        return
    
    current_row_count = 1000  # Default
    for sheet in spreadsheet.get('sheets', []):
        props = sheet.get('properties', {})
        if props.get('sheetId') == tab_id:
            grid_props = props.get('gridProperties', {})
            current_row_count = grid_props.get('rowCount', 1000)
            break
    
    # Convert to 0-indexed for API
    # start_row and end_row are 1-indexed (inclusive), convert to 0-indexed (start inclusive, end exclusive)
    start_row_index = start_row - 1
    end_row_index = min(end_row + 1, current_row_count)  # end_row is inclusive, so +1 for exclusive end
    
    if end_row_index <= start_row_index:
        return  # Nothing to clear after adjusting for sheet size
    
    # Create empty cells for the range
    num_rows_to_clear = end_row_index - start_row_index
    empty_rows = []
    for _ in range(num_rows_to_clear):
        empty_rows.append({'values': [{}] * num_cols})
    
    requests = [{
        'updateCells': {
            'range': {
                'sheetId': tab_id,
                'startRowIndex': start_row_index,
                'endRowIndex': end_row_index,
                'startColumnIndex': start_col - 1,  # Convert 1-indexed to 0-indexed
                'endColumnIndex': start_col - 1 + num_cols  # Convert 1-indexed to 0-indexed
            },
            'rows': empty_rows,
            'fields': 'userEnteredValue'
        }
    }]
    
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={'requests': requests}
    ).execute()


def auto_resize_columns(sheets_service, sheet_id: str, tab_id: int, start_col: int, end_col: int) -> None:
    """Auto-resize specific columns in a tab using Google Sheets autoResizeDimensions API.
    
    Google Sheets requires columns to have width >= 8 pixels before auto-resize will work.
    This function first sets columns to width 8, then calls the Google Sheets autoResizeDimensions
    API to automatically size columns based on their content.
    
    Args:
        start_col: 1-indexed start column (inclusive)
        end_col: 1-indexed end column (exclusive)
    """
    if start_col >= end_col:
        return

    # Convert 1-indexed to 0-indexed
    start_idx = start_col - 1
    end_idx = end_col - 1
    
    # First, set columns to minimum width that allows auto-resize (8 pixels)
    # This is necessary because Google Sheets autoResizeDimensions doesn't work on columns with width < 8
    # Then call autoResizeDimensions which uses Google Sheets' built-in auto-sizing based on content
    requests = [{
        'updateDimensionProperties': {
            'range': {
                'sheetId': tab_id,
                'dimension': 'COLUMNS',
                'startIndex': start_idx,
                'endIndex': end_idx
            },
            'properties': {
                'pixelSize': 8
            },
            'fields': 'pixelSize'
        }
    }, {
        'autoResizeDimensions': {
            'dimensions': {
                'sheetId': tab_id,
                'dimension': 'COLUMNS',
                'startIndex': start_idx,
                'endIndex': end_idx
            }
        }
    }]
    
    try:
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body={'requests': requests}
        ).execute()
    except HttpError as err:
        # Log but don't fail - auto-resize is a nice-to-have
        print(f'Warning: Could not auto-resize columns {start_col}-{end_col}: {err.resp.status} - {err}')
