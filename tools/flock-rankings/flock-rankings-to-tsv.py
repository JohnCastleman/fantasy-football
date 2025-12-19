"""Convert Flock Fantasy rankings (8 lines per player) to TSV.

Invokes remove-tiers tool and outputs TSV with only columns needed by target sheet.
NOTE: Column selection will be finalized after sheet structure exploration.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

def invoke_remove_tiers(input_content: str) -> str:
    """Invoke remove-tiers script on input content."""
    try:
        # Use npm run to invoke remove-tiers script (defined in package.json)
        # On Windows, npm is npm.cmd, so use shell=True for cross-platform compatibility
        # Use --silent to suppress npm's own output messages, only capture script output
        repo_root = Path(__file__).resolve().parent.parent.parent
        result = subprocess.run(
            'npm run --silent remove-tiers',
            input=input_content,
            capture_output=True,
            text=True,
            encoding='utf-8',
            shell=True,
            cwd=repo_root  # Run from repo root so npm can find package.json
        )
        if result.returncode != 0:
            print(f"Error running remove-tiers: {result.stderr}", file=sys.stderr)
            sys.exit(1)
        return result.stdout
    except Exception as e:
        print(f"Error invoking remove-tiers: {e}", file=sys.stderr)
        sys.exit(1)


def infer_column_count(lines: List[str]) -> int:
    """Infer column count by detecting first two player starts.
    
    Players start with lines matching pattern: digit(s), period, spaces, then letters (rank number, period, spaces, then name).
    The distance between first and second player start is the column count.
    """
    first_player_start = None
    second_player_start = None
    
    for i, line in enumerate(lines):
        if re.match(r'^\d+\.\s+[A-Za-z]', line):
            if first_player_start is None:
                first_player_start = i
            elif second_player_start is None:
                second_player_start = i
                break
    
    if first_player_start is not None and second_player_start is not None:
        return second_player_start - first_player_start
    
    # Fallback: assume 8 columns if we can't detect
    return 8


def parse_rankings_to_tsv(cleaned_content: str, columns_needed: list, ranking_type: str, position: Optional[str] = None) -> str:
    """Parse cleaned rankings format to TSV with specified columns.
    
    Args:
        cleaned_content: Output from remove-tiers tool
        columns_needed: List of column names to include
        ranking_type: 'ROS' or 'WEEKLY'
        position: Position for WEEKLY rankings (QB, RB, WR, TE)
    """
    lines = [line.strip() for line in cleaned_content.strip().split('\n') if line.strip()]
    
    # Infer column count dynamically
    col_count = infer_column_count(lines)
    
    # Parse players
    players = []
    i = 0
    
    if ranking_type == 'ROS':
        # ROS: Use first 8 columns (even if more exist)
        # Columns: overallrank+name, position+posrank, team, gamesplayed(FILTER), snap%, fppergame, posrank, overallrank
        while i < len(lines):
            if i + col_count - 1 < len(lines):
                # Column 1: overallrank+name (e.g., "1. Jahmyr Gibbs")
                rank_name = lines[i] if i < len(lines) else ''
                
                # Column 2: position+posrank (e.g., "RB1")
                pos_rank = lines[i + 1] if i + 1 < len(lines) else ''
                
                # Column 3: team
                team = lines[i + 2] if i + 2 < len(lines) else ''
                
                # Column 4: gamesplayed - FILTER OUT (skip, use col 5 for snap%)
                
                # Column 5: snap%
                snap_pct = lines[i + 4] if i + 4 < len(lines) else ''
                
                # Column 6: fppergame
                fppergame = lines[i + 5] if i + 5 < len(lines) else ''
                
                # Column 7: posrank
                pos_rank_stat = lines[i + 6] if i + 6 < len(lines) else ''
                
                # Column 8: overallrank
                overall_rank = lines[i + 7] if i + 7 < len(lines) else ''
                
                # Keep all values as strings for TSV (conversion to numbers happens when writing to Google Sheets)
                players.append({
                    'rank + name': rank_name,
                    'pos + rk': pos_rank,
                    'tm': team,
                    'snap%': snap_pct,
                    'PPR FPs': fppergame,
                    'FPs pos rk': pos_rank_stat,
                    'FPs rk': overall_rank
                })
                i += col_count
            else:
                break
    else:  # WEEKLY
        # WEEKLY: Infer column count dynamically, only take first 2 columns (posrank+name, opponent)
        if not position:
            raise ValueError("Position required for WEEKLY rankings")
        
        # col_count already inferred above
        while i < len(lines):
            if i + col_count - 1 < len(lines):
                # Column 1: posrank+name
                rank_name = lines[i] if i < len(lines) else ''
                
                # Column 2: opponent
                opponent = lines[i + 1] if i + 1 < len(lines) else ''
                
                # Ignore the rest (columns 3 through col_count)
                players.append({
                    'rank + name': rank_name,
                    'opp': opponent
                })
                
                i += col_count
            else:
                break
    
    # Build TSV with only needed columns
    tsv_lines = []
    tsv_lines.append('\t'.join(columns_needed))
    
    for player in players:
        row = []
        for col in columns_needed:
            value = player.get(col, '')
            # Convert to string for TSV (numbers will be converted back to numbers when writing to sheet)
            row.append(str(value) if value != '' else '')
        tsv_lines.append('\t'.join(row))
    
    return '\n'.join(tsv_lines)


def generate_html(tsv_content: str) -> str:
    """Generate HTML preview from TSV."""
    lines = tsv_content.strip().split('\n')
    if not lines:
        return '<html><body>No data</body></html>'
    
    headers = lines[0].split('\t')
    rows = [line.split('\t') for line in lines[1:]]
    
    html = ['<html><head><style>table { border-collapse: collapse; } th, td { border: 1px solid #ddd; padding: 8px; } th { background-color: #f2f2f2; }</style></head><body>']
    html.append('<table>')
    html.append('<thead><tr>')
    for header in headers:
        html.append(f'<th>{header}</th>')
    html.append('</tr></thead>')
    html.append('<tbody>')
    for row in rows:
        html.append('<tr>')
        for cell in row:
            html.append(f'<td>{cell}</td>')
        html.append('</tr>')
    html.append('</tbody></table>')
    html.append('</body></html>')
    
    return '\n'.join(html)


def main():
    parser = argparse.ArgumentParser(description='Convert Flock Fantasy rankings to TSV (invokes remove-tiers)')
    parser.add_argument('--input', '-i', type=Path, help='Input file (raw rankings, before remove-tiers; default: read from stdin)')
    parser.add_argument('--output', '-o', type=Path, help='Output TSV file (default: write TSV to stdout)')
    parser.add_argument('--type', type=str.upper, choices=['ROS', 'WEEKLY'], required=True, help='Ranking type (case-insensitive)')
    parser.add_argument('--position', type=str.upper, choices=['QB', 'RB', 'WR', 'TE'], help='Position (required for WEEKLY, case-insensitive)')
    parser.add_argument('--week', type=int, help='Week number (required for WEEKLY, optional for ROS; used for HTML filename inference)')
    parser.add_argument('--html', action='store_true', help='Also write HTML file to docs/flock-rankings/ with inferred filename (in addition to TSV output)')
    args = parser.parse_args()
    
    if args.type == 'WEEKLY':
        if not args.position:
            parser.error("--position is required for WEEKLY type")
        if not args.week:
            parser.error("--week is required for WEEKLY type")
    
    # Warn if --position provided for ROS (not needed, but harmless)
    if args.type == 'ROS':
        if args.position:
            print(f"Warning: --position is not needed for ROS rankings (ignoring position {args.position})", file=sys.stderr)
    
    # Read input (from file or stdin)
    if args.input:
        input_content = args.input.read_text(encoding='utf-8')
    else:
        input_content = sys.stdin.read()
    
    # Invoke remove-tiers
    cleaned_content = invoke_remove_tiers(input_content)
    
    # Columns needed based on actual sheet structure:
    # ROS: 8 input columns, filter out gamesplayed (4th), output 7 columns
    # WEEKLY: Position-specific input, only take first 2 columns (rankname, opponent)
    if args.type == 'ROS':
        columns_needed = ['rank + name', 'pos + rk', 'tm', 'snap%', 'PPR FPs', 'FPs pos rk', 'FPs rk']
    else:  # WEEKLY
        columns_needed = ['rank + name', 'opp']
    
    # Generate TSV
    # Note: position is only used/read during WEEKLY processing (ignored for ROS to keep things flowing)
    tsv_content = parse_rankings_to_tsv(cleaned_content, columns_needed, args.type, args.position if args.type == 'WEEKLY' else None)
    
    # Determine default output directory (same as waiver tool: docs/flock-rankings/)
    repo_root = Path(__file__).resolve().parent.parent.parent
    default_output_dir = repo_root / 'docs' / 'flock-rankings'
    
    # Write TSV (to file if --output provided, otherwise to stdout for piping)
    if args.output:
        args.output.write_text(tsv_content, encoding='utf-8')
        print(f"Wrote TSV to {args.output}", file=sys.stderr)
    else:
        # Always write TSV to stdout for piping
        sys.stdout.write(tsv_content)
        if not tsv_content.endswith('\n'):
            sys.stdout.write('\n')
    
    # If --html is set, also write HTML to inferred filename
    if args.html:
        if args.output:
            # Level 1: Infer HTML filename from --output path (same path, .html extension)
            html_path = args.output.with_suffix('.html')
            html_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            # Level 2: Use default output directory and infer filename from pattern
            default_output_dir.mkdir(parents=True, exist_ok=True)
            if args.type == 'ROS':
                if args.week:
                    html_filename = f'flock-ROS(W{args.week}).html'
                else:
                    html_filename = 'flock-ROS.html'
            else:  # WEEKLY
                html_filename = f'flock-W{args.week}-{args.position}.html'
            html_path = default_output_dir / html_filename
        
        html_content = generate_html(tsv_content)
        html_path.write_text(html_content, encoding='utf-8')
        print(f'Wrote HTML to {html_path.resolve()}', file=sys.stderr)


if __name__ == '__main__':
    main()





