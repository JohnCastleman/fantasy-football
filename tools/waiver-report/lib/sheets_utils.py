import uuid
from typing import Any, Dict, List, Optional, Tuple

from googleapiclient.errors import HttpError


def ensure_grid_with_boundary(sheets_service, sheet_id: str, tab_id: int, data_rows: int, data_cols: int) -> None:
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

    if current_rows != desired_row_count:
        grid_updates['rowCount'] = desired_row_count
        update_fields.append('gridProperties.rowCount')
    if current_cols != desired_col_count:
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


def initialize_tab(sheets_service, sheet_id: str, tab_id: int, tab_name: str, column_width: int = 1500) -> None:
    ensure_grid_with_boundary(sheets_service, sheet_id, tab_id, data_rows=1, data_cols=1)

    requests = [
        {
            'updateDimensionProperties': {
                'range': {
                    'sheetId': tab_id,
                    'dimension': 'COLUMNS',
                    'startIndex': 0,
                    'endIndex': 1
                },
                'properties': {
                    'pixelSize': column_width
                },
                'fields': 'pixelSize'
            }
        },
        {
            'repeatCell': {
                'range': {
                    'sheetId': tab_id,
                    'startColumnIndex': 0,
                    'endColumnIndex': 1
                },
                'cell': {
                    'userEnteredFormat': {
                        'wrapStrategy': 'WRAP'
                    }
                },
                'fields': 'userEnteredFormat.wrapStrategy'
            }
        }
    ]

    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={'requests': requests}
    ).execute()


def auto_resize_rows(sheets_service, sheet_id: str, tab_id: int, data_rows: int) -> None:
    if data_rows <= 0:
        return

    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={'requests': [{
            'autoResizeDimensions': {
                'dimensions': {
                    'sheetId': tab_id,
                    'dimension': 'ROWS',
                    'startIndex': 0,
                    'endIndex': data_rows
                }
            }
        }]}
    ).execute()


def add_tab(sheets_service, sheet_id: str, tab_name: str) -> int:
    spreadsheet = sheets_service.spreadsheets().get(
        spreadsheetId=sheet_id,
        fields='sheets(properties(sheetId,title))'
    ).execute()

    for sheet in spreadsheet.get('sheets', []):
        if sheet.get('properties', {}).get('title') == tab_name:
            raise RuntimeError(f"Tab '{tab_name}' already exists. Rename or remove it before running this script.")

    result = sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={'requests': [{'addSheet': {'properties': {'title': tab_name}}}]}
    ).execute()

    return result['replies'][0]['addSheet']['properties']['sheetId']


def rename_tab(sheets_service, sheet_id: str, tab_id: int, new_title: str) -> None:
    spreadsheet = sheets_service.spreadsheets().get(
        spreadsheetId=sheet_id,
        fields='sheets(properties(sheetId,title))'
    ).execute()

    for sheet in spreadsheet.get('sheets', []):
        props = sheet.get('properties', {})
        if props.get('sheetId') != tab_id and props.get('title') == new_title:
            raise RuntimeError(f"Tab '{new_title}' already exists. Choose a different name or remove it.")

    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={'requests': [{
            'updateSheetProperties': {
                'properties': {
                    'sheetId': tab_id,
                    'title': new_title
                },
                'fields': 'title'
            }
        }]}
    ).execute()


def create_temp_tab(sheets_service, sheet_id: str) -> Tuple[int, str]:
    temp_title = f"weekly waivers {uuid.uuid4().hex[:8]}"
    tab_id = add_tab(sheets_service, sheet_id, temp_title)
    return tab_id, temp_title


def delete_tab(sheets_service, sheet_id: str, tab_name: str) -> None:
    try:
        spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    except HttpError:
        return

    for sheet in spreadsheet.get('sheets', []):
        props = sheet.get('properties', {})
        if props.get('title') == tab_name:
            try:
                sheets_service.spreadsheets().batchUpdate(
                    spreadsheetId=sheet_id,
                    body={'requests': [{'deleteSheet': {'sheetId': props.get('sheetId')}}]}
                ).execute()
            except HttpError:
                pass
            break

