# Design Document: Character Edit Error Handling

## Overview

This design addresses a critical bug in the Telegram bot's character editing functionality where ValueError exceptions incorrectly reset the FSM state, breaking the user input flow. The solution involves removing the inappropriate state reset from the ValueError handler while preserving proper error handling for other exception types.

## Architecture

The character editing system uses aiogram's FSM (Finite State Machine) with two main state groups:

- **CharacterCreation.editing_sheet**: The main editing menu state where users select which field to edit
- **CharacterEdit.waiting_for_value**: The input waiting state where users provide new values for selected fields

The current bug occurs in the transition handling between these states when input validation fails.

### Current Flow (Buggy)
```
CharacterCreation.editing_sheet 
    → User selects field to edit
    → CharacterEdit.waiting_for_value
    → User enters invalid input (ValueError)
    → BUG: State reset to CharacterCreation.editing_sheet
    → User input no longer processed
```

### Fixed Flow
```
CharacterCreation.editing_sheet 
    → User selects field to edit
    → CharacterEdit.waiting_for_value
    → User enters invalid input (ValueError)
    → Error message shown, state remains CharacterEdit.waiting_for_value
    → User can retry with correct input
    → Success: State returns to CharacterCreation.editing_sheet
```

## Components and Interfaces

### Modified Components

**process_edit Function**
- **Location**: `handlers.py`
- **Current State**: Contains bug in ValueError exception handler
- **Modification**: Remove state reset from ValueError handler
- **Interface**: Handles `CharacterEdit.waiting_for_value` state messages

**Exception Handling Logic**
- **ValueError Handler**: Remove `await state.set_state(CharacterCreation.editing_sheet)` line
- **General Exception Handler**: Keep existing state reset behavior for non-ValueError exceptions
- **Success Handler**: Keep existing state transition to `CharacterCreation.editing_sheet`

### Unchanged Components

**State Definitions**
- `CharacterCreation.editing_sheet`: Remains unchanged
- `CharacterEdit.waiting_for_value`: Remains unchanged

**Input Validation**
- `NUMERIC_FIELDS` list: No changes required
- Integer conversion logic: No changes required
- Error message text: No changes required

**Database Operations**
- `db.update_character()`: No changes required
- Character field updates: No changes required

## Data Models

No data model changes are required. The existing character data structure and database schema remain unchanged:

```python
# Existing character fields (unchanged)
NUMERIC_FIELDS = [
    'level', 'strength', 'dexterity', 'constitution', 'intelligence',
    'wisdom', 'charisma', 'max_hp', 'current_hp', 'armor_class',
    'initiative_bonus', 'speed', 'passive_perception', 'proficiency_bonus'
]

# Existing field mapping (unchanged)
EDIT_FIELD_MAP = {
    "edit_name": ("name", "Введи новое имя:"),
    "edit_level": ("level", "Введи уровень:"),
    # ... other mappings remain the same
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*
