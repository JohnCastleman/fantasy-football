# Display and Output Enhancements - Planning Document

## Goal

Implement settings refactorings, markdown table formatting, and file output capabilities that are prerequisites for CLI parameter support.

## Motivation

These enhancements provide immediate value to the application while also preparing the codebase for CLI parameter overrides. Settings will be clearer and more consistent, output will be more readable (markdown tables), and file output will provide precise control over what gets written to files vs console.

## Implementation Strategy

The work will be implemented in three working sets to respect task dependencies and provide quick wins:

### Working Set 1: Simple Renamings (Tasks 1, 4, 5)

- Rename `displaySize` → `displayMaxPlayers`
- Rename `testRankingTypes` → `rankingType` (array → single enum)
- Rename `testPositions` → `positions`

**Rationale**: Three quick wins with no dependencies between them. All are straightforward renamings that can be tested immediately.

### Working Set 2: New Setting and Defaults (Tasks 3, 6)

- Add `outputFile` setting
- Apply defensive defaults

**Rationale**: Isolates the new setting work. Defensive defaults done first in this set (likely already close to complete). Task 2 deferred to Working Set 3 due to dependency on markdown table output.

### Working Set 3: Output Enhancements (Tasks 7, 8, 2)

- Implement markdown table output format (task 7)
- Implement file output capability (task 8)
- Replace `testOutputTypes` enum with `dump` boolean (task 2)

