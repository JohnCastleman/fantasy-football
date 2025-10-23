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

### 7. Google Drive + Git Hybrid Approach (October 2025)
**Decision**: Local development with GitHub sync, Google Drive as backup
**Context**: Google Drive incompatible with npm packages
**Options**: Full Google Drive, full local, hybrid approach

**Chosen**: Hybrid - local development, GitHub primary, Google Drive backup
**Rationale**:
- Unlocks npm ecosystem
- Enables proper version control
- Maintains Google Drive convenience
- Supports MCP GitHub integration
- Cross-device synchronization

**Implementation**: `C:\temp\fantasy-football\` → GitHub → Google Drive sync

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

**Implementation**: `.ai-context/` folder with structured documentation

### 9. Todo Management: File + Tool Hybrid Strategy (October 2025)
**Decision**: Use `todo.md` as source of truth with VS Code todo list tool as write-through cache
**Context**: Need persistent git-synced tasks + convenient tool interface for active sessions
**Alternatives**: File-only, tool-only, separate systems

**Chosen**: Hybrid write-through cache pattern
**Rationale**:
- `todo.md`: Persistent source of truth, git-synced, cross-device accessible
- Chat todo tool: Transient cache for session convenience and UI benefits
- Write-through: All new tasks added to both simultaneously
- Sync strategy: Load from `todo.md` at session start if time gap exists
- Diff/merge: Handle conflicts when `todo.md` modified externally

**Implementation Strategy**:
- Session start: Check if sync needed, load `todo.md` → tool
- New tasks: Write-through to both `todo.md` and tool simultaneously  
- External changes: Detect diffs, merge conflicts intelligently
- Cross-device: GitHub sync ensures `todo.md` consistency

## Design Principles Established

1. **Modularity**: Single-responsibility modules with clear interfaces
2. **Configuration**: Settings-driven with sensible defaults
3. **Type Safety**: Enum patterns for contract clarity
4. **Testability**: Comprehensive testing with configurable output
5. **Extensibility**: Architecture supports future enhancements
6. **Cross-Device**: Git-based context for multi-device development

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

**Note**: This log helps maintain architectural consistency and provides context for future AI development sessions via MCP GitHub integration.