import json
import os
import re
import html
from datetime import datetime, timezone
from typing import Any, Dict, List, Sequence, Tuple

from googleapiclient.errors import HttpError


def extract_id_from_url(url_or_id: str, *, allow_gid: bool = True) -> str:
    if not ('/' in url_or_id or ':' in url_or_id):
        return url_or_id

    if not allow_gid and '#gid=' in url_or_id:
        raise ValueError('Tab references (#gid=...) are not supported; provide the root Sheets URL.')

    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url_or_id)
    if match:
        return match.group(1)

    match = re.search(r'([a-zA-Z0-9_-]{20,})', url_or_id)
    if match:
        return match.group(1)

    raise ValueError(f'Could not extract a document ID from {url_or_id!r}')


def extract_tab_name_from_doc(first_line: str) -> str:
    match = re.match(r'WEEK\s+(\d+)', first_line, re.IGNORECASE)
    if match:
        week_num = match.group(1)
        return f'W{week_num} waivers'

    match = re.search(r'WEEK\s+(\d+)', first_line, re.IGNORECASE)
    if match:
        week_num = match.group(1)
        return f'W{week_num} waivers'

    return 'weekly waivers'


def transform_player_name(line: str) -> str:
    pattern = r'^(.+?)\s*-\s*(\d+)%\s*(?:to\s*(\d+)%)?$'
    match = re.match(pattern, line.strip())

    if match:
        player_name = match.group(1).strip()
        percent1_num = match.group(2)
        percent2_num = match.group(3)

        if percent2_num:
            return f'{percent1_num}-{percent2_num}% - {player_name}'
        return f'{percent1_num}% - {player_name}'

    return line


def extract_text_from_doc_elements(elements: Sequence[Dict[str, Any]]) -> List[Tuple[str, int]]:
    lines: List[Tuple[str, int]] = []

    def process_element(element: Dict[str, Any]) -> None:
        if 'paragraph' in element:
            para = element['paragraph']
            para_elements = para.get('elements', [])
            bullet = para.get('bullet', {})
            nesting_level = bullet.get('nestingLevel', 0) if bullet else 0

            para_text = ''
            for elem in para_elements:
                if 'textRun' in elem:
                    para_text += elem['textRun'].get('content', '')

            if para_text.strip():
                lines.append((para_text.rstrip(), nesting_level))

        elif 'table' in element:
            table = element['table']
            for row in table.get('tableRows', []):
                row_texts = []
                for cell in row.get('tableCells', []):
                    cell_text = ''
                    for cell_elem in cell.get('content', []):
                        if 'paragraph' in cell_elem:
                            for para_elem_item in cell_elem['paragraph'].get('elements', []):
                                if 'textRun' in para_elem_item:
                                    cell_text += para_elem_item['textRun'].get('content', '')
                    if cell_text.strip():
                        row_texts.append(cell_text.strip())
                if row_texts:
                    lines.append((' | '.join(row_texts), 0))

        for nested in element.get('elements', []):
            process_element(nested)

    for element in elements:
        process_element(element)

    return lines


def read_week_doc(docs_service, doc_id: str) -> Tuple[str, List[str], List[int]]:
    try:
        doc = docs_service.documents().get(documentId=doc_id).execute()
    except HttpError as err:
        raise RuntimeError(
            f"Unable to read Google Doc '{doc_id}'. Status: {err.resp.status}"
        ) from err

    body = doc.get('body', {})
    content = body.get('content', [])

    lines_with_levels = extract_text_from_doc_elements(content)
    lines = [line for line, _ in lines_with_levels]
    nesting_levels = [level for _, level in lines_with_levels]

    first_line = lines[0] if lines else ''

    return first_line, lines, nesting_levels


def _make_segment(text: str, *, bold: bool = False, italic: bool = False, newline: bool = False) -> Dict[str, Any]:
    return {
        'text': text,
        'bold': bool(bold),
        'italic': bool(italic),
        'newline': bool(newline)
    }


def strip_outer_asterisks(text: str) -> str:
    stripped = text.strip()

    while stripped.startswith('*'):
        stripped = stripped[1:].lstrip()

    while stripped.endswith('*'):
        stripped = stripped[:-1].rstrip()

    return stripped


