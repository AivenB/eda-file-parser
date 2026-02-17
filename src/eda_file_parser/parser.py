import sys
import argparse
import logging
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class TimingPath:
    """
    Represents a single timing path from an EDA timing report.
    
    Attributes:
        startpoint: The starting point of the timing path.
        endpoint: The ending point of the timing path.
        path_group: The group this path belongs to (e.g., clock domain).
        path_type: Type of timing analysis ("min" or "max").
        required_time: Required arrival time in nanoseconds.
        arrival_time: Actual data arrival time in nanoseconds.
        slack: Timing slack (positive = met, negative = violated).
    """
    startpoint:     str = ""
    endpoint:       str = ""
    path_group:     str = ""
    path_type:      str = ""
    required_time:  Optional[float] = None
    arrival_time:   Optional[float] = None
    slack:          Optional[float] = None

    @property
    def status(self) -> str:
        """Return timing status based on slack value.
        
        Returns:
            str: 'MET' if slack >= 0, 'VIOLATED' if slack < 0, 'UNKNOWN' if slack is None.
        """
        if self.slack is None:
            return "UNKNOWN"
        return "VIOLATED" if self.slack < 0.0 else "MET"

    def __str__(self) -> str:
        """Format timing path as a human-readable string.
        
        Returns:
            str: Formatted multi-line string representation of the timing path.
        """
        lines = [
            f"Startpoint:   {self.startpoint}",
            f"Endpoint:     {self.endpoint}",
            f"Group:        {self.path_group}",
            f"Type:         {self.path_type}",
            f"Required:     {self.required_time}",
            f"Arrival:      {self.arrival_time}",
            f"Slack:        {self.slack}",
            f"Status:       {self.status}",
            "=" * 50
        ]
        return "\n".join(lines)

    
@dataclass 
class TimingReport:
    """
    Container for parsed timing report data.
    
    Attributes:
        paths: List of all timing paths found in the report.
        worst_min_path_index: Index of the path with worst (minimum) slack for min analysis.
        worst_max_path_index: Index of the path with worst (minimum) slack for max analysis.
    """
    paths: list[TimingPath] = field(default_factory=list)
    worst_min_path_index: Optional[int] = None
    worst_max_path_index: Optional[int] = None

    # def get_path(self, index: int) -> TimingPath:
    #     return self.paths[index]

    @property
    def worst_min_path(self) -> Optional[TimingPath]:
        """Get the timing path with the worst slack among min-type paths.
        
        Returns:
            Optional[TimingPath]: The min-type path with minimum slack, or None if not found.
        """
        if self.worst_min_path_index is None:
            return None
        return self.paths[self.worst_min_path_index]

    @property
    def worst_max_path(self) -> Optional[TimingPath]:
        """Get the timing path with the worst slack among max-type paths.
        
        Returns:
            Optional[TimingPath]: The max-type path with minimum slack, or None if not found.
        """
        if self.worst_max_path_index is None:
            return None
        return self.paths[self.worst_max_path_index]


