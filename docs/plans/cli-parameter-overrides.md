# CLI Parameter Overrides - Planning Document

## CLI Framework Reference

This implementation will use **commander.js** for command-line parsing and option handling:

- **NPM Package**: [commander](https://www.npmjs.com/package/commander)
- **GitHub Repository**: <https://github.com/tj/commander.js>
- **Documentation**: <https://github.com/tj/commander.js#readme>

Commander.js provides:

- POSIX-style option flags (`-v`, `--verbose`)
- Type coercion and validation
- Automatic help generation
- Standard CLI conventions
- Well-tested, widely-used framework (40M+ weekly downloads)

## Goal

Implement command-line parameter overrides for client settings to enable flexible testing and investigative work without modifying and saving settings files.

## Motivation

Currently, investigating features like player ownership integration requires manually modifying `client/settings.js` and `client/tests/settings.js`, saving those changes, and then reverting them later. This is tedious and error-prone. Command-line parameter overrides will allow temporary configuration changes without touching the settings files.

## Prerequisites / Pre-Work

Before implementing CLI parameter overrides, the following cleanups and refactorings are needed:

### Rename `displaySize` to `displayMaxPlayers`

**Current Name**: `displaySize` (vague - "size of what?")
**New Name**: `displayMaxPlayers` (clear - maximum number of players to display)
**Behavior**: `0` or less, `null`, or missing = show all players, any positive number = show that many players, maximum

**Files to Update**:

- `client/settings.js`: Rename setting
- `client/client.js`: Update `displayRankings()` function
- All references in client code

### Replace `testOutputTypes` Enum with `dump` Boolean

**Current**: `testOutputTypes` (enum: DISPLAY, DUMP, ALL)
**New**: `dump` (boolean)
**Behavior**:

- `false`, `null`, or missing = DISPLAY mode
- `true` = DUMP mode
- The "run both modes in one test run" functionality (ALL) is being retired; the general use case for an app such as this, for a general user, is the DISPLAY output case - DUMP is a specialty case for power users to integrate into spreadsheets

**Files to Update**:

- `client/tests/settings.js`: Replace `testOutputTypes` with `dump` boolean
- `client/tests/runner.js`: Simplify test logic (remove ALL handling)
- get rid of `TestOutputTypeEnum` when getting rid of `TestSettings.testOutputTypes`

### Change `testRankingTypes` Array to `testRankingType` Single Enum

**Current**: `testRankingTypes` (array of ranking types)
**New**: `testRankingType` (single ranking type enum)

**Rationale**:

- **Pre-season context**: ROS/WEEKLY make no sense (not in season), and between DRAFT and DYNASTY, you're either one or the other, not both at once
- **In-season context**: DRAFT/DYNASTY make almost no sense (occasionally useful for comparison early in season). Between ROS and WEEKLY, you sometimes want both, but usually want one THEN the other, not one AND the other
- **Conclusion**: A collection doesn't match typical usage patterns - you typically want ONE ranking type at a time

**Default Behavior**:

- `null` or missing → defensive default is `DRAFT`
- Cannot make it season/off-season-aware (too complex for low-level code)
- `DRAFT` chosen as defensive default because:
  - ROS/WEEKLY have _no_ context outside the season
  - DRAFT (and DYNASTY) have minimal context during the season, but the only (i.e., maximal) context during the off-season
  - DRAFT is more common than DYNASTY

**Settings File Value**:

- Should be explicitly set to `DRAFT` in `TestSettings` (not `null`)
- User will naturally update this as seasons change:
  - End of season: switch from ROS/WEEKLY to DRAFT/DYNASTY for next season
  - Season getting ready to begin: update `season` server settings from last year to this year
  - Season begins: switch from DRAFT/DYNASTY to ROS/WEEKLY

**Files to Update**:

- `client/tests/settings.js`: Change `testRankingTypes` (array) to `testRankingType` (single enum), set to `RankingTypeEnum.DRAFT`
- `client/tests/runner.js`: Remove array handling, use single value

### Apply Defensive Defaults

**Objective:** Add defensive defaults as "last resort" fallbacks for unexpected situations where settings are missing/null/undefined.

**Defensive Default Behavior** (only applied when setting is missing/null/undefined):

- `verbose`: No defensive default needed - `null`, `false`, or missing → base display (i.e., not verbose)
- `displayMaxPlayers`: No defensive default needed - `null`, non-positive, or missing → show all players
- `dump`: No defensive default needed - `null`, `false`, or missing → DISPLAY mode
- `testRankingType`: Defensive default is `RankingTypeEnum.DRAFT` (it's the only ranking type with year-round context)
- `testPositions`: No defensive default needed - `null`, empty array, or missing → all positions

**Implementation**: Add nullish coalescing where settings are consumed, but only apply actual defaults for `testRankingType`:

```javascript
// Example for client/client.js displayRankings()
const { displayMaxPlayers = Settings.displayMaxPlayers ?? null, verbose = Settings.verbose ?? false } = options;

// Example for client/tests/runner.js
const rankingType = TestSettings.testRankingType ?? RankingTypeEnum.DRAFT; // only year-round context
```

## Current Settings (After Pre-Work)

### Client Settings (`client/settings.js`)

- `verbose` (boolean): Whether to show detailed ranking metadata - **default in file**: `false`
- `displayMaxPlayers` (number|null): Maximum number of players to show in display rankings - **default in file**: currently `3`, but should be `null` (show all) - we can set to `null` after the CLI option exists allowing us to set it to `3` from there

### Test Settings (`client/tests/settings.js`)

- `dump` (boolean): Whether to dump tab-delimited output (false = DISPLAY mode, true = DUMP mode) - **default in file**: should be `false`
- `testRankingType` (enum|null): Which ranking type to test - **default in file**: should be `RankingTypeEnum.DRAFT`
  - Single `RankingTypeEnum` value: `ROS`, `WEEKLY`, `DYNASTY`, or `DRAFT`
  - `null` or missing → defensive default is `DRAFT`
- `testPositions` (array|null): Which positions to test - **default in file**: should be `null` (test all positions)
  - Can be array of `PositionEnum` values: `QB`, `RB`, `WR`, `TE`, `K`, `DST`

## Important: Understanding "Default" Values

**Three Levels of Defaults**:

1. **CLI Parameter Value** (highest priority): Explicitly provided on command line
2. **Settings File Value** (middle priority): Configured in `client/settings.js` or `client/tests/settings.js`
3. **Built-in Default** (lowest priority/last resort): Hardcoded behavior when setting is missing/null

**The `default` Keyword**: When `default` is specified as a CLI parameter value, it means "ignore the Settings file value and use the built-in default behavior":

- `--verbose=default` → use built-in default (base display, not verbose)
- `--displayMaxPlayers=default` → use built-in default (show all players)
- `--dump=default` → use built-in default (DISPLAY mode)
- `--rankingType=default` → use built-in default (DRAFT)
- `--positions=default` → use built-in default (all positions)

this is specifically for when the setting value has been set to _other_ than the expected default value, and the only way to reset it to the default from the command line is to support that as a CLI option

**When CLI Parameter is Omitted**: Uses the Settings file value (not the built-in default)

## Current Usage Patterns

### Settings Consumption

**`verbose`:**

- `client/client.js`: `displayRankings()` uses `Settings.verbose` as default for options
- `client/utils.js`: `rankingsMetadataToString()` accepts verbose parameter

**`displayMaxPlayers`:**

- `client/client.js`: `displayRankings()` uses `Settings.displayMaxPlayers` as default for options
- Controls whether to show all players (`null` or `0`) or limit display (positive number)

**`dump`:**

- `client/tests/runner.js`: `runConfigurableTests()` reads `TestSettings.dump`
- Used to determine whether to run display or dump mode

**`testRankingType`:**

- `client/tests/runner.js`: `runConfigurableTests()` reads `TestSettings.testRankingType`
- Single `RankingTypeEnum` value, no array handling needed
- `null` or missing → uses defensive default `RankingTypeEnum.DRAFT`

**`testPositions`:**

- `client/tests/runner.js`: `runConfigurableTests()` reads `TestSettings.testPositions`
- `null` expands to all positions: `[QB, RB, WR, TE, K, DST]`

## CLI Parameters

### CLI Parameter 1: `--verbose`

**Type**: Boolean

**Values**:

- `--verbose` or `--verbose=true` or `-v` - enable verbose mode
- `--verbose=false` - disable verbose mode
- `--verbose=default` - use built-in default (base display, not verbose; in the current implementation, default → `false`)
- Omit parameter - use Settings file value
- the presence of more than one dump parameter on the command line would be an error, if inconsistent (e.g., -v --verbose=false)

**Overrides**: `Settings.verbose`

### CLI Parameter 2: `--displayMaxPlayers`

**Type**: Nullable integer

**Values**:

- `--displayMaxPlayers=<number>` or `--maxPlayers=<number>` or `--players=<number>` - show N players (e.g., `--displayMaxPlayers=5`)
- `--displayMaxPlayers=0` or `--maxPlayers=0` or `--players=0` - show all players
- `--displayMaxPlayers=default` or `--maxPlayers=default` or `--players=default` - use built-in default (show all players; in the current implementation, default → show all players, i.e., not `slice`)
- Omit parameter - use Settings file value
- the presence of more than one max players parameter on the command line would be an error, if inconsistent (e.g., --players=1 --displayMaxPlayers=0)

**Overrides**: `Settings.displayMaxPlayers`

### CLI Parameter 3: `--dump`

**Type**: Boolean

**Values**:

- `--dump` or `--dump=true` or `-d` - enable DUMP mode (tab-delimited output)
- `--dump=false` - enable DISPLAY mode (formatted console output)
- `--dump=default` - use built-in default (DISPLAY mode; in the current implementation, default → DISPLAY)
- Omit parameter - use TestSettings file value
- the presence of more than one dump parameter on the command line would be an error, if inconsistent (e.g., -d --dump=false)

**Overrides**: `TestSettings.dump`

### CLI Parameter 3b: `--dumpFile` (Optional Enhancement)

**Type**: String (filename)

**Values**:

- `--dumpFile=<filename>` or `--dumpFile <filename>` - write dump output to specified file
- `-d=<filename>` - shorthand for `--dump --dumpFile=<filename>`
- Omit parameter - dump output goes to stdout (current behavior)

**Behavior**:

- When `--dumpFile` is specified, automatically enables dump mode (sets `dump=true`)
- Creates/overwrites the specified file with tab-delimited output
- Useful for scripting and avoiding shell redirection
- Example: `npm test -- --dumpFile=rankings.tsv --rankingType=ROS`

**Implementation Notes**:

- This is an enhancement to the basic dump functionality
- May defer to later iteration if it adds complexity
- Current stdout approach works well with shell redirection (`npm test -- --dump > output.tsv`)

**Overrides**: N/A (new functionality, not overriding existing setting)

### CLI Parameter 4: `--rankingType`

**Type**: Enum (RankingTypeEnum)

**Values**:

- `--rankingType=DRAFT` or `-DRAFT` - use DRAFT rankings
- `--rankingType=DYNASTY` or `-DYNASTY`- use DYNASTY rankings
- `--rankingType=ROS` or `-ROS` - use Rest-of-Season rankings
- `--rankingType=WEEKLY` or `-WEEKLY` - use Weekly rankings
- `--rankingType=default` - use built-in default (DRAFT; in the current implementation, default → DRAFT)
- Omit parameter - use TestSettings file value
- the presence of more than one ranking type on the command line would be an error, if inconsistent (e.g., -DRAFT --rankingType=DYNASTY)

**Overrides**: `TestSettings.testRankingType`

### CLI Parameter 5: `--positions`

**Type**: Comma-separated list (PositionEnum)

**Values**:

- `--positions=QB` or `-QB` - test single position
- `--positions=QB,RB,WR` or `-QB -RB -WR` - test multiple positions (comma-separated)
- `--positions=default` - use built-in default (all positions; in the current implemenation, default → [QB, RB, WR, TE, K, DST])
- Omit parameter - use TestSettings file value
- the presence of more than one position on the command line would be an error, if inconsistent (e.g., -QB --positions=default); however, because it's a collection, any number of position parameters is valid, as long as --positions=default is not also present, i.e., each param turns on that position, so repeats of the same position would result in it still being turned on

**Valid Position Values**: `QB`, `RB`, `WR`, `TE`, `K`, `DST`

**Overrides**: `TestSettings.testPositions`

## Implementation Approach

### Step 1: Install commander.js

```bash
npm install commander
```

### Step 2: Create CLI Module

Create `client/cli-args.js` using commander.js:

```javascript
import { Command } from 'commander';
import { RankingTypeEnum, PositionEnum } from '../common/index.js';

const program = new Command();

program
  .option('-v, --verbose [value]', 'enable verbose output', false)
  .option('--displayMaxPlayers <number>', 'maximum players to display', parseInt)
  .option('--maxPlayers <number>', 'alias for displayMaxPlayers', parseInt)
  .option('--players <number>', 'alias for displayMaxPlayers', parseInt)
  .option('-d, --dump [value]', 'enable dump mode', false)
  .option('--dumpFile <filename>', 'output file for dump mode')
  .option('--rankingType <type>', 'ranking type (DRAFT|DYNASTY|ROS|WEEKLY)')
  .option('-DRAFT', 'use DRAFT rankings')
  .option('-DYNASTY', 'use DYNASTY rankings')
  .option('-ROS', 'use ROS rankings')
  .option('-WEEKLY', 'use WEEKLY rankings')
  .option('--positions <positions>', 'comma-separated positions (QB,RB,WR,TE,K,DST)')
  .option('-QB', 'include QB position')
  .option('-RB', 'include RB position')
  .option('-WR', 'include WR position')
  .option('-TE', 'include TE position')
  .option('-K', 'include K position')
  .option('-DST', 'include DST position');

program.parse();

export const cliOptions = program.opts();
```

### Step 3: Settings Override

Modify settings modules to check for CLI overrides:

```javascript
// In client/settings.js
import { cliOptions } from './cli-args.js';

const Settings = {
  verbose: cliOptions.verbose ?? false,
  displayMaxPlayers: cliOptions.displayMaxPlayers ?? cliOptions.maxPlayers ?? cliOptions.players ?? null,
  // ... rest of settings
};
```

### Step 4: Special Value Handling

- `"default"` keyword - ignore Settings file value and use built-in default behavior
- `0` (for displayMaxPlayers) - show all items
- `--dumpFile <filename>` - redirect dump output to file instead of stdout
- Array values (for positions) - parse comma-separated strings and/or collect multiple position flags
- Validation for conflicting options (e.g., `-v --verbose=false` or `--players=1 --displayMaxPlayers=0`)

## Testing Strategy

For each CLI parameter:

1. Test with explicit value specified
2. Test without CLI parameter (should use Settings file value)
3. Test with `default` keyword (should use built-in default behavior)
4. Test with invalid values (should error gracefully)

## Usage Examples

```bash
# Verbose weekly QB rankings, show all players
npm test -- --verbose --displayMaxPlayers=all --rankingType=WEEKLY --positions=QB

# Quick dump of all ROS positions to stdout
npm test -- --dump --rankingType=ROS

# Dump ROS rankings to file
npm test -- --dumpFile=ros-rankings.tsv --rankingType=ROS

# Display only kickers and defense for WEEKLY rankings, limit to 5 players
npm test -- --rankingType=WEEKLY --positions=K,DST --displayMaxPlayers=5

# Alternative position syntax using flags
npm test -- -WEEKLY -K -DST --players=5

# Use built-in defaults instead of Settings file values
npm test -- --verbose=default --displayMaxPlayers=default --dump=default --rankingType=default --positions=default

# Dump to file with short flags
npm test -- -d=output.tsv -ROS -QB -RB -WR
```

## Benefits

1. **No file modifications** - Settings files remain clean and committed, without requiring code mods just to change test settings
2. **Rapid iteration** - Quick testing of different configurations
3. **Documentation** - Command history shows what was tested
4. **Scriptable** - Easy to create test scripts with specific configurations
5. **Player ownership prep** - Essential for ownership investigation work

## Status

**Planning** - Prerequisites identified, tasks defined, awaiting pre-work completion before implementation.
