# Contributing to TN5250-RT

Thank you for your interest in contributing to TN5250-RT! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Submitting Changes](#submitting-changes)
- [Documentation](#documentation)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- Be respectful and considerate in all interactions
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Assume good intentions

## Getting Started

### Prerequisites

- Docker or Podman
- VS Code with DevContainers extension (recommended)
- Git
- Access to an IBM i system for testing (optional but recommended)

### First Time Setup

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/tn5250-rt.git
   cd tn5250-rt
   ```

3. Set up the development environment:
   ```bash
   cp .devcontainer/devcontainer.template.json .devcontainer/devcontainer.json
   # Edit devcontainer.json with your git user name and email
   ```

4. Open in VS Code and rebuild the DevContainer

## Development Setup

### DevContainer (Recommended)

The project includes a complete DevContainer configuration:

1. Configure hosts (optional):
   ```bash
   # Edit .devcontainer/hosts.conf
   dev400 192.168.1.100
   ```

2. Configure LPAR environment:
   ```bash
   cp .envs/.env.sh.template .envs/.env.sh.dev400
   # Edit with your credentials
   ```

3. Rebuild container in VS Code (F1 → "Dev Containers: Rebuild Container")

### Manual Setup

If not using DevContainers:

1. Build the Docker image:
   ```bash
   docker build -t tn5250-rt .
   ```

2. Run the container:
   ```bash
   docker run -it --rm -v $(pwd):/app tn5250-rt bash
   ```

## Coding Standards

### Python Code

All Python code must follow these standards:

**Style**:
- Use `snake_case` for function and method names
- Use Google-style docstrings for all public methods
- Maximum line length: 100 characters
- Use type hints where appropriate

**Example**:
```python
def send_text(self, text):
    """Types text into the terminal.

    Sends the specified text to the active TN5250 session as keyboard input.
    Supports Robot Framework Secret type for passwords.

    Args:
        text (str or Secret): The text to type into the terminal.

    Returns:
        None

    Raises:
        subprocess.CalledProcessError: If sending keys to tmux fails.
    """
    # Implementation
```

**Logging**:
- Use `robot.api.logger` for all output
- Log at appropriate levels (DEBUG, INFO, WARN, ERROR)
- Never log sensitive information (passwords, etc.)

**Error Handling**:
- Use `subprocess.run()` with `check=True` for external commands
- Let exceptions propagate to Robot Framework
- Provide clear error messages

See `.github/instructions/python.instructions.md` for complete guidelines.

### Robot Framework Tests

**Style**:
- Use Title Case for keyword calls
- Prefer Gherkin style (Given/When/Then) for high-level tests
- Use descriptive test case names
- Include documentation for all test cases and keywords

**Example**:
```robot
*** Test Cases ***
Login To IBM i
    [Documentation]    Validates complete login flow from sign-on screen to authenticated session.
    [Tags]    login    smoke
    
    Verify Sign On Screen
    Login With Credentials
    Verify Login Success
```

**Tags**:
- Use meaningful tags: `smoke`, `login`, `system`, `network`, `database`, `application`
- Use `wip` for work-in-progress tests
- Keep tags lowercase

See `.github/instructions/robot.instructions.md` for complete guidelines.

### Bash Scripts

**Style**:
- Use descriptive comments at the top of each script
- Validate all inputs
- Use meaningful variable names (UPPERCASE for environment/global)
- Include error handling with `set -e`
- Comment complex logic

**Example**:
```bash
#!/usr/bin/env bash
# Description of what this script does
# Usage: ./script.sh <arg1> [arg2]

set -e

# Validate inputs
if [ -z "$1" ]; then
    echo "Error: Missing required argument"
    exit 1
fi
```

## Testing Guidelines

### Running Tests

Test your changes thoroughly before submitting:

```bash
# Run all tests for an LPAR
./run_suites.sh DEV400

# Run specific tests
./run_suites.sh DEV400 --include smoke

# Run without WIP tests
./run_suites.sh DEV400 --exclude wip
```

### Writing Tests

When adding new test cases:

1. **Create test in appropriate location**:
   - Common functionality → `tests/common/`
   - LPAR-specific → `tests/LPAR_NAME/`

2. **Follow existing patterns**:
   ```robot
   *** Settings ***
   Documentation    What this test suite validates
   Resource    ../../resources/common.robot

   *** Test Cases ***
   Test Name
       [Documentation]    What this specific test validates
       [Tags]    category    subcategory
       
       Execute Command And Verify    COMMAND
       Send Special Key    F3
   ```

3. **Use appropriate tags**:
   - Functional area: `system`, `network`, `database`, `application`
   - Importance: `smoke`, `critical`
   - Status: `wip` (work in progress)

4. **Add documentation**:
   - Suite-level documentation (what the suite tests)
   - Test case documentation (what this specific test validates)
   - Keyword documentation (for custom keywords)

### Testing Changes to TN5250Library

When modifying `libraries/TN5250Library.py`:

1. Update or add docstrings following Google style
2. Test manually in a Robot test first
3. Verify verbose mode output
4. Test error conditions
5. Regenerate documentation:
   ```bash
   python -m robot.libdoc libraries/TN5250Library.py docs/TN5250Library.html
   ```

## Submitting Changes

### Workflow

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the coding standards

3. Test your changes thoroughly

4. Commit with clear, descriptive messages:
   ```bash
   git commit -m "Add feature: description of what changed"
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a Pull Request on GitHub

### Pull Request Guidelines

**Title**: Clear and descriptive summary of changes

**Description**: Include:
- What changed and why
- Related issue numbers (if applicable)
- Testing performed
- Screenshots (if UI/visual changes)
- Any breaking changes

**Example**:
```markdown
## Summary
Add support for custom character maps in TN5250 connections

## Changes
- Add `map` parameter to `Start TN5250 Session` keyword
- Update documentation for character map configuration
- Add test case for non-default map

## Testing
- Tested with maps 285, 37, and 273
- All existing tests pass
- Added new test case in tests/common/login.robot

## Breaking Changes
None - `map` parameter has default value of 285
```

### Review Process

1. Automated checks must pass (if configured)
2. Code review by maintainer(s)
3. Address any feedback
4. Approval and merge

## Documentation

### When to Update Documentation

Update documentation when you:
- Add new keywords or features
- Change existing behavior
- Add configuration options
- Modify architecture

### Documentation Types

1. **Code Documentation**:
   - Python docstrings (Google style)
   - Robot Framework documentation
   - Bash script comments

2. **README Files**:
   - Main `README.md` - Project overview
   - `tests/README.md` - Test structure
   - `.devcontainer/README.md` - DevContainer setup

3. **Technical Documentation**:
   - `docs/ARCHITECTURE.md` - System design
   - `docs/PASSWORD_SECURITY.md` - Security implementation
   - Generated docs (`TN5250Library.html`, `tests_overview.html`)

### Generating Documentation

Library documentation:
```bash
python -m robot.libdoc libraries/TN5250Library.py docs/TN5250Library.html
```

Test documentation:
```bash
python -m robot.testdoc tests/ docs/tests_overview.html
```

## Common Contributions

### Adding a New Keyword

1. Add method to `libraries/TN5250Library.py`:
   ```python
   def new_keyword(self, arg1, arg2="default"):
       """Brief description.
       
       Detailed description.
       
       Args:
           arg1 (type): Description
           arg2 (type, optional): Description. Defaults to "default".
       
       Returns:
           type: Description
       
       Raises:
           ExceptionType: When this happens
       """
       # Implementation
   ```

2. Add test case using the new keyword

3. Update documentation:
   ```bash
   python -m robot.libdoc libraries/TN5250Library.py docs/TN5250Library.html
   ```

### Adding a New Test Suite

1. Create `tests/common/new_suite.robot`:
   ```robot
   *** Settings ***
   Documentation    What this suite validates
   Resource    ../../resources/common.robot

   *** Test Cases ***
   Test Case Name
       [Documentation]    What this test validates
       [Tags]    category
       
       # Test steps
   ```

2. Add to `run_suites.sh` in `SUITE_NAMES` array

3. Test execution:
   ```bash
   ./run_suites.sh DEV400
   ```

### Supporting a New LPAR

1. Create directories:
   ```bash
   mkdir tests/NEW_LPAR
   mkdir -p results/NEW_LPAR/{suites,screenshots}
   ```

2. Create environment file:
   ```bash
   cp .envs/.env.sh.template .envs/.env.sh.NEW_LPAR
   # Edit with LPAR credentials
   ```

3. Run tests:
   ```bash
   ./run_suites.sh NEW_LPAR
   ```

## Questions or Issues?

- Check existing [documentation](./docs/)
- Review [open issues](../../issues)
- Ask questions in [discussions](../../discussions) (if available)
- Create a new issue with the `question` label

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see [LICENSE](./LICENSE) file).

---

Thank you for contributing to TN5250-RT!
