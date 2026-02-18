# EDA File Parser

A Python-based tool for parsing and analyzing static timing analysis (STA) reports used in Electronic Design Automation (EDA) workflows. The project converts timing report output into structured data models that enable filtering, summarization, and programmatic analysis.

## Features

- **Parse Timing Reports**: Extract timing paths, clock group, timing type, slack values, and path status
- **Statistical Analysis**: Generate summary statistics including worst paths, path status, and slack distribution
- **Flexible Filtering**: Filter paths by status (MET/VIOLATED), type (min/max), or clock group
- **CLI Interface**: Command-line tool with multiple analysis options
- **Test Suite**: Comprehensive test suite using pytest
- **Type-Safe**: Fully typed with Python type hints and dataclasses

## Prerequisites/Requirements
Before dowloading repo, ensure the following is met:

- **Python 3.14+** was used and (recommonded)
- Install **uv** - Fast Python package installer and resolver ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))

## Dependencies

### Runtime Dependencies
- None (pure Python, standard library only)

### Development Dependencies
- `pytest >= 9.0.2` - Testing framework
- `pytest-cov>=7.0.0` - Testing code coverage

All dependencies are managed in `pyproject.toml` and automatically installed with uv.

## Usage

### Command-Line Interface

After downloading repo, the following shows usage ways:
```bash
# using uv
uv run path/to/parser.py reports/<file_name>.rpt
```

OR

```bash
# using standard python
python path/to/parser.py reports/<file_name>.rpt
```

```bash
# Basic parsing with summary
python src/eda_file_parser/parser.py reports/timing_full.rpt --summary

# Show worst timing paths
python src/eda_file_parser/parser.py reports/timing_full.rpt --worst

# Filter violated paths
python src/eda_file_parser/parser.py reports/timing_full.rpt --status VIOLATED

# Filter by path type (min or max)
python src/eda_file_parser/parser.py reports/timing_full.rpt --type max

# Filter by path group
python src/eda_file_parser/parser.py reports/timing_full.rpt --group clk_group

# Combine multiple options
python src/eda_file_parser/parser.py reports/timing_full.rpt --summary --worst --type max

# Enable debug logging
python src/eda_file_parser/parser.py reports/timing_full.rpt --debug
```

- NOTE: A bash script `test_cli.sh` is included to show usage.

### Python API

The definitions in `__init__.py` allows the parser
to be used programmatically:

```python
from eda_file_parser import parse_report, SummaryStats

# Parse a timing report
report = parse_report("reports/timing_full.rpt")

# Access parsed data
print(f"Total paths: {len(report.paths)}")
print(f"Worst min slack: {report.worst_min_path.slack}")

# Generate statistics
stats = SummaryStats.from_report(report)
print(stats)

# Filter paths
violated_paths = [p for p in report.paths if p.status == "VIOLATED"]
```

### Available Command line Options

| Option | Description |
|--------|-------------|
| `--summary` | Display summary statistics (total paths, violations, slack analysis) |
| `--worst` | Show worst min and max timing paths |
| `--status MET\|VIOLATED` | Filter paths by timing status |
| `--type min\|max` | Filter paths by analysis type |
| `--group CLOCK_NAME` | Filter paths by path group name |
| `--debug` | Enable debug-level logging |

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_parser.py

# Run with coverage
uv run pytest --cov=src

# Run with coverage and show lines missing
uv run pytest --cov=src --cov-report=term-missing
```

### Test Structure

Tests are located in the `tests/` directory and use pytest fixtures for setup:

```
tests/
├── __init__.py
└── test_parser.py    # Main test suite
```

Test and sample reports are stored in `reports/` directory:
- `timing_full.rpt` - Comprehensive sample timing report 
- `simple_met.rpt` - Modified report with met timing constraints
- `simple_violated.rpt` - Modified report with violated constraints
- `mixed_paths.rpt` - Modified report with mix of min/max paths
- `empty.rpt` - Empty edge case report

## Project Structure

```
eda-file-parser/
├── src/
│   └── eda_file_parser/
│       ├── __init__.py       # Package exports and version
│       └── parser.py         # Core parsing logic and CLI
├── tests/
│   ├── __init__.py
│   └── test_parser.py        # Test suite with fixtures
├── reports/                  # Sample timing reports
│   ├── simple_met.rpt
│   ├── simple_violated.rpt
│   ├── timing_full.rpt
│   └── ...
├── pyproject.toml           # Project metadata and dependencies
├── uv.lock                  # Locked dependencies
├── README.md
└── .python-version          # Python version specification
```

## Roadmap

### Planned Improvements
- Add containerized test environments (Docker / Podman)
- Expand test coverage for edge cases
- Improve parser validation for malformed or unexpected formats
- Improve structured error handling and reporting
- Add data visualizations for analysis results (e.g., slack distribution histograms, worst-path summaries, and group-level metrics)

### Developer Notes
- AI-assisted tools were used to help generate and refine portions of the unit test suite.

## Sample Output
```bash
$ uv run src/eda_file_parser/parser.py reports/timing_full.rpt --summary

Parsed 102 timing paths
==================================================
TIMING REPORT SUMMARY
==================================================
Total Paths:          102
  Min Type Paths:     51
  Max Type Paths:     51

Timing Status:
  Met Paths:          64
  Violated Paths:     38

Slack Analysis:
  Worst Overall:      -0.5674
  Worst Min:          0.4880
  Worst Max:          -0.5674
  Best Slack:         2.1268
==================================================
```

```bash
$ uv run src/eda_file_parser/parser.py reports/timing_full.rpt --help

usage: parser.py [-h] [--debug] [--summary] [--worst] [--status {MET,VIOLATED}] [--type {min,max}] [--group GROUP] report

EDA Timing Report Parser

positional arguments:
  report                Path to timing report file

options:
  -h, --help            show this help message and exit
  --debug               Enable debug output
  --summary             Show summary statistics
  --worst               Show worst paths
  --status {MET,VIOLATED}
                        Filter paths by status (MET or VIOLATED)
  --type {min,max}      Filter paths by type (min or max)
  --group GROUP         Filter paths by path group name
```

## How to Build
Assuming prequisites are met:

1. Clone GitHub repository
```bash
git clone git@github.com:AivenB/eda-file-parser.git
```

2. Setup Virtual Environment
- Run `uv sync` to setup virtual environment with correct
dependencies seen in `pyproject.toml` and `uv.lock`
```bash
uv sync
```

3. Run test to verify setup
```bash
uv run pytest
```

## Quick Start Build

```bash
git clone https://github.com/AivenB/eda-file-parser.git
cd eda-file-parser
uv sync
uv run pytest
```

## Additional Resources

- [uv Documentation](https://docs.astral.sh/uv/)
- [uv GitHub Repository](https://github.com/astral-sh/uv)
- [pytest Documentation](https://docs.pytest.org/)
- [pytest Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
- [uv and pytest setup](https://pydevtools.com/handbook/tutorial/setting-up-testing-with-pytest-and-uv/)
- [Python Docstring Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Python Dataclasses Documentation](https://docs.python.org/3/library/dataclasses.html)
- [OpenROAD GitHub Repository](https://github.com/The-OpenROAD-Project/OpenROAD)

