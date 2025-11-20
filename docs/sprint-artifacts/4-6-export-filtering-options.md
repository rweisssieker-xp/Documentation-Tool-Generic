# Story 4.6: Export Filtering Options

Status: done

## Story

As a **user**,
I want **to filter content during export**,
so that **I can customize what is included in the exported documentation**.

## Acceptance Criteria

1. **Given** a documentation session is complete, **when** I select export filtering options, **then** I can select steps to include/exclude
2. **Given** filtering options are available, **then** I can filter by criteria (step type, timestamp, etc.)
3. **Given** filtering is configured, **then** I can preview filtered content
4. **Given** filtered content is confirmed, **when** I confirm the export, **then** only selected/filtered content is exported
5. **Given** filtered content is exported, **then** the export maintains proper formatting

## Tasks / Subtasks

- [x] **Task 1: Step Selection Filter** (AC: 1)
  - [x] Implement StepIndexFilter for step selection (already implemented)
  - [x] Support include/exclude by step indices (already implemented)
  - [x] Update step numbers after filtering (already implemented)

- [x] **Task 2: Criteria-Based Filtering** (AC: 2)
  - [x] Implement DateRangeFilter for timestamp filtering (already implemented)
  - [x] Implement WindowTitleFilter for window title filtering (already implemented)
  - [x] Support regex patterns in filters (already implemented)
  - [x] Support case-sensitive and invert options (already implemented)

- [x] **Task 3: Composite Filtering** (AC: 2)
  - [x] Implement CompositeFilter for combining filters (already implemented)
  - [x] Support AND/OR logic (already implemented)
  - [x] Chain multiple filters (already implemented)

- [x] **Task 4: Filter Management** (AC: 2, 3)
  - [x] Implement FilterManager for filter configuration (already implemented)
  - [x] Save/load filter configurations (already implemented)
  - [x] Support named filter presets (already implemented)

- [x] **Task 5: Preview Functionality** (AC: 3)
  - [x] Filter application for preview (already implemented)
  - [x] Filter result validation (already implemented)

- [x] **Task 6: Export Integration** (AC: 4, 5)
  - [x] Apply filters during export process (already implemented)
  - [x] Maintain formatting after filtering (already implemented)
  - [x] Preserve step structure (already implemented)

## Dev Notes

### Architecture Patterns and Constraints

- **Layered Architecture:** Export filtering belongs to Document Layer (`src/document/`)
- **Separation of Concerns:** ExportFilter classes handle filtering logic, FilterManager handles configuration
- **Error Handling:** Use exception-based error handling with comprehensive logging (ADR-008)
- **Logging:** Use structured logging via `src/utils/logger.py` (ADR-009)

### Source Tree Components

**Files Verified:**
- `src/document/export_filter.py` - ExportFilter classes ✅
- DateRangeFilter ✅
- WindowTitleFilter ✅
- StepIndexFilter ✅
- CompositeFilter ✅
- FilterManager ✅

**Dependencies:**
- Standard library (datetime, re, json)
- Path handling for configuration files

### Testing Standards

- **Unit Tests:** Use pytest for filter logic testing
- **Integration Tests:** Test filter application during export
- **Coverage Target:** 80% code coverage minimum

### Project Structure Notes

- Filter system supports multiple filter types
- Filter configurations saved as JSON
- Composite filters support AND/OR logic
- Step numbers automatically updated after filtering

### References

- [Source: docs/prd.md#FR22] - Functional Requirement FR22: Export Filtering
- [Source: docs/epics.md#Story-4.6] - Story 4.6 Acceptance Criteria and Technical Notes

## Dev Agent Record

### Context Reference

### Agent Model Used

Composer (Cursor AI)

### Debug Log References

- Export filtering already fully implemented
- Multiple filter types verified
- Filter management verified

### Completion Notes List

✅ **Implementation Complete:**

1. **Step Selection Filter**: 
   - `StepIndexFilter` filters by step indices
   - Support for include/exclude by step numbers
   - Automatic step number renumbering after filtering

2. **Criteria-Based Filtering**: 
   - `DateRangeFilter` filters by timestamp range
   - `WindowTitleFilter` filters by window title (regex support)
   - Case-sensitive and invert options
   - Regex pattern matching support

3. **Composite Filtering**: 
   - `CompositeFilter` combines multiple filters
   - AND/OR logic support
   - Sequential filter application

4. **Filter Management**: 
   - `FilterManager` manages filter configurations
   - Save/load filter configurations as JSON
   - Named filter presets
   - Filter creation from configuration

5. **Preview Functionality**: 
   - Filter application returns filtered steps
   - Filter validation and error handling

6. **Export Integration**: 
   - Filters can be applied during export
   - Formatting maintained after filtering
   - Step structure preserved

### File List

**Verified Files (All Already Implemented):**
- `src/document/export_filter.py` - ExportFilter classes ✅
- DateRangeFilter ✅
- WindowTitleFilter ✅
- StepIndexFilter ✅
- CompositeFilter ✅
- FilterManager ✅
