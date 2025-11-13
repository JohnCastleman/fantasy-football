# Fantasy Football Rankings - Development Guide

**Last Updated**: October 23, 2025
**Current Status**: Housekeeping phase - migrating AI context to portable format

## Current Development State

### 🏗️ Architecture Status: ✅ COMPLETE

- **Modular Structure**: Successfully refactored from monolithic to clean separation
- **File Organization**: `client/` `server/` `common/` with proper exports
- **Test Framework**: Configurable testing with preview-sized output
- **Legacy Preservation**: All development iterations moved to `legacy/` folder

### 🎯 Active Focus

**Primary Goal**: Display and Output Enhancements - Working Set 3 (Output Enhancements)

**Current Session Tasks**:

1. ⏸️ Implement markdown table output format
2. ⏸️ Replace `testOutputTypes` enum with `dump` boolean

**See**: [plans/cli-parameter-prerequisites.md](plans/cli-parameter-prerequisites.md) for full working set details

**Completed**: Working Set 2 (PR #4) - Added `outputFile` setting with defensive defaults, stream-based file output, atomic writes, and factory pattern for wrapper functions. See [archive/pr-4-implementation.md](archive/pr-4-implementation.md) for details.

## Development Workflow

### Running Tests

```powershell
# Set API key (required)
$env:FANTASYPROS_API_KEY = "your_api_key_here"

# Run tests
npm test
```

### Test Configuration

Edit `client/tests/settings.js` to configure:

- Output types (DISPLAY, DUMP, or ALL)
- Ranking types to test (ROS, WEEKLY, DYNASTY, DRAFT)
- Positions to test (QB, RB, WR, TE, K, DST)

### Individual Function Usage

```javascript
const { displayRosQbRankings, dumpWeeklyWrRankings } = require('./client');

// Display formatted rankings
await displayRosQbRankings();

// Export tab-delimited data
await dumpWeeklyWrRankings();
```

## Module Responsibilities

### Common Module (`common/`)

- **Purpose**: Shared enums, data classes, and utilities
- **Key Components**:
  - `ScoringTypeEnum`: STD, PPR, HALF
  - `RankingTypeEnum`: ROS, WEEKLY, DYNASTY, DRAFT
  - `PositionEnum`: QB, RB, WR, TE, K, DST
  - `PlayerRankingData`: Player data model (rank, name, team)
  - `RankingsResult`: Complete result with metadata

### Server Module (`server/`)

- **Purpose**: API integration with FantasyPros
- **Key Components**:
  - `server.js`: HTTP request logic and business rules
  - `settings.js`: API configuration and mappings
  - `utils.js`: Data transformation utilities
  - `index.js`: Public interface

### Client Module (`client/`)

- **Purpose**: Data presentation and output
- **Key Components**:
  - `client.js`: Core display logic
  - `display.js`: 24 display functions (4 types × 6 positions)
  - `dump.js`: 24 tab-delimited output functions
  - `settings.js`: Display configuration
  - `utils.js`: String formatting
  - `tests/`: Test framework

## Configuration

### Server Settings (`server/settings.js`)

```javascript
const Settings = {
  season: 2025,
  scoringType: ScoringTypeEnum.STD,
  fantasyprosApiKey: process.env.FANTASYPROS_API_KEY || null,  // Required env var
  fantasyprosApiMapping: { /* ... */ }
};
```

### FantasyPros API Configuration

- **Season**: 2025 (hardcoded in server/settings.js)
- **Default scoring**: STD (hardcoded in server/settings.js)
- **League-specific**: Geeksquadron (Yahoo Standard scoring)
- **API key**: REQUIRED via FANTASYPROS_API_KEY environment variable
  - Set via PowerShell: `$env:FANTASYPROS_API_KEY = "your_key"`
  - Loaded from .env file using dotenv package

**Note**: API key must be set via environment variable before running tests

### Client Settings (`client/settings.js`)

```javascript
const Settings = {
  displaySize: 3,        // Number of players in preview
  verbose: false,        // Include detailed headers
  tabDelimitedHeader: "rank\tname\tteam",
  displayText: { /* ... */ }
};
```

## Environment Constraints

### Development Environment

- **Repository**: Local git repository with GitHub remote
- **Node.js**: Standard npm package management
- **Version Control**: Git with feature branch workflow

## API Samples

Raw API response samples are stored in `docs/api-samples/` for reference:

- `fantasypros-ROS(W*)-(QB|RB|WR|TE|K|DST).json` - Rest-of-Season rankings for all positions
- `fantasypros-W*-(QB|RB|WR|TE|K|DST).json` - Weekly rankings for all positions
- `fantasypros-league-roster-geeksquadron.json` - League roster data with player ownership
- `flockfantasy-REDRAFT-ALL.json` - Alternative data source sample

## Fantasy Football Context

**Season**: 2025 NFL season
**API**: FantasyPros with API key authentication
**Leagues**:

- Default: Standard scoring (STD)
- Geeksquadron: Yahoo public league (Standard scoring)

**Use Cases**:

- Weekly waiver wire decisions
- Dynasty league analysis
- Draft preparation
- Lineup optimization

## Known Issues & Future Work

### Completed

- [x] **SECURITY**: Revoke GitHub Personal Access Token (shared in chat session) and generate a new one at <https://github.com/settings/tokens>
- [x] **API Key Setup**: Install dotenv package and configure to load .env file (test with new GitHub PAT)
- [x] **Dependency Migration**: Move globally-installed packages to local node_modules (date-fns installed locally, axios not used in code)
- [x] **Environment Cleanup**: Remove NODE_PATH workaround from package.json now that we're off Google Drive and npm works properly
- [x] **ES Modules Migration**: Convert entire project from CommonJS (require/module.exports) to ES modules (import/export)
- [x] **Process (Important)**: Define TodoWrite/backlog integration in .cursorrules - TodoWrite acts as writethrough cache of subset of development.md backlog for active session work
- [x] **Process (Important)**: Scrub .cursorrules to separate clear AI instructions (.cursorrules) vs project/process details (move to docs/*.md)
- [x] **Player Data: BYE Week Field**
  - [x] Server: Add BYE to ranking results in ROS and WEEKLY (and anywhere else where available in API response)
  - [x] Client DISPLAY: Surface BYE in tabular display anywhere it's available in the ranking result
  - [x] Client DUMP: Add "bye" column ONLY in ROS dumped results (per TSV usage requirements)
- [x] **Player Data: Opponent Field**
  - [x] Server: Add Opponent only in WEEKLY ranking results (opponent changes week-to-week, only makes sense in that context)
  - [x] Client DISPLAY: Surface Opponent in tabular display anywhere it's available in the ranking result (should only be WEEKLY)
  - [x] Client DUMP: Add "opponent" column ONLY in WEEKLY dumped results (per TSV usage requirements)
- [x] **Interactive Rebase**: Reorganize commits 931ec30 through b2e3329 into focused, single-purpose commits following commit message guidelines - see [archive/rebase-plan-OCT-24-work.md](archive/rebase-plan-OCT-24-work.md)
- [x] **Display and Output Enhancements - Working Set 1**: Simple renamings for clarity and consistency - see [archive/pr-2-implementation.md](archive/pr-2-implementation.md)
  - [x] Rename `displaySize` → `displayMaxPlayers`
  - [x] Rename `testRankingTypes` → `rankingType` (array → single enum)
  - [x] Rename `testPositions` → `positions`
  - [x] Fix null handling in displayMaxPlayers
  - [x] Document DRAFT default reasoning

### High Priority (top of the backlog)

(currently empty)

### Backlog

- [ ] **Display and Output Enhancements**: Settings refactoring, markdown table formatting, and file output capabilities - see [plans/cli-parameter-prerequisites.md](plans/cli-parameter-prerequisites.md)
  - [x] Working Set 1 (Simple Renamings): clearer names, simplified types, defensive defaults - **COMPLETE** (PR #2, merged 2025-10-28)
  - [ ] Working Set 2 (New Setting and Defaults): Add `outputFile` setting, apply defensive defaults
  - [ ] Working Set 3 (Output Enhancements): Markdown table output format, file output with Node.js streams, replace `testOutputTypes` enum with `dump` boolean
  - **Status**: IN PROGRESS - Working Set 2 (New Setting and Defaults) next
- [ ] **CLI Parameter Overrides**: Implement command-line parameter overrides for flexible testing without modifying settings files - see [plans/cli-parameter-overrides.md](plans/cli-parameter-overrides.md)
  - Enables rapid iteration and investigation for features like player ownership integration
  - Commander.js integration for POSIX-style CLI parameters
  - **Status**: Requires completion of Display and Output Enhancements
  - Parameters: `-v` (verbose), `-d` (dump), `-o` (output), `-t` (type), `-p` (position), `-m` (max-players)
- [ ] **Player Ownership Integration**: Add league roster data to show which team owns each player in rankings - see [plans/player-ownership-integration.md](plans/player-ownership-integration.md)
- [ ] **Extract Configuration to Separate Files**: Refactor inline configuration objects to dedicated config files for better organization and maintainability
  - `server/settings.js`: Extract `fantasyprosApiMapping` to `server/api-mappings.js`
  - `server/settings.js`: Extract `fantasyprosLeagues` to `server/leagues.js`
  - `client/settings.js`: Extract `tabDelimitedHeader` to `client/header-formats.js`
  - `client/settings.js`: Extract `displayText` to `client/display-text.js`
- [ ] **Server Architecture**: Host server in separate process with HTTP API for client access (enables multiple client types and remote access)

### Future Enhancements (might get to some day)

- [ ] **Player Data Expansion (Full API)**: Fetch all available fields from FantasyPros API response and perform filtering client-side instead of server-side (e.g., projections, injury status, ADP, tiers)
- [ ] **Additional Data Source Integrations**: Integrate additional data sources (e.g., Flock Fantasy API - sample responses available in `docs/api-samples/`)
- [ ] **Standard npm Scripts**: Add proper npm test and task runner scripts (grunt/gulp-style automation)
- [ ] **TypeScript Migration**: Port JavaScript to TypeScript for type safety
- [ ] **Cross-Device AI Context**: Enable async AI model execution in the cloud (similar to GitHub Copilot Coding Agent or Google Jules) - submit instructions from any device (e.g., phone) that run to completion asynchronously using Cursor Pro subscription

### Nice to Haves

- [ ] **Server- and Client-Side Logging**: Add configurable logging framework for debugging and monitoring (e.g., winston, pino, or debug module)
  - Server: Log API requests, responses, errors, and performance metrics
  - Client: Log display/dump operations, settings overrides, and errors
  - Configurable log levels (error, warn, info, debug, trace)
  - Optional log file output with rotation
- [ ] **Alternative GSheets Integration**: Explore options beyond TSV-to-stdout for transferring DUMP results into Google Sheets (e.g., direct Google Sheets API integration). Note: Current TSV-to-stdout implementation is intentional and works well with shell redirection/piping
- [ ] **UI Client**: Supplement existing CLI client with a UI client (web or desktop) that provides the same functionality. Would leverage the separate HTTP API server

## Recent Development History

### October 9, 2025

- Tested WEEKLY K/DST dump functions
- Generated tab-delimited output for spreadsheet import

### October 8, 2025

- Tested ROS K/DST dump functions
- Validated tab-delimited format

### October 5, 2025

- Completed architectural refactoring
- Split monolithic file into modular structure
- Implemented 24 display + 24 dump functions
- Created configurable test framework

### November 13, 2025

- ✅ **PR #4 Completed**: Working Set 2 - New Setting and Defaults
  - Added `outputFile` setting with stream-based file output
  - Implemented atomic write strategy using `withTempFile` wrapper
  - Added path sanitization and directory validation
  - Fixed resource leaks in stream error handling
  - Implemented factory pattern for 48 wrapper functions (display.js and dump.js)
  - Added options forwarding for per-call overrides
  - See [archive/pr-4-implementation.md](archive/pr-4-implementation.md) for full details

### October 23, 2025

- Migrated from editor-specific folders to portable documentation structure
- Created `.cursorrules` for AI development guidelines
- Organized documentation in `docs/` folder
- Fixed all markdown linting issues across documentation
- Added environment variable support for API key
- Initialized git repository with GitHub remote
- Installed dotenv package and created .env template
- Removed NODE_PATH workaround from package.json
- Migrated globally-installed date-fns to local dependency
- Converted entire project from CommonJS to ES modules

---

**For architectural decisions and rationale, see**: `docs/architecture.md`
**For AI development rules, see**: `.cursorrules`