@dataclass
class SummaryStats:
    """Summary statistics for timing analysis.
    
    Attributes:
        total_paths: Total number of timing paths.
        min_paths: Number of min-type paths.
        max_paths: Number of max-type paths.
        violated_paths: Number of paths with negative slack.
        met_paths: Number of paths with non-negative slack.
        worst_slack: Minimum slack value across all paths.
        worst_min_slack: Minimum slack value among min-type paths.
        worst_max_slack: Minimum slack value among max-type paths.
        best_slack: Maximum slack value across all paths.
    """
    total_paths:        int = 0
    min_paths:          int = 0
    max_paths:          int = 0
    violated_paths:     int = 0
    met_paths:          int = 0
    worst_slack:        Optional[float] = None
    worst_min_slack:    Optional[float] = None
    worst_max_slack:    Optional[float] = None
    best_slack:         Optional[float] = None
    
    @classmethod
    def from_report(cls, report: TimingReport) -> 'SummaryStats':
        """Generate summary statistics from a TimingReport.
        
        Args:
            report: TimingReport object containing timing paths to analyze.
            
        Returns:
            SummaryStats: Statistics object with calculated metrics.
        """
        paths_with_slack = [p for p in report.paths if p.slack is not None]
        min_paths = [p for p in paths_with_slack if p.path_type == "min"]
        max_paths = [p for p in paths_with_slack if p.path_type == "max"]
        
        violated = [p for p in paths_with_slack if p.slack < 0]
        met = [p for p in paths_with_slack if p.slack >= 0]
        
        # Calculate worst/best slacks
        all_slacks = [p.slack for p in paths_with_slack]
        min_slacks = [p.slack for p in min_paths]
        max_slacks = [p.slack for p in max_paths]
        
        return cls(
            total_paths=len(report.paths),
            min_paths=len(min_paths),
            max_paths=len(max_paths),
            violated_paths=len(violated),
            met_paths=len(met),
            worst_slack=min(all_slacks) if all_slacks else None,
            worst_min_slack=min(min_slacks) if min_slacks else None,
            worst_max_slack=min(max_slacks) if max_slacks else None,
            best_slack=max(all_slacks) if all_slacks else None,
        )
    
    def __str__(self) -> str:
        """Format summary as a readable report.
        
        Returns:
            str: Formatted multi-line summary report.
        """
        lines = [
            "=" * 50,
            "TIMING REPORT SUMMARY",
            "=" * 50,
            f"Total Paths:          {self.total_paths}",
            f"  Min Type Paths:     {self.min_paths}",
            f"  Max Type Paths:     {self.max_paths}",
            "",
            f"Timing Status:",
            f"  Met Paths:          {self.met_paths}",
            f"  Violated Paths:     {self.violated_paths}",
            "",
            f"Slack Analysis:",
            f"  Worst Overall:      {self.worst_slack:.4f}" if self.worst_slack is not None else "  Worst Overall:      N/A",
            f"  Worst Min:          {self.worst_min_slack:.4f}" if self.worst_min_slack is not None else "  Worst Min:          N/A",
            f"  Worst Max:          {self.worst_max_slack:.4f}" if self.worst_max_slack is not None else "  Worst Max:          N/A",
            f"  Best Slack:         {self.best_slack:.4f}" if self.best_slack is not None else "  Best Slack:         N/A",
            "=" * 50,
        ]
        return "\n".join(lines)


@dataclass
class AnalysisConfig:
    """
    Configuration for timing analysis operations.
    
    Attributes:
        report_file: Path to the timing report file to parse.
        show_summary: Whether to display summary statistics.
        show_worst: Whether to display worst-case paths.
        filter_status: Filter paths by status ('MET' or 'VIOLATED').
        filter_type: Filter paths by type ('min' or 'max').
        filter_group: Filter paths by specific path group name.
        debug: Enable debug-level logging output.
    """
    report_file:        str
    show_summary:       bool = False
    show_worst:         bool = False
    filter_status:      Optional[str] = None
    filter_type:        Optional[str] = None
    filter_group:       Optional[str] = None
    debug:              bool = False
    
    @classmethod
    def from_args(cls, args: argparse.Namespace) -> 'AnalysisConfig':
        """
        Create configuration object from command-line arguments.
        
        Args:
            args: Parsed command-line arguments from argparse.
            
        Returns:
            AnalysisConfig instance populated with argument values.
        """
        return cls(
            report_file=args.report,
            show_summary=args.summary,
            show_worst=args.worst,
            filter_status=args.status,
            filter_type=args.type,
            filter_group=args.group,
            debug=args.debug
        )
    
    def has_filters(self) -> bool:
        """
        Check if any path filters are active.
        
        Returns:
            True if status, type, or group filters are set.
        """
        return any([self.filter_status, self.filter_type, self.filter_group])


def parse_report(filename: str) -> TimingReport:
    """
    Parse an EDA timing report file and extract timing path information.
    
    Args:
        filename: Path to the timing report file.
        
    Returns:
        TimingReport object containing all parsed paths and metadata.
        
    Raises:
        OSError: If the file cannot be opened or read.
    """
    logging.debug(f"Opening timing report: {filename}")
    
    paths: list[TimingPath] = []
    current_path = None

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()

            # ["Startpoint:", Start, Info]
            if line.startswith("Startpoint:"):
                current_path = TimingPath()
                paths.append(current_path)
                current_path.startpoint = line.split(maxsplit=2)[1]
                logging.debug(f"Found path #{len(paths)}: {current_path.startpoint}")

            # ["Startpoint:", End, Info]
            elif line.startswith("Endpoint:") and current_path:
                current_path.endpoint = line.split(maxsplit=2)[1]

            # ["Path Group:", Clk]
            elif line.startswith("Path Group:") and current_path:
                current_path.path_group = line.split(maxsplit=2)[-1]

            # ["Path Type:", Type]
            elif line.startswith("Path Type:") and current_path:
                current_path.path_type = line.split(maxsplit=2)[-1]

            # [time_value, "data required time"]
            elif "data required time" in line and current_path:
                current_path.required_time = float(line.split(maxsplit=1)[0])

            # [time_value, "data arrival time"]
            elif "data arrival time" in line and current_path:
                current_path.arrival_time = float(line.split(maxsplit=1)[0])

            elif "slack" in line and current_path:
                parts = line.split()

                # [slack_value, "slack", "MET/VIOLATED"]
                if len(parts) == 3:
                    # skip invalid lines
                    try:
                        slack = float(parts[0])
                    except ValueError:
                        continue

                    current_path.slack = slack

    logging.info(f"Parsed {len(paths)} timing paths\n")
    
    # Find worst min path (lowest slack among "min" type paths)
    min_paths = [(i, path) for i, path in enumerate(paths) 
                 if path.path_type == "min" and path.slack is not None]
    worst_min_idx = min(min_paths, key=lambda x: x[1].slack)[0] if min_paths else None
    
    # Find worst max path (lowest slack among "max" type paths)
    max_paths = [(i, path) for i, path in enumerate(paths) 
                 if path.path_type == "max" and path.slack is not None]
    worst_max_idx = min(max_paths, key=lambda x: x[1].slack)[0] if max_paths else None
    
    report = TimingReport(paths=paths)
    report.worst_min_path_index = worst_min_idx
    report.worst_max_path_index = worst_max_idx
    
    logging.debug(f"Worst min path index: {worst_min_idx}")
    logging.debug(f"Worst max path index: {worst_max_idx}")
    
    return report


