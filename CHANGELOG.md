# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-11

### Added

#### Core Features
- Headless TN5250 terminal emulation via tmux
- SSL/TLS connection support for secure IBM i communications
- Multi-LPAR support with environment-specific configurations
- Password security using Robot Framework Secret type
- Automated screenshot capture in text and PNG formats
- Verbose logging mode for debugging test development

#### Test Automation
- Robot Framework test suite with comprehensive IBM i coverage
- Common test library for shared functionality across LPARs
- LPAR-specific test override capability
- Tag-based test filtering (smoke, system, network, database, application)
- Sequential test execution with shared session
- Automatic cleanup and logout via bash trap

#### Test Suites
- Login test suite with authentication verification
- Logout test suite with graceful session termination
- System configuration tests (OS/400 licensing, QSECURITY)
- Network configuration and connectivity tests
- Journal entry verification tests
- Database object and integrity tests (QIWS library)
- Application installation verification tests

#### TN5250Library Keywords
- `Start TN5250 Session` - Initialize headless TN5250 connection
- `Stop TN5250 Session` - Terminate tmux session
- `Send Text` - Type text into terminal (supports Secret type)
- `Send Special Key` - Send function keys, Enter, Tab, etc.
- `Screen Should Contain` - Wait for text with configurable timeout
- `Capture Screen` - Save screen as text and/or PNG image
- `Set Verbose` - Enable/disable console logging

#### Infrastructure
- Docker multi-stage build with tn5250 v0.18 compilation
- VS Code DevContainer configuration
- Dynamic host configuration via hosts.conf
- LPAR-specific environment file management
- Automated host setup script with validation
- Git configuration for DevContainers

#### Documentation
- Comprehensive README with architecture diagram
- Test suite structure documentation
- Password security implementation guide
- DevContainer setup instructions
- Architecture documentation (ARCHITECTURE.md)
- Contributing guidelines (CONTRIBUTING.md)
- Generated library documentation (HTML)
- Generated test documentation (HTML)

#### Scripts
- `run_suites.sh` - Sequential test suite runner with LPAR support
- `setup-hosts.sh` - Dynamic /etc/hosts configuration
- Environment variable management per LPAR

### Security
- Password protection via Robot Framework Secret type
- Automatic keyword removal from HTML logs (--removekeywords)
- Environment file gitignore to prevent credential exposure
- DevContainer customer config exclusion from version control
- Input validation in host setup script
- SSL/TLS support for encrypted connections

### Dependencies
- Python 3.12
- Robot Framework 7.4
- robotframework-datadriver 1.11.2
- tn5250 v0.18 (compiled from source with SSL)
- tmux (terminal multiplexer)
- ImageMagick (optional, for PNG screenshots)

### Configuration
- Environment-based configuration per LPAR
- Template files for DevContainer and environment setup
- Configurable character maps (default: 285)
- Configurable SSL/TLS connections
- Optional device name specification
- LPAR-specific results organization

### Repository Structure
```
tn5250-rt/
├── .devcontainer/      # VS Code DevContainer config
├── .envs/              # LPAR-specific environment files
├── .github/            # GitHub workflows and instructions
├── docs/               # Documentation files
├── libraries/          # Robot Framework libraries
├── resources/          # Shared Robot Framework resources
├── results/            # Test results per LPAR
├── tests/              # Test suites (common + LPAR-specific)
├── Dockerfile          # Multi-stage build
├── pyproject.toml      # Python project configuration
├── requirements.txt    # Python dependencies
├── run_suites.sh       # Test suite runner
└── variables.py        # Robot Framework variable file
```

### Technical Decisions
- Headless execution via tmux for CI/CD compatibility
- Session reuse across tests for performance
- Standard 80x24 terminal dimensions
- Sequential (not parallel) test execution to share session
- LPAR-based test organization with common fallback
- Screenshot cleanup (delete .txt, keep .png)
- Exit on first failure with guaranteed cleanup
- Google-style docstrings for Python code
- Gherkin-style test organization

## [Unreleased]

### Planned Features
- Parallel test execution across multiple LPARs
- Enhanced error recovery with retry logic
- Test data management from external files
- Performance metrics collection
- CI/CD pipeline integration (GitHub Actions, Jenkins)
- Additional test coverage for specific IBM i modules
- API for programmatic test execution

---

## Version History

- **0.1.0** (2026-01-11) - Initial release

## Links

- [Repository](https://github.com/robinsg/tn5250-rt)
- [Issues](https://github.com/robinsg/tn5250-rt/issues)
- [Documentation](./docs/)
