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
**Behavior**: `null` or `0` = show all players, any positive number = show that many players

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
- The "run both modes in one test run" functionality (ALL) is being retired

**Files to Update**:

- `client/tests/settings.js`: Replace `testOutputTypes` with `dump` boolean
- `client/tests/runner.js`: Simplify test logic (remove ALL handling)
- Remove `TestOutputTypeEnum.ALL` (keep DISPLAY and DUMP for internal use if needed)

### Reconsider `testRankingTypes` Default Behavior

**Current**: `null` = test all 4 ranking types (ROS, WEEKLY, DYNASTY, DRAFT)
**Concern**: Running DRAFT and DYNASTY by default may not make sense for typical mid-season use

**Decision Needed**: Should `null` mean:

- All 4 types (current)
- Only ROS and WEEKLY (more common mid-season)
- Require explicit specification (error if null)

This should be decided before implementation.

## Current Settings (After Pre-Work)

### Client Settings (`client/settings.js`)

- `verbose` (boolean): Whether to show detailed ranking metadata - **default in file**: `false`
- `displayMaxPlayers` (number|null): Maximum number of players to show in display rankings - **default in file**: currently `3`, but should be `null` (show all)

### Test Settings (`client/tests/settings.js`)

- `dump` (boolean): Whether to dump tab-delimited output (false = DISPLAY mode, true = DUMP mode) - **default in file**: should be `false`
- `testRankingTypes` (array|null): Which ranking types to test - **default in file**: should be `null` (meaning TBD based on decision above)
  - Can be array of `RankingTypeEnum` values: `ROS`, `WEEKLY`, `DYNASTY`, `DRAFT`
- `testPositions` (array|null): Which positions to test - **default in file**: should be `null` (test all positions)
  - Can be array of `PositionEnum` values: `QB`, `RB`, `WR`, `TE`, `K`, `DST`

## Important: Understanding "Default" Values

**Critical Distinction**: The "default" value for each setting is **whatever is stored in the Settings/TestSettings file**, NOT a hardcoded value. This is fundamental to the override system:

- CLI parameters **override** the settings file values
- When no CLI parameter is provided, the value from the settings file is used
- The keyword `"default"` in a CLI parameter means "use the value from the settings file"
- Task 0's "defensive defaults" are **fallback values** used ONLY when Settings/TestSettings are missing/null/undefined

**Defensive Default Values** (used only when settings are missing):

- `verbose`: `false`
- `displayMaxPlayers`: `null` (show all)
- `dump`: `false` (DISPLAY mode)
- `testRankingTypes`: `null` (behavior TBD)
- `testPositions`: `null` (all positions)

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

**`testRankingTypes`:**

- `client/tests/runner.js`: `runConfigurableTests()` reads `TestSettings.testRankingTypes`
- `null` expands to some set of ranking types (behavior TBD)

**`testPositions`:**

- `client/tests/runner.js`: `runConfigurableTests()` reads `TestSettings.testPositions`
- `null` expands to all positions: `[QB, RB, WR, TE, K, DST]`

## Implementation Tasks

### Task 0: Add Defensive Defaults

**Objective:** Ensure code gracefully handles missing settings with appropriate defensive defaults.

**Current State**:

- Settings consumers assume settings exist and have valid values
- No defensive checks for undefined/missing settings

**Required Changes**:

For each setting consumer, add defensive defaults using nullish coalescing. These defensive defaults are ONLY used if the Settings/TestSettings values are missing/null/undefined:

```javascript
// Example for client/client.js displayRankings()
const { displayMaxPlayers = Settings.displayMaxPlayers ?? null, verbose = Settings.verbose ?? false } = options;
```

**Defensive Default Values** (fallback when Settings are missing):

- `verbose`: `false`
- `displayMaxPlayers`: `null` (show all)
- `dump`: `false` (DISPLAY mode)
- `testRankingTypes`: `null` (behavior TBD)
- `testPositions`: `null` (all positions)

### Task 1: Implement `--verbose` CLI Parameter

**CLI Syntax:**

- `--verbose` or `--verbose=true` - enable verbose mode
- `--verbose=false` - disable verbose mode
- `--verbose=default` - use Settings file value

**Implementation:**

- Parse CLI arguments
- Override `Settings.verbose` if parameter present
- Respect "default" keyword to use Settings file value

### Task 2: Implement `--displayMaxPlayers` CLI Parameter

**CLI Syntax:**

- `--displayMaxPlayers=<number>` - show N players
- `--displayMaxPlayers=0` or `--displayMaxPlayers=all` or `--displayMaxPlayers=null` - show all players
- `--displayMaxPlayers=default` - use Settings file value

**Implementation:**

- Parse CLI arguments, handle numeric conversion
- Override `Settings.displayMaxPlayers` if parameter present
- Handle special values: `0`, `all`, `null`, `default`

### Task 3: Implement `--dump` CLI Parameter

**CLI Syntax:**

- `--dump` or `--dump=true` - enable DUMP mode (tab-delimited output)
- `--dump=false` - enable DISPLAY mode (formatted console output)
- `--dump=default` - use TestSettings file value

**Implementation:**

- Parse CLI arguments
- Override `TestSettings.dump` if parameter present
- `true` = DUMP mode, `false` = DISPLAY mode

### Task 4: Implement `--rankingTypes` CLI Parameter

**CLI Syntax:**

- `--rankingTypes=ROS,WEEKLY` - test specific types (comma-separated)
- `--rankingTypes=all` or omit parameter - use default behavior (TBD)
- `--rankingTypes=default` - use TestSettings file value

**Implementation:**

- Parse CLI arguments, split on comma
- Override `TestSettings.testRankingTypes` if parameter present
- Validate against `RankingTypeEnum` values
- Handle special values: `all`, `default`

### Task 5: Implement `--positions` CLI Parameter

**CLI Syntax:**

- `--positions=QB,RB,WR` - test specific positions (comma-separated)
- `--positions=all` or omit parameter - test all positions
- `--positions=default` - use TestSettings file value

**Implementation:**

- Parse CLI arguments, split on comma
- Override `TestSettings.testPositions` if parameter present
- Validate against `PositionEnum` values
- Handle special values: `all`, `default`

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

- `"default"` - use the value from settings file
- `"all"`, `"null"`, or `0` (for displayMaxPlayers) - use null/undefined to trigger "all" logic
- Array values - parse comma-separated strings

## Testing Strategy

After each task implementation:

1. Test with CLI parameter specified
2. Test without CLI parameter (should use Settings file value)
3. Test with `default` keyword (should use Settings file value)
4. Test with invalid values (should error gracefully)

## Usage Examples

```bash
# Verbose weekly QB rankings, show all players
npm test -- --verbose --displayMaxPlayers=all --rankingTypes=WEEKLY --positions=QB

# Quick dump of all ROS positions
npm test -- --dump --rankingTypes=ROS

# Display only kickers and defense across all ranking types, limit to 5 players
npm test -- --positions=K,DST --displayMaxPlayers=5

# Reset to defaults after code has non-default values
npm test -- --verbose=default --displayMaxPlayers=default --dump=default
```

## Benefits

1. **No file modifications** - Settings files remain clean and committed
2. **Rapid iteration** - Quick testing of different configurations
3. **Documentation** - Command history shows what was tested
4. **Scriptable** - Easy to create test scripts with specific configurations
5. **Player ownership prep** - Essential for ownership investigation work

## Status

**Planning** - Prerequisites identified, tasks defined, awaiting pre-work completion before implementation.
