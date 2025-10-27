# CLI Parameter Overrides - Planning Document

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
- The "run both modes in one test run" functionality (ALL) is being retired; the general use case for an app such as this, for a general user, is the display output case - DUMP is a specialty case for me to use to integrate into Sheets

**Files to Update**:

- `client/tests/settings.js`: Replace `testOutputTypes` with `dump` boolean
- `client/tests/runner.js`: Simplify test logic (remove ALL handling)
- ~~Remove `TestOutputTypeEnum.ALL` (keep DISPLAY and DUMP for internal use if needed)~~ get rid of `TestOutputTypeEnum` when getting rid of `TestSettings.testOutputTypes`

### Change `testRankingTypes` Array to `testRankingType` Single Enum

**Current**: `testRankingTypes` (array of ranking types)
**New**: `testRankingType` (single ranking type enum)

**Rationale**:

- **Pre-season context**: ROS/WEEKLY make no sense (not in season). Between DRAFT and DYNASTY, you're either one or the other, not both at once
- **In-season context**: DRAFT/DYNASTY make almost no sense (occasionally useful for comparison early in season). Between ROS and WEEKLY, you sometimes want both, but usually want one THEN the other, not simultaneously
- **Conclusion**: A collection doesn't match typical usage patterns - you typically want ONE ranking type at a time

**Default Behavior**:

- `null` or missing → defensive default is `DRAFT`
- Cannot make it season-aware (too complex for low-level code)
- `DRAFT` chosen as defensive default because:
  - ROS/WEEKLY have no context outside the season
  - DRAFT (and DYNASTY) have minimal context during the season, but maximal (only) context during the off-season
  - DRAFT is more common than DYNASTY

**Settings File Value**:

- Should be explicitly set to `DRAFT` in `TestSettings` (not `null`)
- User will naturally update this as seasons change:
  - End of season: switch from ROS/WEEKLY to DRAFT/DYNASTY for next season
  - New season starts: update `season` setting in server settings
  - Season begins: switch from DRAFT/DYNASTY to ROS/WEEKLY

**Files to Update**:

- `client/tests/settings.js`: Change `testRankingTypes` (array) to `testRankingType` (single enum), set to `RankingTypeEnum.DRAFT`
- `client/tests/runner.js`: Remove array handling, use single value

### Apply Defensive Defaults

**Objective:** Add defensive defaults as "last resort" fallbacks for unexpected situations where settings are missing/null/undefined.

**Defensive Default Behavior** (only applied when setting is missing/null/undefined):

- `verbose`: No defensive default needed - `null`, `false`, or missing → base display (not verbose)
- `displayMaxPlayers`: No defensive default needed - `null`, `0`, or missing → show all players
- `dump`: No defensive default needed - `null`, `false`, or missing → DISPLAY mode
- `testRankingType`: Defensive default is `RankingTypeEnum.DRAFT` (only ranking type with year-round context)
- `testPositions`: No defensive default needed - `null`, empty array, or missing → all positions

**Implementation**: Add nullish coalescing where settings are consumed, but only apply actual defaults for `testRankingType`:

```javascript
// Example for client/client.js displayRankings()
const { displayMaxPlayers = Settings.displayMaxPlayers ?? null, verbose = Settings.verbose ?? false } = options;

// Example for client/tests/runner.js
const rankingType = TestSettings.testRankingType ?? RankingTypeEnum.DRAFT;
```

## Current Settings (After Pre-Work)

### Client Settings (`client/settings.js`)

- `verbose` (boolean): Whether to show detailed ranking metadata - **default in file**: `false`
- `displayMaxPlayers` (number|null): Maximum number of players to show in display rankings - **default in file**: currently `3`, but should be `null` (show all)

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

- `--verbose` or `--verbose=true` - enable verbose mode
- `--verbose=false` - disable verbose mode
- `--verbose=default` - use built-in default (base display, not verbose)
- Omit parameter - use Settings file value