def normalize_note_text(text: str) -> str:
    stripped = strip_outer_asterisks(text)

    if stripped.upper().startswith('NOTE:'):
        rest = stripped[5:].lstrip()
        return f'NOTE: {rest}' if rest else 'NOTE:'

    return stripped


def process_document(lines: List[str], nesting_levels: List[int]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    def add_row(segments: List[Dict[str, Any]]) -> None:
        rows.append({'cells': [{'segments': segments}]})

    i = 0
    in_wr_section = False
    in_player_section = False
    in_drop_section = False
    in_week_section = False
    week_note_segments: List[Dict[str, Any]] = []

    def line_at(idx: int) -> str:
        return lines[idx]

    def normalized(idx: int) -> str:
        return lines[idx].strip()

    while i < len(lines):
        raw_line = line_at(i)
        norm = normalized(i)
        clean_norm = strip_outer_asterisks(norm)
        upper_clean = clean_norm.upper()
        nesting = nesting_levels[i] if i < len(nesting_levels) else 0

        if not norm:
            i += 1
            continue

        is_section_header = bool(re.match(r'^(WEEK \d+|RUNNING BACKS:|WIDE RECEIVERS:|TIGHT ENDS:|QUARTERBACKS:|Drop List)', clean_norm, re.IGNORECASE))

        if re.match(r'^WEEK \d+', clean_norm, re.IGNORECASE):
            in_week_section = True
            in_wr_section = False
            in_player_section = False
            in_drop_section = False
            week_note_segments = []
        elif 'WIDE RECEIVERS' in upper_clean:
            in_wr_section = True
            in_player_section = True
            in_week_section = False
            in_drop_section = False
        elif any(section in upper_clean for section in ['RUNNING BACKS', 'TIGHT ENDS', 'QUARTERBACKS']):
            in_wr_section = False
            in_player_section = True
            in_week_section = False
            in_drop_section = False
        elif 'DROP LIST' in upper_clean:
            in_drop_section = True
            in_player_section = False
            in_wr_section = False
            in_week_section = False
        elif is_section_header:
            in_wr_section = False
            in_player_section = False
            in_drop_section = False
            in_week_section = False

        if in_week_section and (
            clean_norm.startswith('Intro:')
            or clean_norm.upper().startswith('NOTE:')
            or 'these are not concrete' in clean_norm.lower()
            or clean_norm.startswith('THE PERCENT')
        ):
            newline = bool(week_note_segments)
            week_note_segments.append(_make_segment(normalize_note_text(clean_norm), italic=True, newline=newline))
            i += 1
            continue

        is_player = False
        if in_player_section:
            is_player = bool(re.match(r'^[^-]+\s*-\s*\d+%\s*(?:to\s*\d+%)?\s*$', clean_norm))

        if is_player:
            transformed = transform_player_name(clean_norm)
            segments = [_make_segment(transformed, bold=True)]
            i += 1

            while i < len(lines):
                next_norm = normalized(i)
                clean_next = strip_outer_asterisks(next_norm)
                upper_clean_next = clean_next.upper()
                next_raw = line_at(i).rstrip()
                next_nesting = nesting_levels[i] if i < len(nesting_levels) else 0

                if not next_norm:
                    i += 1
                    continue

                if re.match(r'^[^-]+\s*-\s*\d+%\s*(?:to\s*\d+%)?\s*$', clean_next) or re.match(r'^(WEEK \d+|RUNNING BACKS:|WIDE RECEIVERS:|TIGHT ENDS:|QUARTERBACKS:|Drop List)', clean_next, re.IGNORECASE):
                    break

                if upper_clean_next.startswith('NOTE:'):
                    note_text = normalize_note_text(clean_next)
                    segments.append(_make_segment(note_text, italic=True, newline=True))
                    i += 1
                    continue

                lettered_bullet = (next_nesting >= 1) or bool(re.match(r'^[a-zA-Z]+[\.\)]\s+', clean_next))
                if lettered_bullet:
                    cleaned = re.sub(r'^[a-zA-Z0-9]+[\.\)]\s*', '', clean_next)
                    segments.append(_make_segment(f'• {cleaned}', newline=True))
                    i += 1
                    continue

                segments.append(_make_segment(clean_next, newline=True))
                i += 1

            add_row(segments)
            continue

        if clean_norm.upper().startswith('NOTE:') and in_wr_section:
            remainder = normalize_note_text(clean_norm)
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ''
            clean_next_line = normalize_note_text(next_line)
            if 'KEY:' in remainder:
                parts = remainder.split('KEY:', 1)
                note_part = parts[0].strip()
                key_part = 'KEY:' + parts[1].strip() if len(parts) > 1 else 'KEY:'
                segments = []
                if note_part:
                    segments.append(_make_segment(note_part, italic=True))
                segments.append(_make_segment(key_part, italic=True, newline=bool(segments)))
                add_row(segments)
                i += 1
                continue
            elif clean_next_line.upper().startswith('KEY:'):
                segments = [
                    _make_segment(remainder, italic=True),
                    _make_segment(clean_next_line, italic=True, newline=True)
                ]
                add_row(segments)
                i += 2
                continue
            else:
                add_row([_make_segment(remainder, italic=True)])
                i += 1
                continue

        if clean_norm.upper().startswith('NOTE:'):
            note_text = normalize_note_text(clean_norm)
            add_row([_make_segment(note_text, italic=in_wr_section or in_drop_section)])
            i += 1
            continue

        if is_section_header:
            add_row([_make_segment(clean_norm, bold=True)])
            i += 1
            continue

        if clean_norm.startswith('Intro:') or 'these are not concrete' in clean_norm.lower() or clean_norm.startswith('THE PERCENT'):
            add_row([_make_segment(clean_norm, italic=True)])
            i += 1
            continue

        lettered_bullet = (nesting >= 1) or bool(re.match(r'^[a-zA-Z]+[\.\)]\s+', clean_norm))
        if lettered_bullet:
            cleaned = re.sub(r'^[a-zA-Z0-9]+[\.\)]\s*', '', clean_norm)
            add_row([_make_segment(f'• {cleaned}', italic=False)])
            i += 1
            continue

        if in_drop_section:
            add_row([_make_segment(f'• {clean_norm}')])
            i += 1
            continue

        add_row([_make_segment(clean_norm)])
        i += 1

    if week_note_segments:
        rows.insert(1, {'cells': [{'segments': week_note_segments}]})

    return rows


def rows_to_json(metadata: Dict[str, Any], rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        'metadata': {
            **metadata,
            'generated_at': datetime.now(timezone.utc).isoformat()
        },
        'rows': rows
    }


def write_json_report(path: str, metadata: Dict[str, Any], rows: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = rows_to_json(metadata, rows)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def load_rows_from_json(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def render_rows_to_html(metadata: Dict[str, Any], rows: List[Dict[str, Any]]) -> str:
    def escape(text: str) -> str:
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;'))

    def render_segments(segments: List[Dict[str, Any]]) -> str:
        parts: List[str] = []
        for segment in segments:
            if segment.get('newline'):
                parts.append('<br/>')
            text = escape(segment.get('text', ''))
            if segment.get('bold'):
                text = f'<strong>{text}</strong>'
            if segment.get('italic'):
                text = f'<em>{text}</em>'
            parts.append(text)
        return ''.join(parts)

    table_rows: List[str] = []
    for row in rows:
        cells_html: List[str] = []
        for cell in row.get('cells', []):
            cell_html = render_segments(cell.get('segments', []))
            cells_html.append(f'<td>{cell_html}</td>')
        if not cells_html:
            cells_html.append('<td></td>')
        table_rows.append(f"      <tr>{''.join(cells_html)}</tr>")

    table_html = '    <table>\n      <tbody>\n' + '\n'.join(table_rows) + '\n      </tbody>\n    </table>'

    title = escape(metadata.get('tab_name', 'waiver report'))

    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
      body {{
        font-family: Arial, sans-serif;
        line-height: 1.4;
      }}
      table {{
        border-collapse: collapse;
        width: 100%;
      }}
      td {{
        border: 1px solid #ccc;
        padding: 6px;
        vertical-align: top;
        white-space: pre-wrap;
      }}
      h1 {{
        font-size: 1.5rem;
      }}
    </style>
  </head>
  <body>
    <h1>{title}</h1>
{table_html}
  </body>
</html>
"""

