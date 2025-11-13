# Fantasy Football Rankings - Architectural Decisions Log

**Project**: Fantasy Football Rankings System
**Repository**: [Future GitHub URL]
**Decision Log Started**: October 5, 2025

## Major Architectural Decisions

### 1. Modular Architecture Over Monolithic (October 2025)

**Decision**: Split 500+ line monolithic file into focused modules
**Context**: Original single file was becoming unmaintainable
**Options Considered**:

- Keep monolithic with better organization
- Split into 2-3 large modules
- Full modular split with single-responsibility principle

**Chosen**: Full modular split (`client/` `server/` `common/`)
**Rationale**:

- Easier testing and maintenance
- Clear separation of concerns
- Supports future enhancements (CLI, TypeScript, multiple data sources)
- Industry best practices for Node.js applications

**Impact**: Successfully implemented with 24 ranking function combinations

### 2. Enum-Based Type System (October 2025)

**Decision**: Use `Object.freeze()` pattern for immutable enums
**Context**: Needed type safety without TypeScript complexity
**Alternatives**: String constants, plain objects, immediate TypeScript migration

**Chosen**: `Object.freeze()` immutable enums
**Rationale**:

- Type safety in JavaScript
- Prevents runtime mutations
- Clear API contracts
- Easy migration path to TypeScript
- Consistent naming patterns

**Implementation**: `ScoringTypeEnum`, `RankingTypeEnum`, `PositionEnum`

### 3. Settings-Driven Configuration (October 2025)

**Decision**: Centralized configuration objects over hardcoded values
**Context**: Multiple configurable options across client/server modules
**Options**: Environment variables only, config files, Settings objects

**Chosen**: Settings objects with future CLI override capability
**Rationale**:

- Sensible defaults for quick usage
- Clear documentation of available options
- Foundation for command-line argument parsing
- Separation of client vs server concerns

**Future**: CLI arguments will override Settings defaults

### 4. Comprehensive Function Generation (October 2025)

**Decision**: Generate all 24 ranking/position combinations
**Context**: FantasyPros API supports 4 ranking types × 6 positions
**Alternatives**: Generic functions with parameters, subset of popular combinations

**Chosen**: Individual functions for each combination
**Rationale**:

- Complete API coverage
- Consistent naming patterns
- Easy discovery and usage
- Both display and dump variants
- Clear function signatures

**Pattern**: `displayRosQbRankings()`, `dumpWeeklyWrRankings()`, etc.

### 5. Test Framework Design (October 2025)

**Decision**: Configurable test execution with preview-sized output
**Context**: 24 functions × full output = console overflow
**Options**: Full output, fixed subset, no testing, configurable approach

**Chosen**: Settings-driven configurable testing with preview mode
**Rationale**:

- Prevents console spam during development
- Configurable for different testing needs
- Validates all functionality
- Real API calls for integration testing
- Visual confirmation of results

**Implementation**: `TestSettings` with output type and preview size controls

### 6. Re-export Pattern for Module Interfaces (October 2025)

**Decision**: Use `index.js` files as clean public interfaces
**Context**: Multiple files per module, need clean external API
**Alternatives**: Direct imports, barrel exports, namespace objects

**Chosen**: `index.js` re-export pattern
**Rationale**:

- Clean public API surface
- Internal refactoring without breaking changes
- Standard Node.js pattern
- Easy to understand and maintain
- Supports future module reorganization

**Pattern**: Each module has focused files + `index.js` for exports

### 7. Git-Based Version Control (October 2025)

**Decision**: Local git repository with GitHub as remote origin
**Context**: Need proper version control and cross-device development support
**Options**: Local-only, GitHub, GitLab, Bitbucket

**Chosen**: Local git with GitHub remote and MCP integration
**Rationale**:

- Standard version control workflow
- Enables collaboration and issue tracking  
- Supports MCP GitHub integration for AI-assisted development
- Cross-device synchronization
- Public repository for portfolio

**Implementation**: Git repository with feature branch workflow

### 8. MCP GitHub Integration Strategy (October 2025)

**Decision**: Use MCP server for cross-device AI development workflow
**Context**: Need Claude access on phone/multiple devices with repository context
**Alternatives**: GitHub Copilot subscription, manual context export, local-only

**Chosen**: MCP GitHub server with git-based context management
**Rationale**:

- Leverages existing Claude Pro subscription
- True cross-device context
- Persistent AI memory via git files
- Sandbox branch workflow for AI suggestions
- No additional subscriptions required

**Implementation**: Documentation structure with `.cursorrules` and `docs/` folder

### 9. AI Context Management: Portable Documentation (October 2025)

**Decision**: Use `.cursorrules` + `docs/` structure for AI context
**Context**: Migrated from editor-specific folder to portable format
**Alternatives**: Keep editor-specific folders, use only `.cursorrules`, no AI context

**Chosen**: Hybrid approach with `.cursorrules` + comprehensive documentation
**Rationale**:

- `.cursorrules`: Portable, works with multiple AI IDEs
- `docs/`: Standard documentation structure, git-friendly
- Architecture decisions preserved in docs/architecture.md
- Development context in docs/development.md
- API samples in docs/api-samples/

**Implementation Strategy**:

- `.cursorrules` contains active development rules
- `docs/` contains historical context and reference material
- Both synced via git for cross-device access

### 12. File Output with Atomic Writes (November 2025)

**Decision**: Use atomic write pattern (temp file + rename) for file output
**Context**: Need reliable file output that prevents partial writes on failure
**Alternatives**: Direct write, append mode, file locking

