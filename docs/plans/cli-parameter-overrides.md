# CLI Parameter Overrides - Planning Document

## CLI Framework Reference

This implementation will use **commander.js** for command-line parsing and option handling:

- **NPM Package**: [commander](https://www.npmjs.com/package/commander)
- **GitHub Repository**: <https://github.com/tj/commander.js>
- **Documentation**: <https://github.com/tj/commander.js#readme>

Commander.js provides:

- POSIX-style option flags (`-v`, `--verbose`, `-h`, `--help`)
- Negatable boolean options (`--no-verbose`)
- Mutually exclusive options via `.conflicts()` method
- Type coercion and validation
- Automatic help and version generation
- Standard CLI conventions
- Well-tested, widely-used framework (40M+ weekly downloads)

## Goal

Implement command-line parameter overrides for client settings to enable flexible testing and investigative work without modifying and saving settings files.

## Motivation

Currently, investigating features like player ownership integration requires manually modifying `client/settings.js` and `client/tests/settings.js`, saving those changes, and then reverting them later. This is tedious and error-prone. Command-line parameter overrides will allow temporary configuration changes without touching the settings files.

## Prerequisites / Pre-Work

Before implementing CLI parameter overrides, the following cleanups and refactorings are needed:

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
- **Update existing display output to use markdown table syntax**

### 3. Add `outputFile` Setting

**New Setting**: `outputFile` (string | null)
**Behavior**:

- `null` or missing = output to stdout (console)
- `<filename>` = write output to specified file

**Output Format Matrix** (simplified to 2 formats × 2 destinations):

| dump | outputFile | Result |
|------|------------|--------|
| false | null | Markdown table to stdout |
| false | \<file> | Markdown table to file |
| true | null | TSV to stdout |
| true | \<file> | TSV to file |

**Key Insight**: The `-o` flag controls destination (stdout vs file), NOT format. The `dump` flag controls format (markdown vs TSV).

**Files to Update**:

- `client/settings.js`: Add `outputFile` setting (default: `null`)
- `client/client.js`: Convert existing display output to markdown table format, add file output support
- `client/dump.js`: Add file output support (or merge into unified output handler)

**Markdown Table Format Examples**:

ROS/DRAFT/DYNASTY (with BYE):

```markdown
| Rank | Name             | Team | BYE |
|------|------------------|------|-----|
| 1    | Patrick Mahomes  | KC   | 10  |
| 2    | Josh Allen       | BUF  | 12  |
```

WEEKLY (with Opponent):

```markdown
| Rank | Name             | Team | Opponent |
|------|------------------|------|----------|
| 1    | Patrick Mahomes  | KC   | @ DEN    |
| 2    | Josh Allen       | BUF  | vs MIA   |
```

### 4. Change `testRankingTypes` Array to `testRankingType` Single Enum

**Current**: `testRankingTypes` (array of ranking types)
**New**: `testRankingType` (single ranking type enum)

**Rationale**:

- **Pre-season**: ROS/WEEKLY make no sense (not in season); between DRAFT and DYNASTY, you're either one or the other, not both at once
- **In-season**: DRAFT/DYNASTY make almost no sense (occasionally useful for comparison early in season); between ROS and WEEKLY, you sometimes want both, but usually want one THEN the other, not simultaneously
- **Conclusion**: A collection doesn't match typical usage patterns - you typically want ONE ranking type at a time

**Default Behavior**:

- `null` or missing → defensive default is `DRAFT`
- `DRAFT` chosen as defensive default because it has year-round context (ROS/WEEKLY have no context outside the season)

**Files to Update**:

- `client/tests/settings.js`: Change `testRankingTypes` (array) to `testRankingType` (single enum), set to `RankingTypeEnum.DRAFT`
- `client/tests/runner.js`: Remove array handling, use single value

### 5. Apply Defensive Defaults

**Objective**: Add defensive defaults as "last resort" fallbacks for unexpected situations where settings are missing/null/undefined.

**Defensive Default Behavior** (only applied when setting is missing/null/undefined):

- `verbose`: No defensive default needed - `null`, `false`, or missing → base markdown table (not verbose)
- `displayMaxPlayers`: No defensive default needed - `null`, non-positive, or missing → show all players
- `dump`: No defensive default needed - `null`, `false`, or missing → markdown table format
- `outputFile`: No defensive default needed - `null` or missing → stdout
- `testRankingType`: Defensive default is `RankingTypeEnum.DRAFT` (only ranking type with year-round context)
- `testPositions`: No defensive default needed - `null`, empty array, or missing → all positions

**Implementation**:

```javascript
// Example for client/client.js
const { 
  displayMaxPlayers = Settings.displayMaxPlayers ?? null, 
  verbose = Settings.verbose ?? false,
  outputFile = Settings.outputFile ?? null 
} = options;

// Example for client/tests/runner.js
const rankingType = TestSettings.testRankingType ?? RankingTypeEnum.DRAFT;
```

## Current Settings (After Pre-Work)

### Client Settings (`client/settings.js`)

- `verbose` (boolean): Whether to show detailed ranking metadata - **default**: `false`
- `displayMaxPlayers` (number|null): Maximum number of players to display - **default**: `null` (show all)
- `outputFile` (string|null): Output file path - **default**: `null` (stdout)

### Test Settings (`client/tests/settings.js`)

- `dump` (boolean): Whether to use TSV format - **default**: `false` (use markdown table format)
- `testRankingType` (enum): Which ranking type to test - **default**: `RankingTypeEnum.DRAFT`
  - Valid values: `ROS`, `WEEKLY`, `DYNASTY`, `DRAFT`
  - `null` or missing → defensive default is `DRAFT`
- `testPositions` (array|null): Which positions to test - **default**: `null` (all positions)
  - Can be array of `PositionEnum` values: `QB`, `RB`, `WR`, `TE`, `K`, `DST`

## CLI Parameter Design

### Short Option Codes (Final)

Following POSIX standards and CLI best practices:

| Short | Long | Type | Purpose |
|-------|------|------|---------|
| `-h` | `--help` | flag | Display help information |
| `-V` | `--version` | flag | Display version number |
| `-v` | `--verbose` | boolean | Enable verbose output |
| `-d` | `--dump` | boolean | Enable TSV output format |
| `-o` | `--output` | string | Output file path |
| `-t` | `--type` | enum | Ranking type (DRAFT\|DYNASTY\|ROS\|WEEKLY) |
| `-p` | `--position` | string | Position (repeatable: `-p QB -p RB`) |
| `-m` | `--max-players` | number | Maximum players to display |

**Notes**:

- Case-distinct `-V` (version) vs `-v` (verbose) follows standard CLI conventions (git, npm, node)
- `-m` chosen for max-players (mnemonic: "max")
- `-o` is the universal standard for output files
- Commander.js distinguishes case even on Windows

### Priority Levels

**CLI Parameters override Settings Files**:

1. **CLI Parameter Value** (highest priority): Explicitly provided on command line
2. **Settings File Value** (middle priority): Configured in `client/settings.js` or `client/tests/settings.js`
3. **Built-in Default** (lowest priority): Hardcoded fallback when setting is missing/null

**Standard Override Behavior**:

- Omit CLI param → use Settings file value
- Provide CLI param → override Settings file value
- Use `--no-<flag>` → explicitly set boolean to false

## CLI Parameters

### `-h, --help`

**Type**: Flag (boolean)

**Behavior**:

- Displays comprehensive help information
- Auto-generated by commander.js
- Includes command description, option list, usage examples
- Exits after displaying help

**Usage**:

```bash
npm test -- --help
npm test -- -h
```

### `-V, --version`

**Type**: Flag (boolean)

**Behavior**:

- Displays version number from package.json
- Auto-generated by commander.js
- Exits after displaying version

**Usage**:

```bash
npm test -- --version
npm test -- -V
```

### `-v, --verbose, --no-verbose`

**Type**: Boolean (negatable)

**Values**:

- `-v` or `--verbose`: Enable verbose output (detailed ranking metadata)
- `--no-verbose`: Explicitly disable verbose output
- Omit: Use Settings file value

**Overrides**: `Settings.verbose`

**Usage**:

```bash
npm test -- --verbose          # Enable
npm test -- -v                 # Enable (short)
npm test -- --no-verbose       # Explicitly disable
```

### `-m, --max-players <number>`

**Type**: Integer

**Values**:

- `-m 5` or `--max-players 5`: Show maximum of 5 players
- `-m 0` or `--max-players 0`: Show all players
- Omit: Use Settings file value (default: null = all players)

**Overrides**: `Settings.displayMaxPlayers`

**Usage**:

```bash
npm test -- --max-players 10
npm test -- -m 5
npm test -- -m 0               # Show all
```

### `-d, --dump, --no-dump`

**Type**: Boolean (negatable)

**Values**:

- `-d` or `--dump`: Enable TSV output format
- `--no-dump`: Explicitly use markdown table format
- Omit: Use TestSettings file value (default: markdown table)

**Overrides**: `TestSettings.dump`

**Usage**:

```bash
npm test -- --dump             # TSV format
npm test -- -d                 # TSV format (short)
npm test -- --no-dump          # Markdown table format
```

### `-o, --output <file>`

**Type**: String (filename)

**Values**:

- `-o rankings.txt` or `--output rankings.txt`: Write output to file
- Omit: Output to stdout

**Behavior**:

- `-o` controls **destination** (stdout vs file), NOT format
- Format is controlled by `dump` flag:
  - `dump=false` → markdown table (to stdout or file)
  - `dump=true` → TSV (to stdout or file)

**Overrides**: `Settings.outputFile`

**Usage**:

```bash
npm test -- -o rankings.md                    # Markdown table to file
npm test -- --dump -o rankings.tsv            # TSV to file
npm test -- -d -o output.tsv                  # TSV to file (short)
# No -o flag outputs to stdout (console)
```

### `-t, --type <type>`

**Type**: Enum (RankingTypeEnum)

**Values**:

- `-t DRAFT`, `--type DRAFT`: Use DRAFT rankings
- `-t DYNASTY`, `--type DYNASTY`: Use DYNASTY rankings
- `-t ROS`, `--type ROS`: Use Rest-of-Season rankings
- `-t WEEKLY`, `--type WEEKLY`: Use Weekly rankings
- Omit: Use TestSettings file value

**Valid Values**: `DRAFT`, `DYNASTY`, `ROS`, `WEEKLY` (case-insensitive)

**Overrides**: `TestSettings.testRankingType`

**Usage**:

```bash
npm test -- --type WEEKLY
npm test -- -t ROS
npm test -- -t draft           # Case-insensitive
```

### `-p, --position <pos>`

**Type**: String (repeatable)

**Values**:

- Single position: `-p QB`
- Multiple positions (repeatable): `-p QB -p RB -p WR`
- Comma-separated: `--position QB,RB,WR`
- Omit: Use TestSettings file value (default: all positions)

**Valid Position Values**: `QB`, `RB`, `WR`, `TE`, `K`, `DST` (case-insensitive)

**Overrides**: `TestSettings.testPositions`

**Usage**:

```bash
npm test -- --position QB
npm test -- -p QB -p RB -p WR                 # Repeatable
npm test -- --position QB,RB,WR               # Comma-separated
npm test -- -p qb                             # Case-insensitive
```

## Implementation Approach

### Step 1: Install commander.js

```bash
npm install commander
```

### Step 2: Create CLI Module (`client/cli-args.js`)

```javascript
import { Command, Option } from 'commander';
import { RankingTypeEnum, PositionEnum } from '../common/index.js';
import { readFileSync } from 'fs';

// Read version from package.json
const packageJson = JSON.parse(readFileSync('package.json', 'utf8'));

const program = new Command();

program
  .name('ff-rankings')
  .description('Fantasy Football Rankings CLI')
  .version(packageJson.version, '-V, --version', 'Display version number')
  .helpOption('-h, --help', 'Display help information');

// Boolean options with negation
program
  .option('-v, --verbose', 'Enable verbose output (detailed ranking metadata)')
  .option('--no-verbose', 'Explicitly disable verbose output')
  .option('-d, --dump', 'Enable TSV output format')
  .option('--no-dump', 'Explicitly disable TSV format (use display-style)');

// Value options
program
  .option('-m, --max-players <number>', 'Maximum number of players to display (0 = all)', parseInt)
  .option('-o, --output <file>', 'Output file path (markdown table if not dump mode, TSV if dump mode)')
  .option('-t, --type <type>', 'Ranking type (DRAFT|DYNASTY|ROS|WEEKLY)', (val) => val.toUpperCase());

// Position option (repeatable or comma-separated)
program
  .option('-p, --position <positions>', 'Position(s) to include (QB,RB,WR,TE,K,DST) - repeatable or comma-separated', 
    (val, previous) => {
      // Handle comma-separated values
      const positions = val.toUpperCase().split(',');
      return previous ? [...previous, ...positions] : positions;
    }, 
    []);

// Add usage examples to help
program.addHelpText('after', `

Examples:
  Display WEEKLY QB rankings with verbose output:
    $ npm test -- -v -t WEEKLY -p QB

  Dump ROS rankings for all positions to TSV file:
    $ npm test -- -d -t ROS -o rankings.tsv

  Show top 10 RB and WR in markdown table:
    $ npm test -- -m 10 -p RB -p WR -o output.md

  Multiple positions (comma-separated):
    $ npm test -- -t WEEKLY -p QB,RB,WR
`);

// Validate ranking type
program.hook('preAction', (thisCommand) => {
  const opts = thisCommand.opts();
  
  if (opts.type) {
    const validTypes = ['DRAFT', 'DYNASTY', 'ROS', 'WEEKLY'];
    if (!validTypes.includes(opts.type)) {
      thisCommand.error(`Invalid ranking type: ${opts.type}. Must be one of: ${validTypes.join(', ')}`);
    }
  }
  
  if (opts.position && opts.position.length > 0) {
    const validPositions = ['QB', 'RB', 'WR', 'TE', 'K', 'DST'];
    const invalidPositions = opts.position.filter(p => !validPositions.includes(p));
    if (invalidPositions.length > 0) {
      thisCommand.error(`Invalid position(s): ${invalidPositions.join(', ')}. Must be one of: ${validPositions.join(', ')}`);
    }
  }
});

program.parse();

export const cliOptions = program.opts();
```

### Step 3: Update Settings Modules

**client/settings.js:**

```javascript
import { cliOptions } from './cli-args.js';

const Settings = {
  // CLI overrides Settings file values
  verbose: cliOptions.verbose ?? false,
  displayMaxPlayers: cliOptions.maxPlayers ?? null,
  outputFile: cliOptions.output ?? null,
  
  // ... other settings
};

export { Settings };
```

**client/tests/settings.js:**

```javascript
import { cliOptions } from '../cli-args.js';
import { RankingTypeEnum } from '../../common/index.js';

const TestSettings = {
  dump: cliOptions.dump ?? false,
  testRankingType: cliOptions.type ? RankingTypeEnum[cliOptions.type] : RankingTypeEnum.DRAFT,
  testPositions: cliOptions.position.length > 0 
    ? cliOptions.position.map(p => PositionEnum[p])
    : null,
};

export { TestSettings };
```

### Step 4: Implement Markdown Table Output

**client/utils.js** (add new functions following existing ToString pattern):

```javascript
// Add playerToMarkdownString as sibling to playerToString and playerToTabDelimitedString
function playerToMarkdownString(player) {
  // Player object knows whether to show opponent or BYE based on its own fields
  const opponentOrBye = player.opponent ? ` | ${player.opponent} |` : player.bye ? ` | ${player.bye} |` : '';
  return `| ${player.rank} | ${player.name} | ${player.team} |${opponentOrBye}`;
}

// Build complete markdown table with header
function playersToMarkdownTable(players) {
  if (!players || players.length === 0) return '';
  
  // Determine header based on first player's fields (player knows its own structure)
  const hasOpponent = !!players[0].opponent;
  const hasBye = !hasOpponent && !!players[0].bye;
  
  // Build header
  let header = '| Rank | Name | Team |';
  let separator = '|------|------|------|';
  
  if (hasBye) {
    header += ' BYE |';
    separator += '-----|';
  }
  
  if (hasOpponent) {
    header += ' Opponent |';
    separator += '----------|';
  }
  
  const lines = [header, separator];
  
  // Each player renders its own markdown row
  for (const player of players) {
    lines.push(playerToMarkdownString(player));
  }
  
  return lines.join('\n');
}

export {
  rankingsMetadataToString,
  playerToString,
  playerToTabDelimitedString,
  playerToMarkdownString,    // New export
  playersToMarkdownTable      // New export
};
```

**Note**: This follows the existing architectural pattern where ToString functions act as extension methods on the object. The player object is responsible for rendering itself - it knows whether to show opponent or BYE based on its own fields.

### Step 5: Update Client Output Logic

**client/client.js** (update `displayRankings` for unified output handling):

```javascript
import { writeFileSync } from 'fs';
import { playersToMarkdownTable } from './utils.js';

export async function displayRankings(/* ... */) {
  const result = await fetchRankings(/* ... */);
  
  const { outputFile, dump } = Settings;
  
  // Generate output in appropriate format
  const output = dump 
    ? dumpRankingsToTabDelimited(result)
    : playersToMarkdownTable(result.players, rankingType);
  
  // Write to destination
  if (outputFile) {
    writeFileSync(outputFile, output, 'utf8');
    console.log(`Output written to: ${outputFile}`);
  } else {
    console.log(output);
  }
}
```

**Key Simplification**: One code path per format, `-o` just changes the destination.

## Testing Strategy

### Test Coverage

For each CLI parameter:

1. **Explicit value**: Verify override works
2. **Omitted param**: Verify Settings file value is used
3. **Negation** (for booleans): Verify `--no-flag` works
4. **Invalid values**: Verify error handling and messages
5. **Conflicts**: Verify mutually exclusive options error appropriately

### Test Scenarios

```bash
# Verbose flag
npm test -- -v                          # Should enable verbose
npm test -- --no-verbose                # Should disable verbose
npm test -- -v --no-verbose            # Should error (conflict)

# Max players
npm test -- -m 5                        # Should limit to 5
npm test -- -m 0                        # Should show all
npm test -- -m abc                      # Should error (invalid)

# Output modes
npm test -- -o output.md                # Markdown table
npm test -- -d -o output.tsv            # TSV file
npm test -- -d                          # TSV to stdout

# Ranking type
npm test -- -t WEEKLY                   # Should use WEEKLY
npm test -- -t invalid                  # Should error

# Positions
npm test -- -p QB                       # Single position
npm test -- -p QB -p RB                 # Multiple positions
npm test -- -p QB,RB,WR                 # Comma-separated
npm test -- -p INVALID                  # Should error

# Help and version
npm test -- -h                          # Should show help
npm test -- -V                          # Should show version
```

### Exit Codes

Follow standard POSIX conventions:

- `0`: Success
- `1`: General error (e.g., API failure, file write error)
- `2`: Usage error (invalid arguments, validation failure)

## Usage Examples

```bash
# Show help
npm test -- -h

# Show version
npm test -- -V

# Verbose weekly QB rankings, all players
npm test -- -v -t WEEKLY -p QB

# Top 10 RBs and WRs for ROS, save to markdown
npm test -- -t ROS -p RB,WR -m 10 -o rankings.md

# Dump all DRAFT positions to TSV file
npm test -- -d -t DRAFT -o draft-rankings.tsv

# Quick check of top 5 TEs for current week
npm test -- -t WEEKLY -p TE -m 5

# Multiple positions with repeatable flags
npm test -- -t WEEKLY -p QB -p RB -p WR -v

# Combine multiple options (short form)
npm test -- -d -t ROS -m 20 -o output.tsv

# Override settings file to disable verbose
npm test -- --no-verbose

# Show all players (override settings file limit)
npm test -- -m 0
```

## Benefits

1. **No file modifications**: Settings files remain clean and committed
2. **Rapid iteration**: Quick testing of different configurations
3. **Standard conventions**: Familiar to users of git, npm, docker
4. **Documentation**: Command history shows what was tested
5. **Scriptable**: Easy to create test scripts with specific configurations
6. **Player ownership prep**: Essential for ownership investigation work
7. **Professional UX**: Follows CLI best practices and POSIX standards

## Error Handling

### Validation Errors

```bash
$ npm test -- -t INVALID
error: Invalid ranking type: INVALID. Must be one of: DRAFT, DYNASTY, ROS, WEEKLY

$ npm test -- -p INVALID
error: Invalid position(s): INVALID. Must be one of: QB, RB, WR, TE, K, DST

$ npm test -- -m abc
error: option '-m, --max-players <number>' argument 'abc' is invalid. Expected a number.
```

### Conflict Errors

```bash
$ npm test -- -v --no-verbose
error: option '-v, --verbose' cannot be used with option '--no-verbose'
```

### File Write Errors

```bash
$ npm test -- -o /invalid/path/file.txt
error: Cannot write to file: /invalid/path/file.txt
ENOENT: no such file or directory
```

## Status

**Planning Complete** - Prerequisites identified, commander.js patterns defined, awaiting pre-work completion before implementation.
