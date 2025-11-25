import argparse
import importlib.util
import sys
import uuid
from pathlib import Path

# Determine paths
SCRIPT_DIR = Path(__file__).resolve().parent
TOOLS_DIR = SCRIPT_DIR.parent
ROOT_DIR = TOOLS_DIR.parent

# Add script directory to sys.path for local lib imports
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from googleapiclient.discovery import build
except ModuleNotFoundError as err:
    print('Error: google-api-python-client is not installed.')
    print('Run "pip install google-api-python-client google-auth-oauthlib google-auth"')
    raise SystemExit(1) from err

# Import shared google_auth_utils from tools/lib/ using importlib
# (avoiding conflict with local lib package)
SHARED_AUTH_PATH = TOOLS_DIR / 'lib' / 'google_auth_utils.py'
spec = importlib.util.spec_from_file_location('shared_google_auth_utils', SHARED_AUTH_PATH)
shared_google_auth = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared_google_auth)
get_credentials = shared_google_auth.get_credentials

# Import from local lib (tools/waiver-report/lib/)
from lib.waiver_processing import (
    extract_id_from_url,
    extract_tab_name_from_doc,
    process_document,
    read_week_doc,
    write_json_report,
    render_rows_to_html,
)
from lib.file_utils import ensure_unique_path

DEFAULT_REPORT_DIR = ROOT_DIR / 'docs' / 'waiver-reports'


def parse_args():
    parser = argparse.ArgumentParser(
        description='Fetch Ron Stewart weekly waiver report and serialize it to JSON (optionally HTML)'
    )
    parser.add_argument('source_doc', help='Google Docs document ID or full URL')
    parser.add_argument(
        '--output',
        help='Optional path for the generated JSON file (defaults to docs/waiver-reports/<tab name>.json)'
    )
    parser.add_argument(
        '--html',
        action='store_true',
        help='Also emit an HTML preview alongside the JSON payload'
    )
    parser.add_argument(
        '--html-output',
        help='Optional explicit path for the HTML file (only used when --html is set)'
    )
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        doc_id = extract_id_from_url(args.source_doc)
    except ValueError as err:
        print(f'Error: {err}')
        raise SystemExit(1)

    creds = get_credentials(['https://www.googleapis.com/auth/documents.readonly'])
    docs_service = build('docs', 'v1', credentials=creds)

    print(f'Reading Google Doc {doc_id} ...')
    first_line, lines, nesting_levels = read_week_doc(docs_service, doc_id)
    tab_name = extract_tab_name_from_doc(first_line)
    print(f'Detected tab name: {tab_name}')

    rows = process_document(lines, nesting_levels)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.exists():
            print(f"Error: Output file '{output_path}' already exists. Delete it or specify another path.")
            raise SystemExit(1)
    else:
        default_dir = DEFAULT_REPORT_DIR
        default_dir.mkdir(parents=True, exist_ok=True)
        suggested_name = f"{tab_name}.json" if tab_name else 'weekly waivers.json'
        output_path = ensure_unique_path(default_dir / suggested_name)

    temp_path = output_path.with_name(f"weekly waivers {uuid.uuid4().hex[:8]}.json")

    metadata = {
        'tab_name': tab_name,
        'source_doc_id': doc_id,
    }

    write_json_report(str(temp_path), metadata, rows)

    try:
        temp_path.replace(output_path)
    except OSError as err:
        print(f"Error renaming '{temp_path}' to '{output_path}': {err}")
        raise SystemExit(1)

    print(f'JSON report written to {output_path.resolve()}')

    if args.html:
        if args.html_output:
            html_path = Path(args.html_output)
            html_path.parent.mkdir(parents=True, exist_ok=True)
            if html_path.exists():
                print(f"Error: HTML output file '{html_path}' already exists. Delete it or specify another path.")
                raise SystemExit(1)
        else:
            html_dir = output_path.parent
            html_name = output_path.stem + '.html'
            html_path = ensure_unique_path(html_dir / html_name)

        html_content = render_rows_to_html(metadata, rows)
        html_path.write_text(html_content, encoding='utf-8')
        print(f'HTML preview written to {html_path.resolve()}')


if __name__ == '__main__':
    main()

