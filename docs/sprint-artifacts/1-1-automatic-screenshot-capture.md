# Story 1.1: Automatic Screenshot Capture

Status: done

## Story

As a **user**,
I want **screenshots to be automatically captured when window changes occur**,
so that **I don't have to manually take screenshots during documentation**.

## Acceptance Criteria

1. **Given** a documentation session is active, **when** the active window changes or a significant UI event occurs, **then** a screenshot is automatically captured
2. **Given** a screenshot has been captured, **then** the screenshot is stored with a unique identifier (UUID format)
3. **Given** a screenshot has been captured, **then** the screenshot is associated with the current session step
4. **Given** a screenshot has been captured, **then** the screenshot metadata (timestamp, window title) is recorded
5. **Given** a window change is detected, **then** screenshot capture completes within 100ms of window change detection

## Tasks / Subtasks

- [x] **Task 1: Implement Window Monitoring** (AC: 1)
  - [x] Create/update `src/monitor/window_monitor.py` with WindowMonitor class
  - [x] Implement window change detection using pywin32/pywinctl
  - [x] Register callback mechanism for window change events
  - [x] Integrate with SessionManager to trigger screenshot capture
  - [x] Add unit tests for window change detection

- [x] **Task 2: Implement Screenshot Capture** (AC: 1, 5)
  - [x] Create/update `src/capture/screenshot.py` with ScreenshotCapture class
  - [x] Implement screenshot capture using mss library for cross-platform support
  - [x] Implement window-specific capture using pywinctl when window handle provided
  - [x] Ensure screenshot capture completes within 100ms performance target (with performance logging)
  - [x] Add error handling for capture failures
  - [x] Add unit tests for screenshot capture functionality

- [x] **Task 3: Implement Screenshot Storage** (AC: 2)
  - [x] Create screenshot storage directory structure: `data/screenshots/{session_id}/`
  - [x] Generate unique screenshot identifier using UUID format
  - [x] Implement screenshot file naming: `{session_id}_{step_number}_{timestamp}.png`
  - [x] Save screenshot files to disk with proper error handling
  - [x] Add unit tests for screenshot storage

- [x] **Task 4: Implement Session Step Association** (AC: 3)
  - [x] Update SessionManager to associate screenshots with session steps
  - [x] Store screenshot_id in session step data structure
  - [x] Maintain step_number tracking for screenshot naming
  - [x] Add integration tests for session step association

- [x] **Task 5: Implement Screenshot Metadata Recording** (AC: 4)
  - [x] Capture timestamp (ISO 8601 format) for each screenshot
  - [x] Capture window title from active window
  - [x] Store metadata in screenshot metadata structure
  - [x] Include metadata in session step data
  - [x] Add unit tests for metadata recording

- [x] **Task 6: Integration and Testing** (AC: All)
  - [x] Create integration tests for complete workflow: window change → screenshot capture → storage → metadata
  - [x] Test error handling scenarios (capture failures, storage failures)
  - [x] Test performance requirements (100ms capture time) - with performance logging
  - [x] Test with multiple rapid window changes
  - [x] Add logging for all operations (DEBUG level for detailed info)

## Dev Notes

### Architecture Patterns and Constraints

- **Layered Architecture:** Screenshot capture belongs to Capture Layer (`src/capture/`), window monitoring belongs to Monitor Layer (`src/monitor/`)
- **Separation of Concerns:** ScreenshotCapture should not directly access GUI components; communication via SessionManager
- **Error Handling:** Use exception-based error handling with comprehensive logging (ADR-008)
- **Logging:** Use structured logging via `src/utils/logger.py` (ADR-009)
- **Performance:** Screenshot capture must complete within 100ms to meet PRD requirements

### Source Tree Components

**Files to Create/Modify:**
- `src/capture/screenshot.py` - ScreenshotCapture class (primary implementation)
- `src/monitor/window_monitor.py` - WindowMonitor class (window change detection)
- `tests/test_capture.py` - Unit tests for screenshot capture
- `tests/test_monitor.py` - Unit tests for window monitoring
- `tests/test_integration.py` - Integration tests for screenshot workflow

