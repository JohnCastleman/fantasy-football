# Flock Fantasy Rankings Integration - Planning Document

## Status

**Phase 1: COMPLETE** - Paste-based workflow fully implemented and working.
**Phase 2: PENDING** - Automate TSV input data gathering (details below).

## What's Implemented (Phase 1)

Tool suite processes Flock Fantasy rankings from paste input → TSV → Google Sheets.

### Tools

- `flock-rankings-to-tsv.py` - Converts raw rankings (with tier markers) to TSV, invokes `npm run --silent remove-tiers`, supports stdin piping, `--html` flag
- `flock-rankings-tsv-to-google-sheets.py` - Writes TSV to Google Sheets, supports stdin piping, `--mock` flag for testing, `--reset` flag for tab initialization
- `generate-mock-data.ps1` - Helper script for mock data generation

**Note**: The `--html` flag is implemented and tested in `flock-rankings-to-tsv.py` (generates HTML table preview from TSV, writes to file with inferred filename).

### Sheet Integration

- ROS data: Tab "Flock ROS raw data", Column L (12), Row 3 (headers row 2, stats merged cell row 1)
- WEEKLY data: Tab "Flock weekly raw data", position-specific columns (QB: G3, RB: X3, WR: AN3, TE: AY3)
- Dynamic column inference, automatic tab creation/clearing, numeric type handling, auto-sizing

### Workflow

```bash
# Paste rankings → TSV → Sheets (can pipe between scripts)
@"raw rankings..."@ | python tools/flock-rankings/flock-rankings-to-tsv.py --type ROS | python tools/flock-rankings/flock-rankings-tsv-to-google-sheets.py --type ROS
```

## Pending: Automate TSV Input Data Gathering (Phase 2)

**Goal**: Automate gathering TSV input data for `flock-rankings-to-tsv.py` and `flock-rankings-tsv-to-google-sheets.py` scripts, eliminating the manual paste step.

Two approaches are planned:

- **Approach 1**: Replaces manual data scraping and pasting using existing `npm run remove-tiers` and `flock-rankings-to-tsv.py` scripts
- **Approach 2**: More complete approach that replaces all of these with a client/server implementation similar to the existing FantasyPros API pattern

### Approach 1: Playwright Web Scraping (Short Term)

**Approach**: Use Playwright to automate browser interaction with Flock Fantasy rankings page. New script: `scrape-flock-rankings.py`

#### URLs

- ROS: `https://flockfantasy.com/rankings?format=year` (select "Overall" position, "Mason Dodd" creator)
- WEEKLY: `https://flockfantasy.com/rankings?format=WEEKLY` (select position QB/RB/WR/TE, "Mason Dodd" creator)

#### Features

- Hardcoded creator: "Mason Dodd" (no CLI param)
- ROS: Hardcoded position "Overall" (no CLI param)
- WEEKLY: Requires `--position` CLI param (QB, RB, WR, or TE)
- Navigate to page, select creator and position, extract rankings text
- Pipe output through `flock-rankings-to-tsv.py` (or invoke remove-tiers internally)
- Output: TSV file (compatible with existing `flock-rankings-tsv-to-google-sheets.py` workflow)

#### CLI Arguments

```bash
--type ROS|WEEKLY          # Required, case-insensitive
--position QB|RB|WR|TE      # Required for WEEKLY, ignored for ROS
--week <number>             # Optional, for output filename generation
--output <file>             # Optional TSV output file (default: stdout for piping)
```

#### Usage

```bash
# ROS Overall
python tools/flock-rankings/scrape-flock-rankings.py \
  --type ROS \
  --week 15 \
  --output Flock-ROS(W15).tsv

# WEEKLY QB (run 4 times for all positions)
python tools/flock-rankings/scrape-flock-rankings.py \
  --type WEEKLY \
  --position QB \
  --week 15 \
  --output Flock-W15-QB.tsv

# Pipe directly to sheets script
python tools/flock-rankings/scrape-flock-rankings.py --type ROS --week 15 | \
  python tools/flock-rankings/flock-rankings-tsv-to-google-sheets.py --type ROS
```

#### Approach 1: Implementation Notes

- Follow Unix philosophy: single-responsibility tool that chains with existing scripts
- Research Flock Fantasy page structure (selectors, form elements, timing requirements)
- Handle page load wait times, dynamic content loading
- Extract rankings text from DOM (likely need to identify the rankings container element)
- Output format should match what manual paste produces (8 lines per player before remove-tiers)

#### Dependencies

- `playwright` - Install via `pip install playwright` + `playwright install` for browsers

### Approach 2: Client/Server Integration (Long Term)

**Approach**: Integrate Flock Fantasy API calls into the existing client/server architecture (similar to FantasyPros pattern), replacing remove-tiers.js, flock-rankings-to-tsv.py, and scrape-flock-rankings.py.

#### Overview

Similar to the kdst-rankings toolkit, dump scripts that output TSV format (currently passthrough wrappers, to be extended with client/server architecture):

- `dump-ros.py` - ROS rankings dump (passthrough wrapper, calls `flock-rankings-to-tsv.py --type ROS`)
- `dump-weekly-qb.py` - Weekly QB rankings dump (passthrough wrapper, calls `flock-rankings-to-tsv.py --type WEEKLY --position QB`)
- `dump-weekly-rb.py` - Weekly RB rankings dump (passthrough wrapper, calls `flock-rankings-to-tsv.py --type WEEKLY --position RB`)
- `dump-weekly-wr.py` - Weekly WR rankings dump (passthrough wrapper, calls `flock-rankings-to-tsv.py --type WEEKLY --position WR`)
- `dump-weekly-te.py` - Weekly TE rankings dump (passthrough wrapper, calls `flock-rankings-to-tsv.py --type WEEKLY --position TE`)

#### Current Implementation

The dump scripts are currently simple passthrough wrappers that call `flock-rankings-to-tsv.py` with the appropriate `--type` and `--position` arguments. They accept the same CLI arguments (`--input`, `--output`, `--week`, `--html`) and support stdin/stdout piping, making them drop-in replacements for manual `flock-rankings-to-tsv.py` calls.

#### Future Enhancement

**Goal**: Replace passthrough wrappers with client/server implementation that fetches data directly from Flock Fantasy APIs, similar to kdst-rankings toolkit pattern. When implemented, these would likely become `.js` scripts (like kdst's `dump-*.js`) since they'd call client JS scripts rather than process raw input.

#### Benefits (when fully implemented)

- Bypasses `scrape-flock-rankings.py` (web scraping no longer needed)
- Bypasses `flock-rankings-to-tsv.py` (dumps output TSV directly, compatible with `flock-rankings-tsv-to-google-sheets.py`)
- Consistent architecture with FantasyPros and kdst tools
- Direct API access (more reliable than scraping)
- Follows existing patterns in the codebase

#### Approach 2: Implementation Notes

- Research Flock Fantasy API endpoints and authentication requirements
- Extend client/server architecture to support Flock Fantasy as additional data source
- Replace passthrough wrappers with client/server calls following kdst-rankings pattern
- Output format: TSV (compatible with existing `flock-rankings-tsv-to-google-sheets.py` workflow)
