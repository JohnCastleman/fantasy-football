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

**Note**: API key must be set via environment variable:

```powershell
$env:FANTASYPROS_API_KEY = "your_api_key_here"
```

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

### Immediate Priority

1. ~~**SECURITY (Immediate)**: Revoke GitHub Personal Access Token (shared in chat session) and generate a new one at <https://github.com/settings/tokens>~~ ✅
2. **API Key Setup**: Install dotenv package and configure to load .env file (test with new GitHub PAT - see instructions below) 🔄
3. **Environment Cleanup**: Remove NODE_PATH workaround from package.json now that we're off Google Drive and npm works properly
4. **Dependency Migration**: Move globally-installed packages to local node_modules (e.g., date-fns used only in this project, remove unused axios)

### High Priority

1. **Process (Important)**: Scrub .cursorrules to separate clear AI instructions (.cursorrules) vs project/process details (move to docs/*.md)
2. **Process (Important)**: Use backlog in development.md as persistent source of truth for task work and TodoWrite chat tool as a writethrough cache of it
3. **Player Data Expansion (Immediate Need)**: Add BYE week per player (ROS rankings) and Opponent per player (WEEKLY rankings)
4. **Update package.json**: Update for modular architecture (entry points, scripts, dependencies)
5. **CLI Options**: Add previewSize and verbose command-line argument overrides for Settings defaults

### Future Enhancements

1. **Player Data Expansion (Full API)**: Fetch all available fields from FantasyPros API response and perform filtering client-side instead of server-side (e.g., projections, injury status, ADP, tiers)
2. **Tab-Delimited Output Handling**: Explore routing dump function output to files for spreadsheet import (console stream separation approach)
3. **Standard npm Scripts**: Add proper npm test and task runner scripts (grunt/gulp-style automation)
4. **TypeScript Migration**: Port JavaScript to TypeScript for type safety
5. **Cross-Device AI Context**: Enhance MCP GitHub integration for full cross-device development workflow

### Future: Enable .env File Support

Once ready to migrate from environment variables to .env file:

```bash
# Install dotenv package
npm install dotenv

# Create .env file in project root
echo "FANTASYPROS_API_KEY=your_key_here" > .env

# Add to top of server/settings.js
require('dotenv').config();

# Then run tests without manual env var:
npm test
```

**Note**: `.env` is already in `.gitignore` to prevent committing secrets.

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
- Prepared baseline architecture for git commit

---

**For architectural decisions and rationale, see**: `docs/architecture.md`
**For AI development rules, see**: `.cursorrules`
