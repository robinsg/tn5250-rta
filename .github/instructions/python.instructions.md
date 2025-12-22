---
name: Python Library Standards
applyTo: "libraries/**/*.py"
---
Python Keywords
Use snake_case for method names.
Always include Google-style docstrings.
Use robot.api.logger for all output.
Every method must handle tmux errors using subprocess.run return codes.