**Rationale**: Task 2 describes `dump=false` as "markdown table format", so markdown must exist first. While technically we could make task 2 agnostic to output format (it's just enum→boolean conversion), keeping this order:

1. Gets three quick wins in first working set
2. Isolates outputFile work with defensive defaults
3. Collects related output format work together (markdown + file output + format selector)

**Dependency Note**: Task 2 was originally in "Settings Refactoring" phase but moved to Working Set 3 because the boolean's default behavior assumes markdown table format exists.

## Prerequisites Overview

This work consists of three phases:

1. **Settings Refactoring** (Items 1-6): Clean up and improve settings structure
2. **Markdown Table Output** (Item 7): Add markdown formatting for display mode
3. **File Output with Streams** (Item 8): Enable writing to files using Node.js streams

## Settings Refactoring

### 1. Rename `displaySize` to `displayMaxPlayers`

**Current Name**: `displaySize` (vague - "size of what?")
**New Name**: `displayMaxPlayers` (clear - maximum number of players to display)
**Behavior**: `0` or less, `null`, or missing = show all players; any positive number = show that many players, maximum

**Files to Update**:

- `client/settings.js`: Rename setting
- `client/client.js`: Update `displayRankings()` function
- All references in client code

### 2. Replace `testOutputTypes` Enum with `dump` Boolean

**Current**: `testOutputTypes` (enum: DISPLAY, DUMP, ALL)
**New**: `dump` (boolean)
**Behavior**:

- `false`, `null`, or missing = markdown table format
- `true` = TSV (tab-separated values) format
- The "run both modes in one test run" functionality (ALL) is being retired

**Files to Update**:

- `client/tests/settings.js`: Replace `testOutputTypes` with `dump` boolean
- `client/tests/runner.js`: Simplify test logic (remove ALL handling)
- Remove `TestOutputTypeEnum` enum entirely

**Note**: Markdown table formatting implementation is item #7.

### 3. Add `outputFile` Setting

**New Setting**: `outputFile` (string | null)
**Behavior**:

- `null` or missing = output to stdout (console)
- `<filename>` = write output to specified file

**Benefit**: Dedicated file output allows precise control over file contents. Currently, shell redirection (`> file.txt`) captures ALL stdout including logging/debug messages. With `outputFile`, only valid markdown or TSV data goes to the file; logging stays on stdout.

**Output Format Matrix** (2 formats × 2 destinations):

| dump | outputFile | Result |
|------|------------|--------|
| false | null | Markdown table to stdout |
| false | \<file> | Markdown table to file (metadata + table) |
| true | null | TSV to stdout |
| true | \<file> | TSV to file (pure TSV, no metadata) |

**Key Insights**:

- The `outputFile` setting (and later `-o` CLI flag) controls destination (stdout vs file), NOT format
- The `dump` setting (and later `-d` CLI flag) controls format (markdown vs TSV)
- Only valid markdown or TSV will be output to the respective file; logging and status messages remain on stdout
- DUMP mode writes pure TSV to file (no metadata header) for clean spreadsheet import
- DISPLAY mode writes metadata + markdown table to file for complete, readable output

**Files to Update**:

- `client/settings.js`: Add `outputFile` setting (default: `null`)

**Note**: Actual implementation of markdown table format and file output capability are items #7 and #8.

### 4. Rename and Simplify Ranking Type Setting

**Current**: `testRankingTypes` (array of ranking types)
**New**: `rankingType` (single ranking type enum)

**Rationale for name change**: The "test" prefix is redundant - this setting is already in `TestSettings` object

**Rationale**:

- **Pre-season**: ROS/WEEKLY make no sense (not in season); between DRAFT and DYNASTY, you're either one or the other, not both at once
- **In-season**: DRAFT/DYNASTY make almost no sense (occasionally useful for comparison early in season); between ROS and WEEKLY, you sometimes want both, but usually want one THEN the other, not simultaneously
- **Conclusion**: A collection doesn't match typical usage patterns - you typically want ONE ranking type at a time

**Default Behavior**:

- `null` or missing → defensive default is `DRAFT`
- `DRAFT` chosen as defensive default because it has year-round context (ROS/WEEKLY have no context outside the season)

**Files to Update**:

- `client/tests/settings.js`: Rename `testRankingTypes` → `rankingType`, change from array to single enum, set to `RankingTypeEnum.DRAFT`
- `client/tests/runner.js`: Remove array handling, use single value, update to `TestSettings.rankingType`
- All references to `testRankingType` throughout codebase

### 5. Rename Positions Setting

**Current**: `testPositions`
**New**: `positions`

**Rationale**: The "test" prefix is redundant - this setting is already in `TestSettings` object

**Files to Update**:

- `client/tests/settings.js`: Rename `testPositions` → `positions`
- `client/tests/runner.js`: Update to `TestSettings.positions`
- All references to `testPositions` throughout codebase

### 6. Apply Defensive Defaults

**Objective**: Add defensive defaults as "last resort" fallbacks for unexpected situations where settings are missing/null/undefined.

**Defensive Default Behavior** (only applied when setting is missing/null/undefined):

- `verbose`: No defensive default needed - `null`, `false`, or missing → base markdown table (not verbose)
- `displayMaxPlayers`: No defensive default needed - `null`, non-positive, or missing → show all players
- `dump`: No defensive default needed - `null`, `false`, or missing → markdown table format
- `outputFile`: No defensive default needed - `null` or missing → stdout
- `rankingType`: Defensive default is `RankingTypeEnum.DRAFT` (only ranking type with year-round context)
- `positions`: No defensive default needed - `null`, empty array, or missing → all positions

**Implementation**:

```javascript
// Example for client/client.js
const { 
  displayMaxPlayers = Settings.displayMaxPlayers ?? null, 
  verbose = Settings.verbose ?? false,
  outputFile = Settings.outputFile ?? null 
} = options;

// Example for client/tests/runner.js
const rankingType = TestSettings.rankingType ?? RankingTypeEnum.DRAFT;
```

## Markdown Table Output

### 7. Implement Markdown Table Output Format

**Objective**: Add markdown table formatting as the display output format (replacing current plain text).

**Rationale**: Separates the feature implementation from CLI parameter addition. Once this works via settings, the CLI parameter just needs to override settings.

**Files to Update**:

- `client/utils.js`: Add `rankingsMetadataToMarkdownString()` following existing ToString pattern
- `client/utils.js`: Add `playerToMarkdownString()` and `playersToMarkdownTable()` following existing ToString pattern
- `client/client.js`: Update `displayRankings()` to use markdown table format instead of plain text

**Markdown Table Format Examples**:

ROS/DRAFT/DYNASTY (with BYE):

```markdown
| 2025 Standard Rest-of-Season Quarterback Rankings (10/27/2025) |
|------------------------------------------------------------------|

| Rank | Name             | Team | BYE |
|------|------------------|------|-----|
| 1    | Patrick Mahomes  | KC   | 10  |
| 2    | Josh Allen       | BUF  | 12  |
```

WEEKLY (with Opponent):

```markdown
| 2025 Standard Week 8 Quarterback Rankings (10/27/2025) |
|---------------------------------------------------------|

| Rank | Name             | Team | Opponent |
|------|------------------|------|----------|
| 1    | Patrick Mahomes  | KC   | @ DEN    |
| 2    | Josh Allen       | BUF  | vs MIA   |
```

**Implementation Pattern**:

- Metadata formatted as single-column markdown table via `rankingsMetadataToMarkdownString()`
- Player data formatted via `playerToMarkdownString()` - knows whether to show opponent or BYE based on its own fields
- Both metadata and player table included in markdown output
- For TSV dump to file: only pure TSV (no metadata)

## File Output with Streams

### 8. Implement File Output Capability

**Objective**: Add ability to write output to file instead of stdout.

**Rationale**: Separates the feature implementation from CLI parameter addition. Once this works via `Settings.outputFile`, the `-o` parameter just needs to override that setting.

**Key Architectural Decision**: Explicit stdout for data output

Before implementing file output, refactor to use explicit stdout for data payload:

- **Data output (payload)** → `process.stdout.write()` or file
- **Logging/status** → Keep as `console.log()` or `console.info()` (already goes to stdout but semantically clearer)

This ensures clean separation: data payload uses explicit streams, logging uses console methods.

**Files to Update**:

- `client/client.js`: Identify and refactor data payload calls to use `process.stdout.write()`
- `client/client.js`: Review non-data console calls and use `console.log()` vs `console.info()` appropriately
- `client/client.js`: Update `displayRankings()` to check `Settings.outputFile` and write to file if specified
- `client/client.js`: Update `dumpRankingsToTabDelimited()` to check `Settings.outputFile` and write to file if specified

**Implementation Approach**:

Step 1 - Refactor data output to explicit stdout:

```javascript
// Data output (payload) - currently console.log for table/TSV data
process.stdout.write(output + '\n');

// Logging/status - keep as console methods
console.log('Fetching rankings using API param strings...', apiParams);
// or
console.info('Fetching rankings using API param strings...', apiParams);
```

Step 2 - Add file output capability using streams:

```javascript
import { createWriteStream } from 'fs';

// Update function signatures to accept optional output stream
function displayRankings(rankingType, position, outStream = process.stdout) {
  // Stream data writes line-by-line
  outStream.write(rankingsMetadataToMarkdownString(metadata) + '\n');
  outStream.write('| Rank | Name | Team | ... |\n');
  outStream.write('|------|------|------|-----|\n');
  
  for (const player of players) {
    outStream.write(playerToMarkdownString(player) + '\n');
  }
}

function dumpRankingsToTabDelimited(rankingType, position, outStream = process.stdout) {
  // Stream TSV line-by-line
  outStream.write(tabDelimitedHeader + '\n');
  
  for (const player of players) {
    outStream.write(playerToTabDelimitedString(player) + '\n');
  }
}

// Call site handles stream creation/cleanup:
if (Settings.outputFile) {
  const outStream = createWriteStream(Settings.outputFile);
  displayRankings(rankingType, position, outStream);
  outStream.end();
  console.info(`Output written to: ${Settings.outputFile}`);
} else {
  displayRankings(rankingType, position);  // Defaults to stdout
}
```

**Benefits of stream-based approach**:

- Scales well for large outputs (thousands of lines)
- Standard Node.js pattern (dependency injection)
- Functions don't depend on Settings
- Default parameter makes stdout usage clean and simple

**Output Matrix** (2 formats × 2 destinations = 4 combinations):

| dump | outputFile | Result |
|------|------------|--------|
| false | null | Markdown table to stdout |
| false | \<file> | Markdown table to file |
| true | null | TSV to stdout |
| true | \<file> | TSV to file |

## Final Settings State

After completing all items, settings will be:

### Client Settings (`client/settings.js`)

- `verbose` (boolean): Whether to show detailed ranking metadata - **default**: `false`
- `displayMaxPlayers` (number|null): Maximum number of players to display - **default**: `null` (show all)
- `outputFile` (string|null): Output file path - **default**: `null` (stdout)

### Test Settings (`client/tests/settings.js`)

- `dump` (boolean): Whether to use TSV format - **default**: `false` (use markdown table format)
- `rankingType` (enum): Which ranking type to test - **default**: `RankingTypeEnum.DRAFT`
  - Valid values: `ROS`, `WEEKLY`, `DYNASTY`, `DRAFT`
  - `null` or missing → defensive default is `DRAFT`
- `positions` (array|null): Which positions to test - **default**: `null` (all positions)
  - Can be array of `PositionEnum` values: `QB`, `RB`, `WR`, `TE`, `K`, `DST`

## Testing Strategy

- Test each settings refactoring individually (items 1-6)
- Test markdown table output for all ranking types and positions (item 7)
- Test file output for both markdown and TSV formats (item 8)
- Verify all combinations in the output matrix work correctly

## Next Steps

After completing these prerequisites:

- Move to CLI Parameter Overrides implementation (see `cli-parameter-overrides.md`)
- CLI parameters will simply override these settings via commander.js

## Status

**Planning Complete** - Ready for implementation.
