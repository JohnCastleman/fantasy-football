# PR #4 Implementation Plan - Code Review Responses

**PR**: [#4 - Display and Output Enhancements - Working Set 2](https://github.com/JohnCastleman/fantasy-football/pull/4)

**Status**: Code changes needed

**Review Response**: [PR Comment](https://github.com/JohnCastleman/fantasy-football/pull/4#issuecomment-3524261876)

---

## Overview

All 5 code review comments accepted. Implementation involves:

1. Code changes to address identified issues
2. Commit and push changes to PR branch
3. Verify tests pass
4. Mark resolved threads as resolved
5. Request re-review

---

## Tasks

### Critical Priority

- [x] **Fix console.log inconsistency in displayRankings**
  - **Reference**: [PR Comment r2519763069](https://github.com/JohnCastleman/fantasy-football/pull/4#discussion_r2519763069)
  - **Issue**: When writing to file, `console.log()` breaks file output consistency - message appears on stdout instead of in file
  - **Fix**: Replace `console.log()` with `outStream.write()` for the player count message
  - **File**: `client/client.js:29`
  - **Implementation**:

    Change line 29 from:

    ```javascript
    console.log('... (showing', displayMaxPlayers, 'of', players.length, 'players)');
    ```

    To:

    ```javascript
    outStream.write(`... (showing ${displayMaxPlayers} of ${players.length} players)\n`);
    ```

  - **Time**: 5 minutes

### High Priority

- [x] **Add stream error handling**
  - **Reference**: [PR Comment r2519763267](https://github.com/JohnCastleman/fantasy-football/pull/4#discussion_r2519763267)
  - **Status**: ✅ **COMPLETED**
  - **Issue**: File streams can encounter errors asynchronously (disk full, permissions, network filesystem issues). Unhandled error events can crash the process.
  - **Fix**: Add error event handler to catch stream errors asynchronously, including ENOENT (directory doesn't exist) with clear error messages
  - **File**: `client/utils.js:42-54`
  - **Implementation**:

    Uses a shared `handleStreamError` function to log errors with ENOENT detection, and tracks errors in `streamError` variable for propagation:

    ```javascript
    let streamError = null;
    
    const handleStreamError = (error) => {
      streamError = error;
      if (error.code === 'ENOENT') {
        console.error(`Directory does not exist for output file: ${outputFile}. Please create the directory first.`);
      } else {
        console.error(`Error writing to file ${outputFile}:`, error);
      }
    };
    
    if (outputFile) {
      stream = createWriteStream(outputFile);
      stream.once('error', handleStreamError);
    }
    ```

  - **Note**: This also addresses directory validation (PR Comment r2519763654) by handling ENOENT errors with clear messages. Fail-fast approach - don't auto-create directories. Uses `once` instead of `on` to prevent duplicate handlers.
  - **Time**: 15 minutes

- [x] **Wait for stream completion**
  - **Reference**: [PR Comment r2519763428](https://github.com/JohnCastleman/fantasy-football/pull/4#discussion_r2519763428)
  - **Status**: ✅ **COMPLETED**
  - **Issue**: Calling `stream.end()` doesn't guarantee data is written to disk. Function may return before all data is flushed, causing race conditions.
  - **Fix**: Wait for stream completion before reporting success
  - **File**: `client/utils.js:62-76`
  - **Implementation**:

    Uses Promise-based approach with `once` handlers to avoid duplicate error handlers:

    ```javascript
    if (stream && outputFile) {
      await new Promise((resolve, reject) => {
        if (streamError) {
          reject(streamError);
          return;
        }
        
        stream.once('finish', resolve);
        stream.once('error', (error) => {
          handleStreamError(error);
          reject(error);
        });
        stream.end();
      });
      console.info(`Output written to: ${outputFile}`);
    }
    ```

  - **Note**: Checks for `streamError` before creating Promise to handle errors that occurred during callback execution. Uses `once` instead of `on` to prevent duplicate handlers (addresses cursor bot issue).
  - **Time**: 20 minutes

### Medium Priority

- [x] **Add directory validation with clear error messages**
  - **Reference**: [PR Comment r2519763654](https://github.com/JohnCastleman/fantasy-football/pull/4#discussion_r2519763654)
  - **Status**: Combined with stream error handling task above (ENOENT error handling included in error event handler)
  - **Note**: Fail-fast approach - don't auto-create directories (that's a UX decision). Clear error messages provided when directory doesn't exist.

- [x] **Clarify displayMaxPlayers comment**
  - **Reference**: [PR Comment r2519763815](https://github.com/JohnCastleman/fantasy-football/pull/4#discussion_r2519763815)
  - **Status**: ✅ **COMPLETED**
  - **Issue**: Comment could be more explicit about null vs 0 behavior and what positive numbers mean
  - **Fix**: Update comment to be more explicit
  - **File**: `client/settings.js:5`
  - **Implementation**:

    ```javascript
    displayMaxPlayers: null, // Default number of players to show in display rankings; null or 0 = show all, o/w, show that many
    ```

  - **Note**: Comment updated to match user's preferred wording ("o/w" instead of "positive number").
  - **Time**: 2 minutes

### Post-Implementation Fixes

- [x] **Fix duplicate stream error handlers**
  - **Reference**: [Cursor Bot Comment r2520281905](https://github.com/JohnCastleman/fantasy-football/pull/4#discussion_r2520281905)
  - **Status**: ✅ **COMPLETED**
  - **Issue**: Duplicate error event handlers were registered on the stream. One handler was added at line 43, then another at line 57 inside the Promise. When a stream error occurs, both handlers fire, causing duplicate error logging and potentially confusing error handling behavior.
  - **Fix**: Use `once` instead of `on` for error handlers, and consolidate error handling logic into a shared function
  - **File**: `client/utils.js:36-87`
  - **Implementation**:

    Consolidated error handling into a shared `handleStreamError` function and use `once` handlers to prevent duplicates:

    ```javascript
    let streamError = null;
    
    const handleStreamError = (error) => {
      streamError = error;
      if (error.code === 'ENOENT') {
        console.error(`Directory does not exist for output file: ${outputFile}. Please create the directory first.`);
      } else {
        console.error(`Error writing to file ${outputFile}:`, error);
      }
    };
    
    // First handler: catches errors during callback execution
    if (outputFile) {
      stream = createWriteStream(outputFile);
      stream.once('error', handleStreamError);
    }
    
    await callback(stream || process.stdout);
    
    // Check for errors that occurred during callback
    if (streamError) {
      throw streamError;
    }
    
    // Second handler: catches errors during stream.end()
    if (stream && outputFile) {
      await new Promise((resolve, reject) => {
        if (streamError) {
          reject(streamError);
          return;
        }
        
        stream.once('finish', resolve);
        stream.once('error', (error) => {
          handleStreamError(error);
          reject(error);
        });
        stream.end();
      });
    }
    ```

  - **Key Changes**:
    - Use `once` instead of `on` for all error handlers to prevent duplicate handlers
    - Track errors in `streamError` variable for proper propagation
    - Check for errors after callback execution and before Promise creation
    - Consolidate error logging into shared `handleStreamError` function
    - Prevent duplicate error logging in catch block by checking if error is already logged
  - **Time**: 15 minutes

### Optional: Future Consideration

- [x] **Consider factory function pattern for wrapper functions**
  - **Status**: ✅ **IMPLEMENTED** (went ahead with implementation)
  - **Reference**: Reviewer suggestion (Low priority - future consideration)
  - **Issue**: All 48 wrapper functions follow the exact same pattern with only `rankingType` and `position` changing. This creates maintenance burden if the pattern needs to change.
  - **Files**: `client/display.js`, `client/dump.js`
  - **Implementation**:

    Display factory (`client/display.js`):

    ```javascript
    function createDisplayFunction(rankingType, position) {
      return async function() {
        await withOptionalFileStream({}, async (stream) => {
          const rankings = await getRankings(rankingType, position);
          displayRankings(rankings, {}, stream);
        });
      };
    }
    
    export const displayRosQbRankings = createDisplayFunction(RankingTypeEnum.ROS, PositionEnum.QB);
    // ... etc for all 24 display functions
    ```

    Dump factory (`client/dump.js`):

    ```javascript
    function createDumpFunction(rankingType, position) {
      return async function() {
        await withOptionalFileStream({}, async (stream) => {
          const rankings = await getRankings(rankingType, position);
          dumpRankingsToTabDelimited(rankings, {}, stream);
        });
      };
    }
    
    export const dumpRosQbRankings = createDumpFunction(RankingTypeEnum.ROS, PositionEnum.QB);
    // ... etc for all 24 dump functions
    ```

  - **Benefits**: Significantly reduces code duplication (500 lines → 90 lines), easier maintenance, API unchanged (all exports preserved identically)
  - **Trade-offs**: Less explicit (functions are generated rather than explicitly defined), slightly more indirection
  - **Time**: 30-60 minutes (refactoring all 48 functions)

---

## Commit Strategy

**Multiple commits** as work progressed:

1. **Implementation plan commit**:

   ```text
   Add PR #4 implementation plan
   ```

2. **Code review fixes commit**:

   ```text
   Fix code review issues from PR #4

   - Fix console.log inconsistency in displayRankings
   - Add stream error handling in withOptionalFileStream (includes directory validation)
   - Wait for stream completion before reporting success
   - Clarify displayMaxPlayers comment

   Addresses PR review comments:
   - r2519763069 (console.log inconsistency)
   - r2519763267 (stream error handling)
   - r2519763428 (stream completion)
   - r2519763654 (directory validation - combined with stream error handling)
   - r2519763815 (comment clarity)
   ```

3. **Factory pattern implementation commit**:

   ```text
   Refactor display and dump functions to use factory pattern

   - Replace 48 individual function definitions with factory functions
   - createDisplayFunction and createDumpFunction reduce code duplication
   - API unchanged - all exports preserved identically
   - Reduces maintenance burden when pattern needs to change

   Implements optional factory pattern suggestion from PR review
   ```

4. **Post-implementation fix commit** (pending):

   ```text
   Fix duplicate stream error handlers in withOptionalFileStream

   - Use once instead of on for error handlers to prevent duplicates
   - Consolidate error handling into shared handleStreamError function
   - Track errors in streamError variable for proper propagation
   - Check for errors after callback execution and before Promise creation
   - Prevent duplicate error logging in catch block

   Addresses cursor bot comment r2520281905
   ```

---

## Verification

After implementation:

1. **Run tests**: `npm test`
2. **Verify file output**: Test with `outputFile` setting - verify all output goes to file (no console.log leaks)
3. **Test error handling**: Test with non-existent directories, permission errors
4. **Test stream completion**: Verify success message appears after data is written
5. **Lint check**: Verify no new linting errors
6. **Manual testing**: Test all combinations of outputFile (null vs file) and verify consistency

---

## Status

**IN PROGRESS** - Original review issues fixed, new issues identified from Copilot Pro and cursor bot

### Implementation Summary

- ✅ **Critical**: Fixed console.log inconsistency in displayRankings
- ✅ **High**: Added stream error handling with ENOENT detection
- ✅ **High**: Implemented stream completion waiting
- ✅ **Medium**: Added directory validation (combined with error handling)
- ✅ **Medium**: Clarified displayMaxPlayers comment
- ✅ **Optional**: Implemented factory pattern for wrapper functions
- ✅ **Post-Implementation**: Fixed duplicate stream error handlers

### Outstanding Issues Summary

- 🔍 **HIGH**: Resource leak in error handling (cursor bot + Copilot Pro)
- 🔍 **HIGH**: Path sanitization missing (Copilot Pro)
- 🔍 **HIGH**: Directory creation missing (Copilot Pro)
- 📋 **MEDIUM**: Atomic writes not implemented (Copilot Pro)
- 📋 **MEDIUM**: Console logging in helper (Copilot Pro)
- 📋 **MEDIUM**: Options forwarding in wrappers (Copilot Pro)
- 📋 **LOW**: Newline at EOF, precedence documentation, outputOverwrite setting (Copilot Pro)
- 📋 **DEFERRED**: Tests and CLI documentation (Copilot Pro)

### Review Status

- **Initial Review**: All 5 issues identified and addressed
- **Follow-Up Review**: All issues resolved, design intent clarified for TSV title/metadata behavior
- **Final Review**: ✅ **APPROVED** - All critical and high-priority issues resolved (from original review)
- **Cursor Bot Review**:
  - ✅ Duplicate error handler issue identified and fixed (r2520281905)
  - 🔍 Resource leak issue identified, under evaluation (r2520354116)
- **GitHub Copilot Pro Review**: ✅ **REVIEWED** - 15+ issues identified, 6 addressed, 9+ remain unaddressed

### Additional Review Feedback

**Summary**: After fixing the original 5 review issues, two additional reviews identified more issues:

- **Cursor Bot**: 1 new issue (resource leak in error handling)
- **GitHub Copilot Pro**: 15+ issues from original PR branch state (6 already addressed, 9+ still relevant)

**Priority Assessment**:

- **HIGH** (Fix Before Merge): Resource leak, path sanitization, directory creation
- **MEDIUM** (Consider for This PR): Atomic writes, options forwarding, console logging refactor
- **LOW** (Follow-up): Newline at EOF, precedence documentation, outputOverwrite setting
- **DEFERRED** (Separate PR): Tests, CLI documentation

#### Cursor Bot - New Issue

- [ ] **Fix stream error handling resource leak**
  - **Reference**: [Cursor Bot Comment r2520354116](https://github.com/JohnCastleman/fantasy-football/pull/4#discussion_r2520354116)
  - **Status**: 🔍 **UNDER REVIEW**
  - **Severity**: 🟠 **HIGH** (Resource leak)
  - **Issue**: Resource leak in error handling - when a stream error occurs during callback execution, the catch block checks `!streamError` before calling `stream.end()`, which prevents the stream from being closed if there's an error. File streams that encounter errors still hold open file handles and need to be explicitly closed or destroyed to release system resources.
  - **Location**: `client/utils.js:78-81`
  - **Current Code**:

    ```javascript
    catch (error) {
      if (stream && outputFile && !streamError) {
        stream.end();
      }
      if (error !== streamError) {
        console.error(`Error writing output:`, error);
      }
      throw error;
    }
    ```

  - **Problem**:
    - If `streamError` is set (error occurred during callback), the condition `!streamError` is false, so `stream.end()` is not called
    - This leaves the stream open, causing a resource leak (file handle not released)
    - Streams in error state may not be safely closed with `end()` - may need `destroy()` instead
  - **Analysis**:
    - **Scenario 1**: Error occurs during callback execution → `streamError` is set → `!streamError` is false → `stream.end()` is not called → **RESOURCE LEAK**
    - **Scenario 2**: Error occurs during `stream.end()` → Promise rejects → `streamError` is set → `!streamError` is false → `stream.end()` is not called → **RESOURCE LEAK** (though stream is already ending)
    - **Scenario 3**: No error occurs → `streamError` is null → `!streamError` is true → `stream.end()` is called → **OK** (but this path should never be reached in catch block if no error)
  - **Suggested Fix**:
    - Always attempt cleanup regardless of error state
    - Use `stream.destroy()` for error cases (more appropriate for errored streams)
    - Use `stream.end()` only for successful cases
    - Consider using `finally` block to ensure cleanup always happens
  - **Potential Solution**:

    ```javascript
    catch (error) {
      if (stream && outputFile) {
        if (streamError) {
          // Stream is in error state - use destroy() to force cleanup
          stream.destroy();
        } else {
          // No stream error - try to close normally
          stream.end();
        }
      }
      if (error !== streamError) {
        console.error(`Error writing output:`, error);
      }
      throw error;
    }
    ```

  - **Chosen Solution** (using finally, per user request):

    ```javascript
    let stream = null;
    let streamError = null;
    try {
      // ... stream creation and callback ...
    } catch (error) {
      // ... error handling ...
      throw error;
    } finally {
      if (stream && outputFile) {
        if (streamError || stream.destroyed) {
          stream.destroy();
        } else {
          stream.end();
        }
      }
    }
    ```

  - **Note**: Review Copilot's suggestion (Untitled-1) for `finished()` from `stream/promises` approach before implementing
  - **Evaluation**:
    - Is this a valid issue? **YES** - Resource leak is a real problem
    - Should we use `stream.destroy()` for error cases? **YES** - More appropriate for errored streams
    - Should we always attempt cleanup regardless of error state? **YES** - Resources must be released
    - Should we use `finally` block? **YES** - User requested, ensures cleanup always happens
  - **Priority**: 🟠 **HIGH** - Resource leaks can cause file handle exhaustion
  - **Time**: 15-30 minutes (depending on approach)

#### GitHub Copilot Pro - Original PR Branch Review

- [x] **Review GitHub Copilot Pro feedback**
  - **Reference**: [GitHub Copilot Share](https://github.com/copilot/share/0a3513b8-0a60-8853-8002-28002049081d)
  - **Status**: ✅ **REVIEWED**
  - **Note**: This feedback is from 2 weeks ago, when the PR branch was first created. All feedback is related to the state of the original PR branch, not the current state.
  - **Context**:
    - Feedback was provided during free trial period
    - Provided before current fixes were implemented
    - Based on original PR branch state (commit `025e59719ebad7530ecf14a5ef5200bce01f47f2`)
    - Many issues have been addressed by subsequent fixes
  - **Evaluation Summary**:
    - **Total Issues Identified**: 15+ issues across 5 files
    - **Issues Addressed**: 6 issues fixed in subsequent commits
    - **Issues Still Relevant**: 9+ issues remain unaddressed
    - **Priority Issues**: Path sanitization, directory creation, atomic writes, resource leaks

  - **Issues Already Addressed**:
    - ✅ **Console.log inconsistency** → Fixed (commit `b74a664`) - `displayRankings` now uses `outStream.write()` for all output
    - ✅ **Stream error handling** → Fixed (commit `b74a664`) - Error handlers added with ENOENT detection
    - ✅ **Stream completion waiting** → Fixed (commit `b74a664`) - Promise-based waiting for stream finish
    - ✅ **Directory validation** → Partially fixed (commit `b74a664`) - ENOENT error handling with clear messages
    - ✅ **Comment clarity** → Fixed (commit `b74a664`) - `displayMaxPlayers` comment updated
    - ✅ **Duplicate error handlers** → Fixed (commit `b9acb32`) - Using `once` handlers and shared error function

  - **Issues Still Relevant** (by file):

    **client/utils.js:**
    - [ ] **Path sanitization** - No `path.resolve()` used, no path traversal prevention
      - **Project Constraint**: Basic location sanity checking (only add "calling folder or child folders" check if it makes implementation easier)
    - [ ] **Directory validation** - No check to ensure parent directory exists before writing
      - **Project Constraint**: Require target folder to exist (error/throw, don't create)
    - [ ] **Atomic writes** - No temp file + rename pattern, partial files could be left on failure
      - **Project Constraint**: Always overwrite (no setting needed)
      - **Note**: Implementation approach needs discussion before starting
    - [ ] **Console logging in helper** - `console.info`/`console.error` side effects in utility function
    - [ ] **Newline at EOF** - File may end without trailing newline
    - [ ] **Resource leak** - Stream not closed when error occurs (cursor bot issue, overlaps with this)

    **client/display.js and client/dump.js:**
    - [ ] **Empty options object** - Wrappers pass `{}` to `withOptionalFileStream`, preventing per-call overrides
    - [ ] **Options forwarding** - CLI options not forwarded through wrapper functions

    **client/settings.js:**
    - [x] **Precedence documentation** - ✅ **ALREADY DOCUMENTED** in `docs/plans/cli-parameter-overrides.md`
    - [x] **outputOverwrite setting** - ✅ **NOT NEEDED** - Project decision: always overwrite

    **Tests & Documentation:**
    - [x] **File output tests** - ✅ **IN BACKLOG** - See `docs/development.md`
    - [x] **CLI usage documentation** - ✅ **IN BACKLOG** - See `docs/plans/cli-parameter-overrides.md`
    - [x] **Error path tests** - ✅ **IN BACKLOG** - Part of overall testing strategy

  - **Priority Assessment**:
    - 🟠 **HIGH**: Resource leak fix, path sanitization (with project constraints)
    - 🟡 **MEDIUM**: Atomic writes (needs discussion), options forwarding, console logging in helper
    - 🟢 **LOW**: Newline at EOF
    - 📋 **DEFERRED**: Tests, CLI documentation (already in project backlog)

  - **Project Constraints** (from discussion):
    - **Always overwrite**: No setting needed, always overwrite existing files
    - **Require folder to exist**: Error/throw if parent directory doesn't exist (don't create)
    - **Path validation**: Basic location sanity checking (only add "calling folder or child folders" check if it makes implementation easier)
    - **Atomic writes**: Will be implemented, but approach needs discussion first

  - **Recommended Implementation Order** (matches user request):
    1. **Phase 1: utils.js fixes** (in order, separate commits):
       - Resource leak fix (use `finally` block)
       - Path sanitization and validation (with project constraints)
       - Atomic writes (after discussion)
       - Console logging refactor
       - Newline at EOF
    2. **Phase 2: Options forwarding**:
       - Add options parameter to wrapper functions

  - **Time Estimate**:
    - Phase 1 (utils.js fixes): 2-3 hours
    - Phase 2 (options forwarding): 30 minutes
    - Phase 3 (follow-up): 10 minutes

### Remaining Tasks

#### Implementation Order

### Phase 1: utils.js fixes (in order, separate commits)

1. [ ] **Fix resource leak in error handling**
   - **Reference**: Cursor Bot r2520354116 + Copilot Pro feedback
   - **Status**: 🔍 **UNDER REVIEW**
   - **Issue**: Stream not closed when error occurs during callback execution
   - **Fix**: Use `finally` block to ensure stream cleanup always happens. Use `stream.destroy()` for error cases, `stream.end()` for normal cases
   - **Note**: Review Copilot's suggestion (Untitled-1) for `finished()` from `stream/promises` approach
   - **Time**: 15-30 minutes

2. [ ] **Add path sanitization and validation**
   - **Reference**: Copilot Pro feedback + project constraints
   - **Status**: 📋 **PENDING**
   - **Issue**: No `path.resolve()` used, no path traversal prevention
   - **Constraints** (from project discussion):
     - Require target folder to exist (error/throw, don't create)
     - Basic location sanity checking (only add "calling folder or child folders" check if it makes implementation easier, otherwise just basic path validation)
   - **Fix**:
     - Use `path.resolve()` to sanitize paths
     - Basic path validation (prevent obvious path traversal, validate path structure)
     - If checking for "calling folder or child folders" makes implementation easier, add that check; otherwise skip it
     - Verify parent directory exists before creating stream (throw error if missing)
   - **Time**: 45 minutes

3. [ ] **Add atomic write strategy**
   - **Reference**: Copilot Pro feedback
   - **Status**: 📋 **PENDING - NEEDS DISCUSSION**
   - **Issue**: No temp file + rename pattern, partial files could be left on failure
   - **Note**: Implementation approach needs discussion before starting
   - **Constraints** (from project discussion):
     - Always overwrite (no setting needed)
   - **Fix**: Write to temp file in same directory, then rename atomically on success. Clean up temp file on error.
   - **Time**: 45 minutes (after discussion)

4. [ ] **Refactor console logging in helper**
   - **Reference**: Copilot Pro feedback
   - **Status**: 📋 **PENDING**
   - **Issue**: `console.info`/`console.error` side effects in utility function
   - **Fix**: Consider returning metadata or throwing errors, let caller handle logging. Evaluate if logging should stay in helper for consistency.
   - **Time**: 30 minutes

5. [ ] **Add newline at EOF**
   - **Reference**: Copilot Pro feedback
   - **Status**: 📋 **PENDING**
   - **Issue**: File may end without trailing newline
   - **Fix**: Ensure trailing newline when writing files
   - **Time**: 10 minutes

### Phase 2: Options forwarding

1. [ ] **Add options forwarding in wrapper functions**
   - **Reference**: Copilot Pro feedback
   - **Status**: 📋 **PENDING**
   - **Issue**: Wrappers pass `{}` to `withOptionalFileStream`, preventing per-call overrides
   - **Fix**: Accept options parameter in wrapper functions (display.js and dump.js), forward to helper
   - **Time**: 30 minutes

#### Deferred (Already in Project Backlog)

**Note**: These items are already planned in the project backlog and should be addressed as part of those planned features, not in this PR.

- [x] **Document precedence in settings**
  - **Reference**: Copilot Pro feedback
  - **Status**: ✅ **ALREADY DOCUMENTED** in `docs/plans/cli-parameter-overrides.md` (lines 82-94)
  - **Issue**: No documentation of precedence (Settings < CLI flags < call-level options)
  - **Resolution**: Precedence is documented in CLI parameter overrides plan (CLI > Settings > Built-in Default). This will be implemented when CLI parameters are added (separate PR).

- [x] **Add outputOverwrite setting**
  - **Reference**: Copilot Pro feedback
  - **Status**: ✅ **NOT NEEDED** - Project decision: always overwrite (no setting needed)
  - **Issue**: No `outputOverwrite`/`allowOverwrite` setting documented
  - **Resolution**: Project constraint: always overwrite files. No setting needed.

- [x] **Add file output tests**
  - **Reference**: Copilot Pro feedback
  - **Status**: ✅ **IN BACKLOG** - See `docs/development.md` (Testing Strategy section)
  - **Issue**: No unit/integration tests for file output scenarios
  - **Resolution**: Tests are planned as part of overall testing strategy. Will be added when test framework is enhanced.

- [x] **Add CLI usage documentation**
  - **Reference**: Copilot Pro feedback
  - **Status**: ✅ **IN BACKLOG** - See `docs/plans/cli-parameter-overrides.md`
  - **Issue**: No CLI usage docs showing `--output-file` usage and default behavior
  - **Resolution**: CLI documentation is planned as part of CLI parameter overrides implementation (separate PR).

### Next Steps

1. **Evaluate priorities** - Review high-priority issues and determine which to address in this PR
2. **Implement high-priority fixes** - Fix resource leak, path sanitization, directory creation
3. **Consider medium-priority fixes** - Evaluate if atomic writes and options forwarding should be in this PR
4. **Defer low-priority and tests** - Move to separate PR or follow-up work
5. **Update PR with fix explanations** - Document what was fixed and what was deferred
6. **Request final re-review** - After high-priority fixes are implemented
