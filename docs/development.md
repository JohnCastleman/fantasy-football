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

**Primary Goal**: Expand player data (bye weeks, opponent teams) and secure API key

**Current Session Tasks**:

1. ✅ Migrate from editor-specific folders to portable documentation
2. ✅ Add environment variable support for API key
3. ✅ Prepare baseline for git commit
4. 🔜 Expand ROS rankings to include BYE week per player (after git setup)
5. 🔜 Expand WEEKLY rankings to include opponent team per player (after git setup)

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

- `fantasypros-ROS(W7)-K.json` - Rest-of-Season Kickers
- `fantasypros-ROS(W7)-DST.json` - Rest-of-Season Defense
- `fantasypros-W7-K.json` - Weekly Kickers (Week 7)
- `fantasypros-W7-DST.json` - Weekly Defense (Week 7)
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

1. ~~**SECURITY**: Revoke GitHub Personal Access Token (shared in chat session) and generate a new one at <https://github.com/settings/tokens>~~ ✅
2. ~~**API Key Setup**: Install dotenv package and configure to load .env file (test with new GitHub PAT)~~ ✅
3. ~~**Dependency Migration**: Move globally-installed packages to local node_modules (date-fns installed locally, axios not used in code)~~ ✅
4. ~~**Environment Cleanup**: Remove NODE_PATH workaround from package.json now that we're off Google Drive and npm works properly~~ ✅
5. ~~**ES Modules Migration**: Convert entire project from CommonJS (require/module.exports) to ES modules (import/export)~~ ✅
6. ~~**Process (Important)**: Define TodoWrite/backlog integration in .cursorrules - TodoWrite acts as writethrough cache of subset of development.md backlog for active session work~~ ✅
7. ~~**Process (Important)**: Scrub .cursorrules to separate clear AI instructions (.cursorrules) vs project/process details (move to docs/*.md)~~ ✅
8. ~~**Player Data: BYE Week Field**~~ ✅
   - ~~Server: Add BYE to ranking results in ROS and WEEKLY (and anywhere else where available in API response)~~
   - ~~Client DISPLAY: Surface BYE in tabular display anywhere it's available in the ranking result~~
   - ~~Client DUMP: Add "bye" column ONLY in ROS dumped results (per TSV usage requirements)~~
9. ~~**Player Data: Opponent Field**~~ ✅
   - ~~Server: Add Opponent only in WEEKLY ranking results (opponent changes week-to-week, only makes sense in that context)~~
   - ~~Client DISPLAY: Surface Opponent in tabular display anywhere it's available in the ranking result (should only be WEEKLY)~~
   - ~~Client DUMP: Add "opponent" column ONLY in WEEKLY dumped results (per TSV usage requirements)~~
10. ~~**Interactive Rebase**: Reorganize commits 931ec30 through b2e3329 into focused, single-purpose commits following commit message guidelines - see [archive/rebase-plan-OCT-24-work.md](archive/rebase-plan-OCT-24-work.md)~~ ✅

### High Priority

1. **Server Architecture**: Host server in separate process with HTTP API for client access (enables multiple client types and remote access)
2. **CLI Options**: Add previewSize and verbose command-line argument overrides for Settings defaults

### Future Enhancements

1. **Player Data Expansion (Full API)**: Fetch all available fields from FantasyPros API response and perform filtering client-side instead of server-side (e.g., projections, injury status, ADP, tiers)
2. **Additional Data Source Integrations**: Integrate additional data sources (e.g., Flock Fantasy API - sample responses available in `docs/api-samples/`)
3. **Standard npm Scripts**: Add proper npm test and task runner scripts (grunt/gulp-style automation)
4. **TypeScript Migration**: Port JavaScript to TypeScript for type safety
5. **Cross-Device AI Context**: Enable async AI model execution in the cloud (similar to GitHub Copilot Coding Agent or Google Jules) - submit instructions from any device (e.g., phone) that run to completion asynchronously using Cursor Pro subscription

### Nice to Haves

1. **Alternative GSheets Integration**: Explore options beyond TSV-to-stdout for transferring DUMP results into Google Sheets (e.g., direct Google Sheets API integration). Note: Current TSV-to-stdout implementation is intentional and works well with shell redirection/piping
2. **UI Client**: Supplement existing CLI client with a UI client (web or desktop) that provides the same functionality. Would leverage the separate HTTP API server from task #4 in High Priority

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
