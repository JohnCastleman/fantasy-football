# Fantasy Football Rankings - Task Management

**Last Updated**: October 5, 2025 at 3:45 PM CT  
**Current Focus**: Architectural refactoring complete, planning git migration

## Active Development Tasks

### 🚀 High Priority (Next Up)

- [ ] **Task #8**: Migrate to local folder with git and npm support
  - **Context**: Unlock npm ecosystem, enable proper dependency management
  - **Blockers**: Need to preserve Google Drive sync while moving dev environment local
  - **Next Steps**: Copy code to C:\temp\fantasy-football, init git, setup GitHub remote

- [ ] **Task #7**: Secure API key configuration  
  - **Context**: Replace hardcoded fantasyprosApiKey with environment variables
  - **Options**: .env file, config.json, or CLI argument approach
  - **Dependencies**: Best done after git migration

### 🔧 Development Infrastructure  

- [ ] **Task #12**: Update package.json for new architecture
  - **Context**: Current package.json references legacy monolithic structure
  - **Required**: Update entry points, scripts, dependencies for modular structure

- [ ] **Task #13**: Add standard npm test and task runner scripts
  - **Context**: Implement proper npm test practices with grunt/gulp-style runners
  - **Benefits**: Streamlined development workflow, automated testing

- [ ] **Task #14**: Implement MCP GitHub integration for cross-device AI context
  - **Context**: Enable Claude on phone to access repository, manage tasks, create branches
  - **Strategy**: Replace VS Code todo with git-based task management
  - **Benefits**: True cross-device AI development workflow

### 📊 Feature Development

- [ ] **Task #5**: Explore options for handling tab-delimited program output
  - **Context**: Route dump function output to files for spreadsheet import
  - **Previous Approach**: PowerShell stdout redirection: `node code/index.js | Out-File -FilePath rankings.tsv -Encoding UTF8`
  - **Discussion**: Explored console.log for tab-delimited content vs console.error/info/warn for headers/extra content, then stdout redirection. This approach: 1) is not ideal, 2) still needs testing and acceptance as part of exploration phase
  - **Status**: Needs further evaluation of console stream separation approach

- [ ] **Task #6**: Add previewSize and verbose CLI options
  - **Context**: Command-line arguments to override Settings defaults
  - **Dependencies**: Requires CLI argument parsing infrastructure

### 🔮 Future Enhancements

- [ ] **Task #9**: Return more player data and verbose playerToString
  - **Context**: FantasyPros API returns dozens of columns, currently using only 3
  - **Benefit**: Richer player analysis and detailed rankings
  - **Samples**: Raw API responses are archived under `code/.ai-context/samples/` for reproducibility. Example: `code/.ai-context/samples/fantasypros-ROS(W7)-K.json` contains the full FantasyPros ROS (pre-week7 2025) K payload captured during testing.

- [ ] **Task #10**: Port JS to TypeScript
  - **Priority**: Lower - architectural enhancement for type safety
  - **Dependencies**: Complete after core functionality stabilized

- [ ] **Task #11**: Preserve AI conversation context in repository
  - **Context**: Export conversations, establish documentation structure
  - **Status**: Partially addressed with this .ai-context/ structure

## ✅ Completed Tasks

### Phase 1: Architectural Refactoring (Complete)

- [x] **Task #1**: Separate display and dump code flows ✅
- [x] **Task #2**: Expand display and dump with DYNASTY and DRAFT ✅  
- [x] **Task #3**: Configure test runs with ClientSettings ✅
- [x] **Task #4**: Split JS into common, server, client files ✅

**Achievement**: Successfully transformed monolithic 500+ line file into clean modular architecture with 24 ranking function combinations across 4 ranking types and 6 positions.

## 🎯 Development Notes

**Current State**: Clean modular architecture, all tests passing, comprehensive README
**Architecture**: client/ server/ common/ structure with proper separation of concerns  
**Testing**: Configurable test framework with preview-sized output
**Next Milestone**: Git migration to unlock npm ecosystem and enable MCP GitHub integration

## 🚧 Known Issues & Workarounds

1. **Google Drive + npm incompatibility**: Using NODE_PATH env var workaround
2. **Hardcoded API key**: Security risk, needs environment variable solution  
3. **Manual context preservation**: MCP GitHub integration will solve cross-device workflow
