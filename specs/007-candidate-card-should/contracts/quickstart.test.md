# Quickstart Test: Candidate Card UI

## Scenario: Minimal details visible by default
- Render candidate list
- Assert only name, skills, experience are visible

## Scenario: Show all details
- Click "Show all details" button
- Assert all candidate fields are visible

## Scenario: Missing data
- Render card with missing skills/experience
- Assert placeholders or hidden fields

## Scenario: Long lists
- Render card with long skills/experience
- Assert truncation/ellipsis

## Scenario: No candidates
- Render empty list
- Assert appropriate message

## Scenario: Accessibility
- Tab to "Show all details" button
- Assert it is focusable and has accessible name