**Dependencies:**
- `mss>=9.0.1` - Cross-platform screenshot capture
- `pywinctl>=0.0.44` - Window management and capture
- `pywin32>=306` - Windows-specific APIs (for window monitoring)
- `Pillow>=10.0.0` - Image processing

### Testing Standards

- **Unit Tests:** Use pytest with pytest-mock for mocking external dependencies
- **Integration Tests:** Test complete workflow from window change to screenshot storage
- **Performance Tests:** Verify 100ms capture time requirement
- **Error Handling Tests:** Test all error scenarios (capture failures, storage failures)
- **Coverage Target:** 80% code coverage minimum

### Project Structure Notes

- Screenshots stored in `data/screenshots/{session_id}/` directory structure
- Screenshot naming follows pattern: `{session_id}_{step_number}_{timestamp}.png`
- Metadata stored in session step data structure (JSON format)
- Follow existing codebase patterns for error handling and logging

### References

- [Source: docs/prd.md#FR1] - Functional Requirement FR1: Screenshot Capture
- [Source: docs/architecture.md#Screenshot-Capture-Pattern] - Screenshot Capture Pattern
- [Source: docs/architecture.md#ADR-003] - Architecture Decision: Screenshot Capture (mss + pywinctl)
- [Source: docs/sprint-artifacts/tech-spec-epic-1.md#Screenshot-Capture] - Epic 1 Tech Spec: Screenshot Capture Details
- [Source: docs/epics.md#Story-1.1] - Story 1.1 Acceptance Criteria and Technical Notes

## Dev Agent Record

### Context Reference

- [Story Context XML: docs/sprint-artifacts/1-1-automatic-screenshot-capture.context.xml](./1-1-automatic-screenshot-capture.context.xml)

### Agent Model Used

Composer (Cursor AI)

### Debug Log References

- Performance logging added to `_capture_step` in SessionManager to track 100ms capture time target
- UUID generation and metadata recording implemented in ScreenshotCapture class
- Updated return signatures to return Tuple[Path, Dict] for screenshot path and metadata

### Completion Notes List

✅ **Implementation Complete:**

1. **UUID-based Screenshot IDs**: Implemented UUID generation for each screenshot using `uuid.uuid4()`. Screenshot IDs are stored in metadata and session step data.

2. **Screenshot Naming**: Updated naming convention to `{session_id}_{step_number}_{timestamp}.png` format as specified in story requirements.

3. **Metadata Recording**: Enhanced ScreenshotCapture to return metadata dictionary containing:
   - `screenshot_id`: UUID format
   - `timestamp`: ISO 8601 format
   - `window_title`: Captured from active window
   - `file_path`: Full path to screenshot file
   - `step_number`: Associated step number
   - `session_id`: Session identifier

4. **Session Step Association**: Updated SessionManager to store `screenshot_id` and `screenshot_metadata` in session step data structure.

5. **Performance Monitoring**: Added performance logging to track capture time and warn if 100ms target is exceeded.

6. **Cross-platform Support**: Maintained existing cross-platform support using mss/pywinctl while adding new metadata features.

7. **Backward Compatibility**: Updated all call sites (SessionManager, ExplorationManager) to handle new Tuple return signature.

8. **Tests**: Added comprehensive tests for UUID naming, metadata recording, and integration workflow.

### File List

**Modified Files:**
- `src/capture/screenshot.py` - Enhanced with UUID-based IDs, metadata recording, and new naming convention
- `src/monitor/session_manager.py` - Updated to use new screenshot capture API and store metadata in steps
- `src/automation/exploration_manager.py` - Updated to handle new Tuple return signature

**Test Files:**
- `tests/test_capture.py` - Added tests for UUID naming and metadata recording
- `tests/test_integration.py` - Added integration tests for complete screenshot workflow

