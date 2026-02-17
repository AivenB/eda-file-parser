"""EDA File Parser - Timing Report Analysis Tool."""

from eda_file_parser.parser import (
    TimingPath,
    TimingReport,
    SummaryStats,
    AnalysisConfig,
    parse_report,
)

__version__ = "0.1.0"

__all__ = [
    "TimingPath",
    "TimingReport",
    "SummaryStats",
    "AnalysisConfig",
    "parse_report",
]
