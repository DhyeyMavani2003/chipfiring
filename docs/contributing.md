# Contributing

Thank you for your interest in contributing to the `chipfiring` package! We welcome contributions of all kinds from bug reports and feature requests to code contributions and documentation improvements.

## Development Setup

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/DhyeyMavani2003/chipfiring.git
cd chipfiring

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements.docs.txt
pip install -e .  # Install in development mode
```

## Running Tests

We use pytest for testing. To run the test suite:

```bash
# Run all tests in the tests directory with verbose info locally
pytest tests/ --verbose

# Run specific tests
pytest tests/test_graph.py

# Run tests across all the supported Python versions
make test
```

## Building Documentation

The documentation is built using Sphinx:

```bash
# Build documentation workflow
make docs

# View the documentation
open _build/html/index.html  # On macOS
# or
xdg-open _build/html/index.html  # On Linux
# or
start _build/html/index.html  # On Windows
```

## Code Style

We follow PEP 8 guidelines for Python code. We use the following tools for code quality:

- black: For code formatting
- ruff: For linting
- mypy: For static type checking

You can run these tools with:

```bash
# Format code
black chipfiring/ tests/

# Lint code
ruff check chipfiring/ tests/

# Type check
mypy --check-untyped-defs chipfiring/
```

## Pull Requests

When submitting a pull request:

1. Fork the repository and create a new branch from `main`
2. Add tests for any new functionality
3. Update documentation as necessary
4. Ensure all tests pass and code quality checks succeed
5. Submit a pull request with a clear description of your changes

## Issues and Feature Requests

If you find a bug or would like to request a feature, please open an issue on the [GitHub repository](https://github.com/DhyeyMavani2003/chipfiring/issues). When reporting a bug, please include:

- A clear description of the issue
- Steps to reproduce the problem
- Expected behavior
- Actual behavior
- Any error messages or stack traces

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.
