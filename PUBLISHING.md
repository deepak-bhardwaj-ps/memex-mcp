# Publishing Memex MCP to PyPI

This guide walks through publishing memex-mcp to PyPI for public installation.

## Prerequisites

1. **PyPI Account**: Create one at https://pypi.org/account/register/
2. **TestPyPI Account** (optional but recommended): https://test.pypi.org/account/register/
3. **Build tools**:
   ```bash
   pip install build twine
   ```

## Step 1: Prepare for Release

### Update version in `pyproject.toml`

```toml
[project]
version = "0.1.0"  # Update this version
```

### Update `CHANGELOG.md`

Move changes from `[Unreleased]` to the new version section:

```markdown
## [0.1.0] - 2026-06-05
### Added
- Initial release features...
```

### Commit and tag

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: prepare v0.1.0 release"
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin main
git push origin v0.1.0
```

## Step 2: Build Distribution

```bash
python -m build
```

This creates:
- `dist/memex-mcp-0.1.0.tar.gz` (source distribution)
- `dist/memex_mcp-0.1.0-py3-none-any.whl` (wheel)

## Step 3: Test on TestPyPI (Recommended)

```bash
python -m twine upload --repository testpypi dist/*
```

When prompted, use your TestPyPI credentials.

Test installation:
```bash
pip install --index-url https://test.pypi.org/simple/ memex-mcp
```

## Step 4: Publish to PyPI

```bash
python -m twine upload dist/*
```

When prompted, use your PyPI credentials.

## Step 5: Verify

Check that your package is available:
- https://pypi.org/project/memex-mcp/
- Test installation: `pip install memex-mcp`
- Verify entry point: `memex-mcp --help`

## Continuous Publishing with GitHub Actions

To automate releases, create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: |
          python -m pip install --upgrade pip
          pip install build twine
      - run: python -m build
      - run: python -m twine upload dist/*
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
```

Then configure the secret in GitHub repository settings.

## Troubleshooting

### `twine upload` errors

- **Invalid credentials**: Double-check PyPI username/password
- **Version already exists**: Increment version in `pyproject.toml`
- **Missing files**: Ensure `CHANGELOG.md`, `README.md`, `LICENSE` exist

### Distribution issues

- **Build fails**: Run `python -m build --verbose` for more info
- **Wheel creation fails**: Ensure `setuptools>=69` and `wheel` are installed

## Subsequent Releases

For each new release:

1. Update version in `pyproject.toml`
2. Add changes to `CHANGELOG.md`
3. Commit and tag: `git tag -a vX.Y.Z && git push origin vX.Y.Z`
4. Build and upload: `python -m build && twine upload dist/*`

## References

- [PyPI Help](https://pypi.org/help/)
- [Python Packaging Guide](https://packaging.python.org/)
- [twine Documentation](https://twine.readthedocs.io/)
