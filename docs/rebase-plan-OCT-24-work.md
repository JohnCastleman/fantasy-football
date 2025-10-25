# Interactive Rebase Plan - October 24, 2025

## Goal

Reorganize recent commits (931ec30 through b2e3329) into focused, single-purpose commits following the commit message guidelines in `.cursorrules`.

## Source Commit

The large commit `931ec30 - add player BYE week and opponent fields` had this multi-line commit message that needs to be split:

- Add bye and opponent fields to PlayerRankingData
- Extract and normalize opponent in server (vs/@ format, BYE for bye weeks)
- Display bye/opponent in client ToString functions
- Add ranking-type-specific tab-delimited headers

## Target Commits

### Commit 1: Test configuration

**Files**: `client/tests/settings.js`  
**Message**: `update test settings to run all possible combinations (both DISPLAY and DUMP, all ranking types, all positions)`

### Commit 2: Server-side data model changes

**Files**: `common/common.js` + `server/utils.js` (combining all changes from 931ec30 AND 9f84c5e)  
**Message**: `[Add player BYE week and opponent fields] server-side, add BYE and opponent fields, normalizing HOME as "vs [opponent]", AWAY as "@ [opponent]", and BYE as "BYE"`

### Commit 3: Client display changes

**Files**: `client/utils.js`  
**Message**: `[Add player BYE week and opponent fields] client-side, display bye/opponent in ToString functions`

### Commit 4: Client dump/header changes

**Files**: `client/settings.js` + `client/client.js`  
**Message**: `[Add player BYE week and opponent fields] client-side, make tab-delimited header be specific to ranking type, and use during DUMP function`

### Commit 5: Documentation update

**Files**: `docs/development.md`  
**Message**: `indicate BYE and opponent field additions DONE`

## Post-Rebase Action

Force push to replace remote 931ec30 with these five commits (private repo, no other developers).

## Status

✅ **Completed** - Successfully rebased and force-pushed to origin/main.
