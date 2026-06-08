# Contributing to Memex MCP

Thank you for your interest in contributing to Memex MCP! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- `pip` and `git`

### Setting up your development environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/deepak-bhardwaj-ps/memex-mcp.git
   cd memex-mcp
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode with test dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Verify installation**
   ```bash
   pytest tests/ -v
   ```

## Development Workflow

### Making Changes

1. Create a feature branch from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes, keeping commits atomic and well-described

3. Add or update tests for new functionality

4. Run tests to ensure nothing is broken
   ```bash
   pytest tests/ -v
   ```

### Code Style

- Follow PEP 8 conventions
- Use type hints in function signatures
- Keep docstrings clear and concise
- Use descriptive variable names

### Testing

- Write tests for all new features
- Maintain or improve test coverage
- Include both unit tests and integration tests where appropriate
- All tests must pass before submitting a PR

**Running tests:**
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_memex_store.py -v

# With coverage
pytest tests/ --cov=src/memex_mcp --cov-report=html
```

## Submitting Changes

### Pull Request Process

1. **Update documentation** - If your changes affect user-facing features, update the README
2. **Update CHANGELOG** - Add an entry to `CHANGELOG.md` under an `[Unreleased]` section
3. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
4. **Create a Pull Request** with:
   - Clear description of what changed and why
   - Reference to any related issues
   - Confirmation that tests pass
5. **Respond to review feedback** promptly

### Commit Messages

Use clear, descriptive commit messages:

- ✅ Good: `feat: add wikilink parsing for memory relationships`
- ✅ Good: `fix: prevent path traversal in memory IDs`
- ✅ Good: `docs: clarify memory metadata format in README`
- ❌ Bad: `fix stuff`
- ❌ Bad: `update`

## Reporting Issues

### Bug Reports

Include:
- Python version and OS
- Steps to reproduce
- Expected vs. actual behavior
- Relevant code snippets or error messages

### Feature Requests

Include:
- Use case and motivation
- Proposed solution (if any)
- Alternatives you've considered

## Areas for Contribution

- **Documentation** - Improve READMEs, examples, or docstrings
- **Testing** - Expand test coverage or add edge case tests
- **Performance** - Optimize search, indexing, or file I/O
- **Features** - New memory operations, search capabilities, or export formats
- **Integration** - Examples for popular agents (Claude, OpenAI, etc.)

## Licensing

By contributing, you agree that your contributions will be licensed under the MIT License (see [LICENSE](LICENSE) file).

## Questions?

Feel free to open an issue to ask questions about contributing or participating in this project.

Thank you for making Memex MCP better! 🚀