**Chosen**: Atomic write using temporary file + rename
**Rationale**:

- Prevents partial file writes on failure
- Ensures file is only visible when complete
- Standard pattern for reliable file I/O
- Works across all filesystems

**Implementation**: `withTempFile` wrapper function that creates temp file, writes to it, then atomically renames to final path. Integrated into `withOptionalFileStream` for all file writes.

### 13. Factory Pattern for Wrapper Functions (November 2025)

**Decision**: Use factory functions to generate wrapper functions instead of explicit definitions
**Context**: 48 wrapper functions (24 display + 24 dump) with identical structure, only differing in parameters
**Alternatives**: Keep explicit function definitions, use class-based approach, use higher-order functions inline

**Chosen**: Factory pattern with `createDisplayFunction` and `createDumpFunction`
**Rationale**:

- Significantly reduces code duplication (500+ lines to ~90 lines)
- Single point of maintenance for pattern changes
- API unchanged - all exports preserved identically
- Same functionality - factory returns async functions with identical behavior
- Simpler than expected in JavaScript

**Implementation**: `client/display.js` and `client/dump.js` use factory functions to generate all 48 wrapper functions.

### 14. Stream Error Handling and Resource Management (November 2025)

**Decision**: Use `finally` blocks and proper error propagation for stream cleanup
**Context**: Need to ensure streams are always closed, even on error, to prevent resource leaks
**Alternatives**: Try/catch only, manual cleanup in catch blocks, stream.destroy() only

**Chosen**: `finally` block with `streamEnded` flag to prevent double-cleanup
**Rationale**:

- Ensures cleanup always happens regardless of error path
- Prevents resource leaks from unclosed streams
- Uses `stream.destroy()` for error cases, `stream.end()` for normal cases
- Proper error propagation with custom error objects

**Implementation**: `withTempFile` and `withOptionalFileStream` use `finally` blocks with conditional cleanup based on stream state.

### 10. Todo Management: Editor Built-in Tool (October 2025)

**Decision**: Use editor's built-in todo list tool as primary task manager
**Context**: Migrated from file-based todo.md to editor's native functionality
**Alternatives**: File-only, external tools, no todo system

**Chosen**: Editor's built-in todo system
**Rationale**:

- Native integration with AI agent
- Real-time updates as work progresses
- Automatic dependency tracking
- Better UX than file-based approach
- Still git-compatible through documentation

**Implementation**: Tasks tracked in editor, documented in git commits/PRs

### 11. Configurable Test Framework (October 2025)

**Decision**: Build custom test framework instead of using external test runner
**Context**: Need flexible testing during rapid development without test framework overhead
**Alternatives**: Jest, Mocha, Tape, npm-only scripts

**Chosen**: Custom configurable test framework in `client/tests/`
**Rationale**:

- Configurable execution via TestSettings (output types, ranking types, positions)
- Preview-sized output prevents console spam during development
- Real API calls for integration validation
- No external dependencies or test framework overhead
- Easy to understand and modify
- Supports future migration to formal test framework

**Implementation**: `client/tests/` with settings-driven test execution

## Design Principles Established

### Core Architectural Principles

Node.js application for fetching and displaying fantasy football player rankings from FantasyPros API. Modular architecture with client/server/common separation of concerns.

1. **Modularity**: Single-responsibility modules with clear interfaces
2. **Configuration**: Settings-driven with sensible defaults
3. **Type Safety**: Enum patterns using Object.freeze() for immutable contracts
4. **Testability**: Comprehensive testing with configurable output
5. **Extensibility**: Architecture supports future enhancements
6. **Portability**: AI context works across tools and environments

### Code Organization Standards

**Naming Conventions**:

- Consistent function naming patterns: `displayRosQbRankings()`, `dumpWeeklyWrRankings()`
- Generate all combinations of ranking types (ROS/WEEKLY/DYNASTY/DRAFT) × positions (QB/RB/WR/TE/K/DST)
- Names tell what code does, not how it's implemented or its history

**ToString Function Design**:

- ToString functions (`playerToString()`, `playerToTabDelimitedString()`, `rankingsMetadataToString()`) contain ALL rendering logic for their context
- Callers (e.g., `displayRankings()`, `dumpRankingsToTabDelimited()`) should not need to know how to format objects
- ToString functions render objects entirely from the object's own context - if context is missing, expand the object being rendered rather than passing additional parameters
- This encapsulation makes rendering logic maintainable and consistent across the application

**Data Normalization Standards**:

- **Opponent format**: All fantasy football data sources must normalize opponent format to "vs [opponent]" for HOME games, "@ [opponent]" for AWAY games, and "BYE" for teams on their bye week
- Server-side normalization ensures consistency across all data sources (FantasyPros, future integrations)
- While primarily important for DUMP (tab-delimited output), DISPLAY also benefits from standardization

## Future Decision Points

### Pending Decisions

- **HTTP Client**: Native fetch vs axios migration
- **CLI Framework**: Commander.js vs yargs vs minimist
- **Test Runner**: npm scripts vs grunt vs gulp vs jest
- **Environment Config**: .env vs config.json vs CLI-only
- **TypeScript Migration**: Timing and approach

### Decision Criteria

- Minimal dependencies (Google Drive npm issues)
- Cross-device compatibility
- MCP GitHub server integration support
- Maintainability and clarity
- Industry standard practices

---

**Note**: This log helps maintain architectural consistency and provides context for AI development sessions across different tools and environments.
