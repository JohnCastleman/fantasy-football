# Command Usage History

This file tracks commands and tools used during development sessions for reference and reproducibility.

## 2025-10-23 — Housekeeping: Migration to Portable AI Context

- **Date**: 2025-10-23
- **Task**: Migrated from editor-specific folders to portable documentation
- **Actions**:
  - Created `.cursorrules` with AI development guidelines
  - Created `docs/architecture.md` (from `decisions-log.md`)
  - Created `docs/development.md` (from `active-context.md`)
  - Created `docs/command-history.md` (this file, from `tool-usage-log.md`)
  - Moved API samples to `docs/api-samples/`
  - Updated references to use neutral terminology
  - Migrated MCP configuration to `.cursor/mcp.json`
  - Fixed markdown linting issues across all documentation files

---

## 2025-10-09 — Test Runner: WEEKLY K and DST Tab-Delimited Output

- **Date**: 2025-10-09
- **Test Settings**: DUMP, rankingType=WEEKLY, positions=[K, DST]
- **Command** (from project root):

```powershell
clear; $env:NODE_PATH = "C:\Users\johnc\AppData\Roaming\npm\node_modules"; node ".\code\client\tests\index.js" > ".\code\client\tests\output\tmp_runner_output.txt"
```

- **Output**: Captured stdout to `code/client/tests/output/tmp_runner_output.txt`
- **Processing**: Created `tmp_runner_output_tabs.txt` with explicit tab separators for spreadsheet import (TSV)
- **Cleanup**: Both temp files removed after verification

---

## 2025-10-08 — Test Runner: ROS K and DST Tab-Delimited Lists

- **Date**: 2025-10-08
- **Test Settings**: DUMP, rankingType=ROS, positions=[K, DST]
- **Command** (from project root):

```powershell
clear; $env:NODE_PATH = "C:\Users\johnc\AppData\Roaming\npm\node_modules"; node ".\code\client\tests\index.js"
```

- **Output**: Copied terminal output to scratchpad for tab character manipulation
- **Processing**: Updated content for use in external tools
- **Cleanup**: Temp scratchpad file discarded after use

---

## Common Commands Reference

### Run Tests

```powershell
# Set API key (required)
$env:FANTASYPROS_API_KEY = "your_api_key_here"

# Standard test run
npm test

# Manual test run with NODE_PATH
$env:NODE_PATH = "C:\Users\johnc\AppData\Roaming\npm\node_modules"
node "client\tests\index.js"

# Capture output to file
node "client\tests\index.js" > output.txt
```

### Clear Console Before Test

```powershell
clear; npm test
```

### Git Operations

```powershell
# Check status
git status

# Create feature branch
git checkout -b feature/branch-name

# Commit changes  
git add .
git commit -m "description"

# Push to remote
git push origin branch-name
```

---

**Note**: This log helps reproduce development workflows and understand command patterns used across sessions.
