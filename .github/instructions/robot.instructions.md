---
name: Robot Framework Standards
applyTo: "tests/**/*.robot"
---
# Robot Test Rules
- Use `Title Case` for Keyword calls.
- Prefer **Gherkin style** (Given/When/Then) for high-level tests.
- Reference the custom library using relative paths: `Library  ../libraries/TmuxTn5250Library.py`.
- Generate documentation to be used with python -m robot.testdoc.
