# Contributing

## Development Setup

1. Use Python 3.9 or newer.
2. Clone the repository.
3. Run tests:

```bash
python -m unittest discover -s tests -v
```

## Pull Request Checklist

1. Keep behavior changes scoped and documented in the PR description.
2. Add or update tests for behavior changes.
3. Ensure all tests pass locally.
4. Avoid committing generated files (`__pycache__`, `build`, `*.egg-info`).

## Commit Message Style

- Keep commits focused and atomic.
- Use short imperative subject lines, for example:
  - `add startup script CI test`
  - `fix base-path discovery fallback`
