# Story 6.2: Intelligent Step Consolidation

Status: done

## Story

As a **user**,
I want **similar documentation steps to be automatically consolidated**,
so that **my documentation is concise and avoids redundancy**.

## Acceptance Criteria

1. **Given** a documentation session has multiple steps, **when** intelligent consolidation is triggered, **then** similar steps are identified
2. **Given** similar steps are identified, **then** consolidation suggestions are provided
3. **Given** consolidation is confirmed, **then** similar steps are merged
4. **Given** steps are merged, **then** merged descriptions are generated using AI
5. **Given** consolidation completes, **then** the documentation is updated with consolidated steps

## Tasks / Subtasks

- [x] **Task 1: Similarity Detection** (AC: 1)
  - [x] Implement StepConsolidator class (already implemented)
  - [x] Detect similar steps (already implemented)
  - [x] Calculate step similarity (already implemented)
  - [x] Identify consolidation candidates (already implemented)

- [x] **Task 2: Consolidation Suggestions** (AC: 2)
  - [x] Generate consolidation suggestions (already implemented)
  - [x] Show similarity scores (already implemented)
  - [x] Provide merge preview (already implemented)

- [x] **Task 3: Step Merging** (AC: 3)
  - [x] Merge similar steps (already implemented)
  - [x] Combine step metadata (already implemented)
  - [x] Update step numbers (already implemented)

- [x] **Task 4: AI Description Merging** (AC: 4)
  - [x] Generate merged descriptions using AI (already implemented)
  - [x] Use OpenAI API for merging (already implemented)
  - [x] Preserve essential information (already implemented)

- [x] **Task 5: Documentation Update** (AC: 5)
  - [x] Update session steps (already implemented)
  - [x] Refresh preview (already implemented)
  - [x] Maintain step integrity (already implemented)

## Dev Notes

### Architecture Patterns and Constraints

- **Layered Architecture:** Step consolidation belongs to AI Layer (`src/ai/`)
- **Separation of Concerns:** StepConsolidator handles consolidation logic, AI handles description merging
- **Error Handling:** Use exception-based error handling with comprehensive logging (ADR-008)
- **Logging:** Use structured logging via `src/utils/logger.py` (ADR-009)

### Source Tree Components

**Files Verified:**
- `src/ai/step_consolidator.py` - StepConsolidator class ✅
- Similarity detection ✅
- Step merging ✅
- AI description merging ✅

**Dependencies:**
- OpenAI API for description merging
- Image comparison for screenshot similarity

### Testing Standards

- **Unit Tests:** Use pytest with pytest-mock for mocking AI calls
- **Integration Tests:** Test complete consolidation workflow
- **Coverage Target:** 80% code coverage minimum

### Project Structure Notes

- StepConsolidator detects similar steps
- Similarity calculated using multiple criteria (screenshot, description, window title)
- AI merges descriptions when consolidating

### References

- [Source: docs/prd.md#FR20] - Functional Requirement FR20: Step Consolidation
- [Source: docs/epics.md#Story-6.2] - Story 6.2 Acceptance Criteria and Technical Notes

## Dev Agent Record

### Context Reference

### Agent Model Used

Composer (Cursor AI)

### Debug Log References

- Intelligent step consolidation already fully implemented
- Similarity detection verified
- AI description merging verified

### Completion Notes List

✅ **Implementation Complete:**

1. **Similarity Detection**: 
   - `StepConsolidator` class detects similar steps
   - `_are_steps_similar()` method calculates similarity
   - Screenshot comparison using image hash
   - Description similarity using text comparison
   - Window title comparison

2. **Consolidation Suggestions**: 
   - `suggest_consolidations()` method generates suggestions
   - Similarity scores calculated
   - Consolidation candidates identified

3. **Step Merging**: 
   - `_merge_steps()` method merges similar steps
   - Combines step metadata
   - Updates step numbers
   - Preserves essential information

4. **AI Description Merging**: 
   - `_merge_descriptions_with_ai()` method uses OpenAI API
   - Merges descriptions intelligently
   - Preserves key information
   - Generates concise merged description

5. **Documentation Update**: 
   - Consolidated steps update session
   - Preview refreshed
   - Step integrity maintained

### File List

**Verified Files (All Already Implemented):**
- `src/ai/step_consolidator.py` - StepConsolidator class ✅
- Similarity detection ✅
- Step merging ✅
- AI description merging ✅
