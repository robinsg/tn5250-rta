# TN5250-RT

Robot Framework Test Automation for TN5250 terminal emulation on IBM i systems. This project provides a headless test automation framework for validating IBM i (formerly iSeries/AS400) functionality through the TN5250 protocol.

## Overview

TN5250-RT is a Robot Framework-based test automation suite that enables headless testing of IBM i systems via TN5250 terminal emulation using tmux. It supports multiple LPARs (Logical Partitions) and provides comprehensive test coverage for system configuration, network settings, database operations, and application functionality.

### Key Features

- **Headless Testing**: Automated TN5250 terminal emulation via tmux
- **SSL Support**: Native SSL/TLS connection support for secure communications
- **Multi-LPAR Support**: Test multiple IBM i environments with LPAR-specific configurations
- **Password Security**: Built-in secret handling to prevent password exposure in logs
- **Screenshot Capture**: Automated screen capture for test verification and debugging
- **Modular Test Structure**: Shared common tests with LPAR-specific override capabilities
- **Comprehensive Coverage**: Tests for system config, networking, databases, journals, and applications

## Project Structure

This repository is organized into several key directories:

| Directory | Description |
|-----------|-------------|
| `libraries/` | Custom Robot Framework libraries for TN5250 interaction |
| `tests/` | Test suites organized by LPAR and functionality |
| `tests/common/` | Shared test cases used across all LPARs |
| `resources/` | Shared Robot Framework keywords and resources |
| `docs/` | Project documentation and guides |
| `results/` | Test execution results, organized by LPAR |
| `.devcontainer/` | VS Code DevContainer configuration |
| `.envs/` | Environment variable configurations per LPAR |

## Documentation

Comprehensive documentation is available in the following locations:

- **[Test Suite Structure](./tests/README.md)** - Multi-LPAR test organization and execution
- **[Password Security](./docs/PASSWORD_SECURITY.md)** - Secret handling and log security
- **[DevContainer Setup](./.devcontainer/README.md)** - Development environment configuration
- **[Library Documentation](./docs/TN5250Lirary.html)** - Generated API documentation for TN5250Library
- **[Test Overview](./docs/tests_overview.html)** - Generated Robot Framework test documentation

## Getting Started

### Prerequisites

- Docker or Podman (for containerized execution)
- VS Code with DevContainers extension (recommended for development)
- Access to an IBM i system with TN5250 connectivity
- Network connectivity to IBM i host(s)

### Installation

#### Using DevContainer (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/robinsg/tn5250-rt.git
   cd tn5250-rt
   ```

2. Configure your DevContainer:
   ```bash
   cp .devcontainer/devcontainer.template.json .devcontainer/devcontainer.json
   # Edit devcontainer.json to set your git user name and email
   ```

3. Configure your IBM i hosts:
   ```bash
   # Edit .devcontainer/hosts.conf with your IBM i systems
   # Format: hostname ip_address
   dev400 192.168.1.100
   ```

4. Open in VS Code and rebuild the container:
   - Press `F1` → "Dev Containers: Rebuild Container"

#### Using Docker

1. Build the container:
   ```bash
   docker build -t tn5250-rt .
   ```

2. Run tests:
   ```bash
   docker run --rm \
     -v $(pwd)/results:/app/results \
     -e TN5250_HOST=your_host \
     -e TN5250_USER=your_user \
     -e TN5250_PASS=your_password \
     -e TN5250_SSL=1 \
     tn5250-rt \
     ./run_suites.sh LPAR_NAME
   ```

### Configuration

#### Environment Variables

Create LPAR-specific environment files in `.envs/.env.sh.LPAR_NAME`:

```bash
export TN5250_HOST=your_host
export TN5250_USER=your_user
export TN5250_PASS=your_password  # Will be converted to Secret type
export TN5250_SSL=1               # 1 for SSL, 0 for non-SSL
export TN5250_DEVNAME=            # Optional device name
export TN5250_MAP=285             # Character map (default: 285)
```

#### LPAR Setup

1. Create LPAR directories:
   ```bash
   mkdir tests/YOUR_LPAR
   mkdir -p results/YOUR_LPAR/{suites,screenshots}
   ```

2. Create LPAR-specific environment file:
   ```bash
   cp .envs/.env.sh.template .envs/.env.sh.YOUR_LPAR
   # Edit with your LPAR credentials
   ```

## Usage

### Running Tests

Execute test suites for a specific LPAR:

```bash
# Run all tests for an LPAR
./run_suites.sh DEV400

# Run only smoke tests
./run_suites.sh DEV400 --include smoke

# Run all tests except work-in-progress
./run_suites.sh PROD500 --exclude wip

# Combine multiple tag filters
./run_suites.sh DEV400 --include smoke --exclude slow
```

### Test Execution Flow

1. **Login** - Establishes TN5250 session and authenticates
2. **Test Suites** - Runs sequentially, sharing the session:
   - System Configuration
   - Network Configuration
   - Journal Verification
   - Database Testing
   - Application Verification
3. **Logout** - Gracefully terminates the session (always runs)

### Viewing Results

Test results are organized by LPAR:

```
results/
├── DEV400/
│   ├── suites/         # XML, HTML logs and reports
│   └── screenshots/    # PNG screen captures
└── PROD500/
    ├── suites/
    └── screenshots/