**Overrides**: `Settings.verbose`

### CLI Parameter 2: `--displayMaxPlayers`

**Type**: Nullable integer

**Values**:

- `--displayMaxPlayers=<number>` - show N players (e.g., `--displayMaxPlayers=5`)
- `--displayMaxPlayers=0` or `--displayMaxPlayers=all` or `--displayMaxPlayers=null` - show all players
- `--displayMaxPlayers=default` - use built-in default (show all players)
- Omit parameter - use Settings file value

**Overrides**: `Settings.displayMaxPlayers`

### CLI Parameter 3: `--dump`

**Type**: Boolean

**Values**:

- `--dump` or `--dump=true` - enable DUMP mode (tab-delimited output)
- `--dump=false` - enable DISPLAY mode (formatted console output)
- `--dump=default` - use built-in default (DISPLAY mode)
- Omit parameter - use TestSettings file value

**Overrides**: `TestSettings.dump`

### CLI Parameter 4: `--rankingType`

**Type**: Enum (RankingTypeEnum)

**Values**:

- `--rankingType=DRAFT` - use DRAFT rankings
- `--rankingType=DYNASTY` - use DYNASTY rankings
- `--rankingType=ROS` - use Rest-of-Season rankings
- `--rankingType=WEEKLY` - use Weekly rankings
- `--rankingType=default` - use built-in default (DRAFT)
- Omit parameter - use TestSettings file value

**Overrides**: `TestSettings.testRankingType`

### CLI Parameter 5: `--positions`

**Type**: Comma-separated list (PositionEnum)

**Values**:

- `--positions=QB` - test single position
- `--positions=QB,RB,WR` - test multiple positions (comma-separated)
- `--positions=all` - test all positions (QB, RB, WR, TE, K, DST)
- `--positions=default` - use built-in default (all positions)
- Omit parameter - use TestSettings file value

**Valid Position Values**: `QB`, `RB`, `WR`, `TE`, `K`, `DST`

**Overrides**: `TestSettings.testPositions`

## Implementation Approach

### Command-Line Parsing

Create a new module (e.g., `client/cli-args.js`) to handle argument parsing:

```javascript
function parseCliArgs() {
  const args = process.argv.slice(2);
  const parsed = {};
  
  for (const arg of args) {
    if (arg.startsWith('--')) {
      const [key, value] = arg.slice(2).split('=');
      parsed[key] = value === undefined ? true : value;
    }
  }
  
  return parsed;
}
```

### Settings Override

Modify settings modules to check for CLI overrides:

```javascript
// In client/settings.js
import { getCliOverride } from './cli-args.js';

const Settings = {
  verbose: getCliOverride('verbose', false),
  displayMaxPlayers: getCliOverride('displayMaxPlayers', null),
  // ... rest of settings
};
```

### Special Value Handling

- `"default"` - ignore Settings file value and use built-in default behavior
- `"all"`, `"null"`, or `0` (for displayMaxPlayers) - show all items
- Array values (for positions) - parse comma-separated strings

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

# Quick dump of all ROS positions
npm test -- --dump --rankingType=ROS

# Display only kickers and defense for WEEKLY rankings, limit to 5 players
npm test -- --rankingType=WEEKLY --positions=K,DST --displayMaxPlayers=5

# Use built-in defaults instead of Settings file values
npm test -- --verbose=default --displayMaxPlayers=default --dump=default --rankingType=default --positions=default
```

## Benefits

1. **No file modifications** - Settings files remain clean and committed
2. **Rapid iteration** - Quick testing of different configurations
3. **Documentation** - Command history shows what was tested
4. **Scriptable** - Easy to create test scripts with specific configurations
5. **Player ownership prep** - Essential for ownership investigation work

## Status

**Planning** - Prerequisites identified, tasks defined, awaiting pre-work completion before implementation.
