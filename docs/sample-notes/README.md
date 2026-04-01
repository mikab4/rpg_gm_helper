# Sample Notes

This directory holds sample campaign notes for:
- manual demos
- extraction development
- backend fixtures
- search validation

## Suggested Conventions

- One markdown file per session or source note
- Clear names such as `session-001.md`
- Include enough repeated references that extraction and search behavior can be verified

## Starter Fixture

Create early fixtures with:
- named characters
- named locations
- one organization or faction
- one explicit relationship
- one unresolved detail that should remain only as note text

## Example

Suggested first file:
- `session-001.md`

Suggested content shape:
- session date
- short summary
- bullet list of notable events
- mentions of recurring people and places

These notes should stay realistic enough to test extraction and review, but small enough that failures are easy to debug.
