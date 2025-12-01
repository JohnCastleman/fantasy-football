# Fantasy Football Rankings System

A modular Node.js application for fetching and displaying fantasy football player rankings from multiple fantasy sports data sources. Currently supports FantasyPros API with configurable league-specific settings, designed to easily integrate additional ranking services and data providers.

## Architecture Overview

This codebase has been carefully refactored from a monolithic structure into a clean, modular architecture with proper separation of concerns.

### Data Sources & League Configuration

**Current Support:**

- **FantasyPros API**: Primary data source with comprehensive ranking types (ROS, Weekly, Dynasty, Draft)
- **League-Specific Rankings**: Configurable support for specific fantasy leagues (e.g., Geeksquadron league integration)

**Future Architecture:**

- **Multiple Ranking Services**: Designed to easily integrate additional fantasy sports data providers
- **Configuration-Driven Sources**: Planned migration from hardcoded Settings to flexible, axios-based HTTP client configuration
- **League Management**: Enhanced support for multiple league contexts and custom scoring systems

### Project Structure

```text
code/
├── README.md                 # This file
├── package.json             # Node.js dependencies and scripts (legacy - needs update)
├── common/                  # Shared utilities and data models
│   ├── index.js            # Module exports
│   └── common.js           # Enums and data classes
├── server/                  # API integration layer
│   ├── index.js            # Module exports
│   ├── server.js           # Core business logic
│   ├── settings.js         # Configuration
│   └── utils.js            # Data transformation utilities
├── client/                  # Display and output logic
│   ├── index.js            # Module exports
│   ├── client.js           # Core display functions
│   ├── settings.js         # Client configuration
│   ├── utils.js            # String formatting utilities
│   ├── display.js          # 24 display functions (all combinations)
│   ├── dump.js             # 24 dump functions (tab-delimited output)
│   └── tests/              # Test framework
│       ├── index.js        # Test runner entry point
│       ├── settings.js     # Test configuration
│       └── runner.js       # Test execution logic
└── legacy/                  # Original files and development history
    ├── .ai-context/           # Archived AI context (pre-portable documentation)
    ├── *.backup.js            # Original monolithic code backups
    ├── FF-scrape-position-list.js     # Chrome DevTools AI-assisted scraping script
    └── FF-ROS(W4)-position-list-K.html # Captured FantasyPros HTML for scraping
```

## Module Responsibilities

### Common Module (`common/`)

- **Purpose**: Shared enums, data classes, and utilities used across all modules
- **Key Components**:
  - `ScoringTypeEnum`: STD, PPR, HALF scoring types
  - `RankingTypeEnum`: ROS, WEEKLY, DYNASTY, DRAFT ranking types
  - `PositionEnum`: QB, RB, WR, TE, K, DST positions
  - `PlayerRankingData`: Individual player data model
  - `RankingsResult`: Complete ranking result with metadata

### Server Module (`server/`)

- **Purpose**: API integration with FantasyPros, data fetching and transformation
- **Key Components**:
  - `server.js`: Core HTTP request logic and business rules
  - `settings.js`: API configuration, season settings, and mapping tables
  - `utils.js`: Data transformation between internal enums and API formats
  - `index.js`: Clean public interface with re-exports

### Client Module (`client/`)

- **Purpose**: Data presentation, formatting, and output generation
- **Key Components**:
  - `client.js`: Core display logic with configurable settings
  - `display.js`: 24 specialized display functions (4 ranking types × 6 positions)
  - `dump.js`: 24 tab-delimited output functions for spreadsheet import
  - `settings.js`: Display configuration (preview size, verbosity, text mappings)
  - `utils.js`: String formatting and metadata processing
  - `tests/`: Configurable test framework for validation

## Key Design Decisions

### 1. Modular Architecture

- **Why**: Moved from single 500+ line file to focused, single-responsibility modules
- **Benefits**: Easier maintenance, testing, and future enhancements
- **Pattern**: Each module has an `index.js` that serves as a clean public interface

### 2. Enum-Based Type System

- **Why**: Ensures type safety and consistent API mapping
- **Implementation**: `Object.freeze()` patterns for immutable enums
- **Benefits**: Prevents runtime errors and provides clear contracts

### 3. Settings-Driven Configuration

- **Why**: Centralized configuration management with sensible defaults
- **Features**: Separate client/server settings, configurable test execution
- **Future**: Foundation for CLI argument overrides

### 4. Comprehensive Function Generation

- **Why**: Covers all 24 combinations of ranking types and positions
- **Pattern**: Both display (formatted output) and dump (tab-delimited) variants
- **Benefits**: Complete API coverage with consistent interface

### 5. Configurable Test Framework

- **Why**: Validates all functionality without overwhelming output
- **Features**: Settings-driven test selection, preview-sized output
- **Benefits**: Quick validation during development