def print_worst_paths(report: TimingReport) -> None:
    """
    Display worst min and max paths from the report.
    
    Args:
        report: TimingReport containing parsed timing paths.
    """
    worst_min = report.worst_min_path
    worst_max = report.worst_max_path
    
    print("WORST (MIN) PATH")
    print(f"{'='*50}")
    print(worst_min if worst_min else "No min paths found")

    print("\nWORST (MAX) PATH")
    print(f"{'='*50}")
    print(worst_max if worst_max else "No max paths found")


def print_filtered_paths(report: TimingReport, config: AnalysisConfig) -> None:
    """Display paths filtered by status, type, or group.
    
    Filters are applied with AND logic when multiple are specified.
    
    Args:
        report: TimingReport containing parsed timing paths.
        config: AnalysisConfig with filter settings.
    """
    filtered_paths = report.paths
    filters_applied = []
    
    if config.filter_status:
        filtered_paths = [p for p in filtered_paths if p.status == config.filter_status]
        filters_applied.append(f"status={config.filter_status}")
    
    if config.filter_type:
        filtered_paths = [p for p in filtered_paths if p.path_type == config.filter_type]
        filters_applied.append(f"type={config.filter_type}")
    
    if config.filter_group:
        filtered_paths = [p for p in filtered_paths if p.path_group == config.filter_group]
        filters_applied.append(f"group={config.filter_group}")
    
    print(f"{'='*50}")
    print(f"FILTERED PATHS: {', '.join(filters_applied)}")
    print(f"{'='*50}")
    print(f"Found {len(filtered_paths)} matching paths\n")
    
    for i, path in enumerate(filtered_paths, 1):
        print(f"Path #{i}:")
        print(path)
        print()


def run_analysis(config: AnalysisConfig, report: TimingReport) -> None:
    """Execute timing analysis operations based on configuration.
    
    Displays summary, worst paths, or filtered results according to the
    provided configuration.
    
    Args:
        config: AnalysisConfig specifying which operations to perform.
        report: TimingReport containing parsed timing data.
    """
    if config.show_summary:
        summary = SummaryStats.from_report(report)
        print(summary)
    
    if config.show_worst:
        print_worst_paths(report)
    
    if config.has_filters():
        print_filtered_paths(report, config)


def main():
    """Main entry point for the EDA timing report parser CLI.
    
    Parses command-line arguments, configures logging, parses the timing report
    file, and executes requested analysis operations.
    """
    parser = argparse.ArgumentParser(description="EDA Timing Report Parser")
    parser.add_argument("report", help="Path to timing report file")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--summary", action="store_true", help="Show summary statistics")
    parser.add_argument("--worst", action="store_true", help="Show worst paths")
    parser.add_argument("--status", choices=["MET", "VIOLATED"], 
                        help="Filter paths by status (MET or VIOLATED)")
    parser.add_argument("--type", choices=["min", "max"],
                        help="Filter paths by type (min or max)")
    parser.add_argument("--group", type=str,
                        help="Filter paths by path group name")

    args = parser.parse_args()
    config = AnalysisConfig.from_args(args)
    
    try:
        # Configure logging
        if config.debug:
            logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
        else:
            logging.basicConfig(level=logging.INFO, format='%(message)s')
        
        # Parse report and run analysis
        report = parse_report(config.report_file)
        run_analysis(config, report)

    # echo $? == 1 if file not found or other OSError occurs
    except OSError as e:
        print(f"ERROR ({type(e).__name__}): {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
