# ChronoEcho

ChronoEcho is a small Python CLI toolset for searching "same day in past years" note records and optionally wiring that lookup into Windows Startup.

## What It Does

- Search note records by date across year folders.
- Support both `YYYY-MM-DD` and `MM-DD` query formats.
- Resolve a note base path from:
  - `--base-path` argument
  - `CHRONOECHO_BASE_PATH` environment variable
  - auto-discovery from script directory
- Generate a `.bat` startup launcher for Windows login startup.

## Project Layout

```text
chronoecho_history.py      # main date lookup CLI
setup_startup.py           # Windows startup .bat generator
tests/
  test_chronoecho_history.py # tests for history lookup logic
  test_setup_startup.py      # tests for startup setup logic
```

## Requirements

- Python 3.10+

No third-party runtime dependency is required.

## Quick Start

Run directly:

```bash
python chronoecho_history.py
python chronoecho_history.py 2026-02-24
python chronoecho_history.py 02-24
python chronoecho_history.py --base-path "/path/to/life-notes"
```

Set environment variable once:

```bash
export CHRONOECHO_BASE_PATH="/path/to/life-notes"
python chronoecho_history.py 02-24
```

Windows PowerShell:

```powershell
$env:CHRONOECHO_BASE_PATH = "D:\notes\life"
python .\chronoecho_history.py 02-24
```

## Install as CLI Commands

Editable install:

```bash
pip install -e .
```

Then you can run:

```bash
chronoecho-history 02-24
chronoecho-startup --help
```

## Windows Startup Script Generator

Generate startup bat file:

```bash
python setup_startup.py --help
python setup_startup.py --base-path "D:\notes\life" --overwrite
```

## Testing

Run all tests:

```bash
python -m unittest discover -s tests -v
```

## Recommended Repository Setup

After creating the GitHub repo:

1. Update URLs in `pyproject.toml` under `[project.urls]`.
2. Tag a first release after your initial commit, for example `v0.1.0`.
3. Enable GitHub Actions (CI workflow is included in this project).

## License

MIT. See [LICENSE](LICENSE).
