#!/bin/bash
# Quick tests for CLI

python src/eda_file_parser/parser.py reports/timing_full.rpt --summary
python src/eda_file_parser/parser.py reports/timing_full.rpt --worst
python src/eda_file_parser/parser.py reports/timing_full.rpt --status VIOLATED
