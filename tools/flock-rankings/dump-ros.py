#!/usr/bin/env python3
"""
ABOUTME: Passthrough wrapper for Flock Fantasy ROS rankings dump.
ABOUTME: Calls flock-rankings-to-tsv.py with --type ROS, accepts same CLI arguments.
"""

import subprocess
import sys
from pathlib import Path


def main():
    script_dir = Path(__file__).parent
    to_tsv_script = script_dir / 'flock-rankings-to-tsv.py'
    
    # Build command: always include --type ROS
    cmd = [sys.executable, str(to_tsv_script), '--type', 'ROS']
    
    # Passthrough arguments (--input, --output, --week, --html)
    for arg in sys.argv[1:]:
        cmd.append(arg)
    
    # Run the script, passing stdin/stdout through (inherits by default, but explicit for clarity)
    result = subprocess.run(cmd, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    sys.exit(result.returncode)


if __name__ == '__main__':
    main()
