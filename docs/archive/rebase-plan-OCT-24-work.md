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

## Summary of Steps Taken

1. **Initial Setup**: Configured git editor (`core.editor = code --wait`) and GitLens interactive rebase editor (`sequence.editor = code --wait`)
2. **Started Interactive Rebase**: `git rebase -i d20994a` with GitLens GUI
3. **Reordered and Marked for Edit**: Moved test settings commit first, marked 931ec30 and 9f84c5e for "edit"
4. **Split Large Commit (931ec30)**: Reset commit and created 4 focused commits:
   - Server-side changes (`common/common.js`, `server/utils.js`)
   - Client display changes (`client/utils.js`)
   - Client header changes (`client/settings.js`, `client/client.js`)
   - Discarded `docs/development.md` changes (handled by later commit)
5. **Incorporated Follow-up Commit (9f84c5e)**: Created fixup commit to merge server-side refinements
6. **Resolved Merge Conflict**: Resolved conflict in `docs/development.md` when applying b2e3329
7. **Auto-squash Rebase**: Ran `git rebase -i --autosquash d20994a` to merge fixup into server commit
8. **Force Push**: `git push --force-with-lease origin main` to replace remote 931ec30

## Final Repository State

**HEAD**: 4eb5c79 (main, origin/main)

**Commits after d20994a** (7 commits total):

1. `d7ff08e` - update test settings to run all possible combinations
2. `cd6e2ac` - [Add player BYE week and opponent fields] server-side (combined 931ec30 + 9f84c5e)
3. `66ba646` - [Add player BYE week and opponent fields] client-side, display bye/opponent
4. `0ade3c9` - [Add player BYE week and opponent fields] client-side, tab-delimited headers
5. `d43016d` - indicate BYE and opponent field additions DONE
6. `7000051` - add interactive rebase plan for Oct 24 work
7. `4eb5c79` - update docs to reflect completed interactive rebase

**Original problematic commit** `931ec30` successfully replaced with focused, single-purpose commits.

## Lessons Learned

1. **GitLens Interactive Rebase GUI**: Significantly easier than text-based rebase-todo editing. Visual drag-and-drop and action buttons provide clear workflow.
2. **Terminal Integration Issues**: Cursor terminal output can break (returns empty even with exit code 0). IDE restart fixes it. Critical to verify terminal works before starting complex operations.
3. **Fixup Commits + Autosquash**: Powerful pattern for incorporating changes into earlier commits during rebase. `--autosquash` automatically positions and marks fixup commits correctly.
4. **Force Push Safety**: `--force-with-lease` is safer than `--force` - protects against accidentally overwriting others' work (though not an issue in single-developer repos).
5. **Merge Conflicts During Rebase**: Expected when reorganizing commits that touch the same files. Resolved by accepting the desired version and continuing.
6. **Documentation as Source of Truth**: Having the plan in `docs/rebase-plan-OCT-24-work.md` meant it survived context resets and provided clear reference throughout the process.
7. **PowerShell Quoting**: Git commit messages with quotes need single-quote wrapping in PowerShell to avoid parsing issues.
8. **Cursor Command Allowlist**: Be aware of auto-approved commands (Settings > Chat > Command Allowlist). Remove `git push` to ensure human review of push operations.