```

Open `results/LPAR_NAME/suites/report.html` in a browser to view the test report.

## Development

### Project Dependencies

- **Python 3.12+** - Runtime environment
- **Robot Framework 7.4** - Test automation framework
- **TN5250 emulator** - Compiled from source (v0.18) with SSL support
- **tmux** - Terminal multiplexer for headless sessions
- **ImageMagick** - Optional, for PNG screenshot generation

### Development Workflow

1. Make changes to library code (`libraries/TN5250Library.py`)
2. Update test cases in `tests/common/` or LPAR-specific directories
3. Run tests to validate changes:
   ```bash
   ./run_suites.sh YOUR_LPAR
   ```

### Generating Documentation

Generate library documentation from Python docstrings:

```bash
python -m robot.libdoc libraries/TN5250Library.py docs/TN5250Library.html
```

Generate test documentation:

```bash
python -m robot.testdoc tests/ docs/tests_overview.html
```

### Code Standards

- **Python**: Follow Google-style docstrings, use `snake_case` for methods
- **Robot Framework**: Use Title Case for keywords, prefer Gherkin style (Given/When/Then)
- **Bash**: Include descriptive comments, validate inputs

See `.github/instructions/` for detailed coding standards.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│ Robot Framework Test Suite                              │
│ ├── Login Tests (establish session)                     │
│ ├── System/Network/Database/Application Tests           │
│ └── Logout Tests (cleanup)                              │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│ TN5250Library (Python)                                   │
│ ├── Session Management (start/stop)                     │
│ ├── Input Handling (text, special keys)                 │
│ ├── Screen Verification (text matching, timeout)        │
│ └── Screenshot Capture (text/image)                     │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│ tmux (Terminal Multiplexer)                             │
│ └── Headless session (80x24 screen)                     │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│ tn5250 Emulator (with SSL support)                      │
│ └── TN5250 protocol implementation                      │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
        ┌─────────────────┐
        │   IBM i System   │
        │   (AS/400)       │
        └─────────────────┘
```

### Key Design Decisions

- **Headless Operation**: Uses tmux for background terminal sessions enabling CI/CD integration
- **Session Persistence**: Login runs once, all tests share the session for efficiency
- **Secret Management**: Passwords handled as Robot Framework Secret type, never logged in clear text
- **Multi-LPAR Support**: LPAR-specific configs with common test fallback
- **Error Handling**: Tests fail fast on critical errors, logout always runs via cleanup trap

## Available Test Suites

### Common Tests (tests/common/)

- **login.robot** - TN5250 session establishment and authentication
- **logout.robot** - Graceful session termination
- **system_config.robot** - OS/400 licensing and security settings (QSECURITY)
- **network_config.robot** - Network interfaces, status, and connectivity
- **journal.robot** - Journal entries and audit trail verification
- **database.robot** - Database objects and integrity (QIWS library)
- **application.robot** - Application installation and functionality

### LPAR-Specific Tests

Create LPAR-specific test files in `tests/LPAR_NAME/` to override common tests or add custom tests for specific environments.

## Security Considerations

- **Password Protection**: All passwords are converted to `Secret` type and logged as `<secret>`
- **Keyword Removal**: Login keywords automatically removed from HTML reports via `--removekeywords`
- **Environment Files**: `.envs/.env.sh.*` files are gitignored to prevent credential exposure
- **DevContainer Config**: Customer-specific `devcontainer.json` and `hosts.conf` are gitignored

See [docs/PASSWORD_SECURITY.md](./docs/PASSWORD_SECURITY.md) for detailed security implementation.

## Version History

**v0.1.0** - Initial Release
- Headless TN5250 testing via tmux
- SSL/TLS connection support
- Multi-LPAR support with shared/specific tests
- Password security with Secret type
- Screenshot capture (text and PNG)
- Comprehensive test coverage (system, network, database, application)

## Contributing

Contributions are welcome! When contributing:

1. Follow the coding standards in `.github/instructions/`
2. Add tests for new functionality
3. Update documentation to reflect changes
4. Ensure all tests pass before submitting

## Support

For issues or questions:

1. Check existing [documentation](./docs/) and [test README](./tests/README.md)
2. Review [existing issues](../../issues)
3. Create a [new issue](../../issues/new) with:
   - Environment details (LPAR, OS version)
   - Steps to reproduce
   - Expected vs actual behavior
   - Relevant logs from `results/`

## License

This project is licensed under the terms specified in the [LICENSE](./LICENSE) file.

## Authors

- **Project Owner**: robinsg

## Acknowledgments

- [TN5250 project](https://github.com/tn5250/tn5250) - Open source TN5250 emulator
- [Robot Framework](https://robotframework.org/) - Test automation framework
- IBM i community

## Related Technologies

- [tn5250](https://github.com/tn5250/tn5250) - TN5250 terminal emulator
- [Robot Framework](https://robotframework.org/) - Generic test automation framework
- [tmux](https://github.com/tmux/tmux) - Terminal multiplexer

---

**Version**: 0.1.0  
**Last Updated**: 2026-01-11