## Configuration

### Environment Variables (Required)

**API Key** - Must be set via environment variable:

**PowerShell** (Windows):

```powershell
$env:FANTASYPROS_API_KEY = "your_api_key_here"
```

**Future**: Create a `.env` file in project root (requires `dotenv` package):

```text
FANTASYPROS_API_KEY=your_api_key_here
```

Then load in code:

```javascript
require('dotenv').config();
```

### Server Settings (`server/settings.js`)

The application configuration:

```javascript
const Settings = {
  season: 2025,
  scoringType: ScoringTypeEnum.STD,
  fantasyprosApiKey: process.env.FANTASYPROS_API_KEY || null,  // Required env var
  fantasyprosApiMapping: { /* API format mappings */ }
};
```

### Client Settings (`client/settings.js`)

```javascript
const Settings = {
  displayMaxPlayers: null,  // Number of players to show in preview; null or 0 = show all
  verbose: false,           // Include detailed headers
  tabDelimitedHeader: "rank\tname\tteam\tbye\topponent",
  displayText: { /* UI text mappings */ }
};
```

### Test Settings (`client/tests/settings.js`)

```javascript
const TestSettings = {
  rankingTypesToTest: [RankingTypeEnum.ROS, RankingTypeEnum.WEEKLY],
  positionsToTest: [PositionEnum.QB, PositionEnum.RB],
  testOutputType: TestOutputTypeEnum.DISPLAY // or ALL, DUMP
};
```

## Documentation Structure

This project uses a portable, AI-friendly documentation structure:

- **`.cursorrules`** - AI development guidelines and coding standards
- **`docs/architecture.md`** - Architectural decisions and rationale
- **`docs/development.md`** - Development guide and workflow reference
- **`docs/api-samples/`** - Sample API responses for reference

## Current Limitations & Future Work

### 1. Google Drive + npm Compatibility

- **Issue**: Cannot easily install npm packages in Google Drive environment
- **Workaround**: Using `require()` instead of `import`, NODE_PATH environment variable
- **Solution**: Migrate to local git repository with proper npm support

### 2. API Key Security

- **Issue**: API key has fallback hardcoded in settings
- **Plan**: Environment variables with .env file
- **Status**: Implemented with environment variable support (fallback remains for development)

### 3. Limited Player Data

- **Issue**: Only using 3 columns from rich FantasyPros API response
- **Plan**: Expand to include bye weeks, opponent teams, projections
- **Status**: Planned for future development

## Usage

### Running Tests

**PowerShell** (set API key first):

```powershell
cd "g:\My Drive\Fantasy Football\code"

# Set API key environment variable (required)
$env:FANTASYPROS_API_KEY = "your_api_key_here"

# Run tests
npm test

# Or manual execution:
$env:NODE_PATH = "C:\Users\johnc\AppData\Roaming\npm\node_modules"
node "client\tests\index.js"
```

### Individual Function Usage

```javascript
const { displayRosQbRankings, dumpWeeklyWrRankings } = require('./client');

// Display formatted rankings
await displayRosQbRankings();

// Export tab-delimited data
await dumpWeeklyWrRankings();
```

## Development Notes

- **Testing Strategy**: Run full test suite after any architectural changes
- **Module Independence**: Each module can be modified without affecting others
- **Consistent Patterns**: All modules follow the same export/import conventions
- **Future-Proof**: Architecture supports CLI arguments, TypeScript migration, and additional data sources

## Migration Checklist

When moving to local git repository:

- [ ] Copy entire `code/` folder to local directory
- [ ] Initialize git repository
- [ ] Create proper `package.json` with dependencies
- [ ] Set up `.gitignore` for API keys and node_modules
- [ ] Replace hardcoded API key with environment variable
- [ ] Consider migrating to ES6 imports
- [ ] Add npm scripts for common tasks
- [ ] Set up GitHub repository as remote origin

## Google Sheets Integration Tools

Automation scripts for integrating fantasy football data with Google Sheets:

- **Waiver Report Tool** (`tools/waiver-report/`) - Processes Ron Stewart's weekly waiver report from Google Docs to Google Sheets. See [tools/waiver-report/README.md](tools/waiver-report/README.md) for details.
- **ROS Report Tool** (`tools/ros-report/`) - Copies Rest of Season rankings from source Google Sheet tabs to destination tabs. See [tools/ros-report/README.md](tools/ros-report/README.md) for details.
- **FantasyPros K/DST Rankings Tool** (`tools/kdst-rankings/`) - Writes FantasyPros Kicker and Defense/Special Teams rankings directly to Google Sheets. See [tools/kdst-rankings/README.md](tools/kdst-rankings/README.md) for details.

All tools use the shared `google-auth-utils` package (installed as editable package from `../google-auth-utils`) for OAuth authentication.
