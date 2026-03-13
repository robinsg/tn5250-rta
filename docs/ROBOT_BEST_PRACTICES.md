# Robot Framework Best Practices for TN5250-RT

This document outlines the best practices and coding standards for the Robot Framework automation suite in the TN5250-RT project.

## 1. Project Structure

*   **`tests/`**: Contains all test suites.
    *   **`tests/common/`**: Reusable test suites that apply across multiple environments (LPARs).
    *   **`tests/<LPAR_NAME>/`**: Environment-specific test suites or overrides.
*   **`resources/`**: Contains `.robot` resource files providing high-level keywords.
*   **`libraries/`**: Contains custom Python libraries (`.py`).
*   **`results/`**: Output directory for Robot Framework reports, logs, and screenshots.
*   **`variables.py`**: Centralized variable management, handling environment variables and secrets.

## 2. Coding Standards (Robot Framework)

### 2.1. Keyword Naming
*   Use **Title Case** for keyword names (e.g., `Login With Credentials`).
*   Names should be descriptive and action-oriented.

### 2.2. Documentation
*   Every suite should have a `Documentation` setting.
*   Every keyword should have a `[Documentation]` tag explaining its purpose, arguments, and return values.

### 2.3. Avoid Static Sleeps
*   **Bad Practice**: `Sleep    2s`
*   **Best Practice**: Use dynamic waits like `Wait Until Keyword Succeeds` or library-provided polling (e.g., `Verify Sign On Screen`).
*   Static sleeps make tests brittle and unnecessarily slow.

### 2.4. Resource and Library Imports
*   Use relative paths for resources within the `tests/` directory.
*   Centralize common imports in `resources/common.resource`.

## 3. Python Library Development

### 3.1. Type Hinting
*   All methods in custom libraries should use Python type hints for better maintainability and IDE support.

### 3.2. Docstrings
*   Use Google-style or Sphinx-style docstrings for all classes and methods. These are parsed by Robot Framework's `Libdoc` tool to generate documentation.

### 3.3. Logging
*   Use `robot.api.logger` for logging.
*   Provide useful debug information that appears in the Robot Framework logs when tests fail.

### 3.4. Error Handling
*   Raise meaningful exceptions (e.g., `AssertionError` for test failures, `RuntimeError` for system issues).
*   Provide clear error messages that help diagnose why a test failed.

## 4. Variable Management

*   **Secrets**: Always use the `Secret` type for sensitive data (passwords, tokens) to ensure they are obfuscated in logs.
*   **Environment Variables**: Prefix environment variables with `TN5250_` to avoid collisions.
*   **Defaults**: Provide sensible defaults in `variables.py` where appropriate.

## 5. Session Management

*   Use `Suite Setup` and `Suite Teardown` for session lifecycle management.
*   Ensure sessions are closed even if tests fail (Robot Framework handles this automatically in teardowns).

## 6. Maintenance and Tooling

*   **Linting**: Use `robocop` to enforce these standards.
*   **Formatting**: Use `robotframework-tidy` (RoboTidy) to maintain consistent formatting.
*   **Dry Runs**: Regularly run `robot --dryrun tests/` to catch syntax errors without executing tests.
