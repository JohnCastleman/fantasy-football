import argparse
from pathlib import Path

from lib.file_utils import ensure_unique_path
from lib.waiver_processing import load_rows_from_json, render_rows_to_html

ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_REPORT_DIR = ROOT_DIR / 'docs' / 'waiver-reports'


def parse_args():
    parser = argparse.ArgumentParser(
        description='Render a waiver JSON report as HTML'
    )
    parser.add_argument('json_path', help='Path to JSON report produced by ron-stewart-weekly-waiver-report-to-json.py')
    parser.add_argument('--output', help='Optional output HTML path (defaults to docs/waiver-reports/<tab name>.html)')
    return parser.parse_args()


def main():
    args = parse_args()

    json_path = Path(args.json_path)
    if not json_path.exists():
        print(f"Error: JSON file '{json_path}' does not exist.")
        raise SystemExit(1)

    payload = load_rows_from_json(str(json_path))
    metadata = payload.get('metadata', {})
    rows = payload.get('rows', [])

    if not rows:
        print('Error: No rows found in JSON payload.')
        raise SystemExit(1)

    tab_name = metadata.get('tab_name', 'weekly waivers')

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.exists():
            print(f"Error: Output file '{output_path}' already exists. Delete it or specify another path.")
            raise SystemExit(1)
    else:
        output_dir = DEFAULT_REPORT_DIR
        output_dir.mkdir(parents=True, exist_ok=True)
        suggested_name = f"{tab_name}.html" if tab_name else 'weekly waivers.html'
        output_path = ensure_unique_path(output_dir / suggested_name)

    html_document = render_rows_to_html(metadata, rows)
    output_path.write_text(html_document, encoding='utf-8')
    print(f'HTML report written to {output_path.resolve()}')


if __name__ == '__main__':
    main()

