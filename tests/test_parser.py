import pytest
from pathlib import Path
from eda_file_parser.parser import parse_report, TimingPath, TimingReport

# scope='module' means this fixture is created once per test file, not once per test function
@pytest.fixture(scope="module")
def reports_dir():
    """Fixture providing path to reports directory.
    
    Scope='module' means this is created once per test file,
    not once per test function.
    """
    project_root = Path(__file__).parent.parent
    return project_root / "reports"


@pytest.fixture
def report_paths(reports_dir):
    """Fixture providing paths to all test report files.
    
    This fixture depends on reports_dir fixture (composition).
    """
    return {
        "simple_met": reports_dir / "simple_met.rpt",
        "simple_violated": reports_dir / "simple_violated.rpt",
        "timing_full": reports_dir / "timing_full.rpt",
        "mixed_paths": reports_dir / "mixed_paths.rpt",
        "empty": reports_dir / "empty.rpt",
    }


# @pytest.mark.unit
class TestParser:
    """Test suite for timing report parser."""
    
    def test_parse_simple_met_report(self, report_paths):
        """Test parsing a simple report with met timing paths."""
        report = parse_report(str(report_paths["simple_met"]))
        
        assert report is not None
        assert len(report.paths) > 0

        path = report.paths[0]
        assert path.startpoint == "reg_a"
        assert path.endpoint == "reg_b"
        assert path.path_group == "clk"
        assert path.path_type in ["min", "max"]
        assert path.slack is not None
        assert path.status == "MET"
    
    def test_parse_simple_violated_report(self, report_paths):
        """Test parsing a report with violated timing paths."""
        report = parse_report(str(report_paths["simple_violated"]))
        
        assert report is not None
        assert len(report.paths) > 0

        path = report.paths[0]
        assert path.startpoint == "reg_x"
        assert path.endpoint == "reg_y"
        assert path.path_group == "clk"
        assert path.path_type in ["min", "max"]
        assert path.slack is not None
        assert path.status == "VIOLATED"

    def test_parse_empty_report(self, report_paths):
        """Test parsing an empty report file."""
        report = parse_report(str(report_paths["empty"]))
        
        assert report is not None
        assert len(report.paths) == 0

        # path = report.paths[0]

    def test_parse_nonexistent_file(self):
        """Test parsing non-existent file raises appropriate error."""
        with pytest.raises(FileNotFoundError):
            parse_report("nonexistent_file.rpt")

    @pytest.mark.parametrize("report_name, expected_min_paths", [
        ("simple_met", 1),
        ("simple_violated", 1),
        ("mixed_paths", 4),
        ("timing_full", 102),
    ])
    def test_path_count_validation(self, report_paths, report_name, expected_min_paths):
        """Test various reports have expected minimum path counts."""
        report = parse_report(str(report_paths[report_name]))
        assert len(report.paths) >= expected_min_paths

    def test_reports_directory_exists(self, reports_dir):
        """Verify reports directory is accessible."""
        assert reports_dir.exists()
        assert reports_dir.is_dir()
    
    def test_report_files_exist(self, report_paths):
        """Verify all test report files exist."""
        assert report_paths["timing_full"].exists()
        assert report_paths["simple_met"].exists()
        assert report_paths["simple_violated"].exists()
        assert report_paths["mixed_paths"].exists()
        assert report_paths["empty"].exists()


# @pytest.mark.unit
class TestTimingPath:
    """Test suite for TimingPath data class."""
    
    def test_timing_path_initialization(self):
        """Test TimingPath initializes with correct attributes."""
        path = TimingPath(
            startpoint="reg_a",
            endpoint="reg_b",
            path_group="clk",
            path_type="min",
            slack=0.5
        )
        
        assert path.startpoint == "reg_a"
        assert path.endpoint == "reg_b"
        assert path.path_group == "clk"
        assert path.path_type == "min"
        assert path.slack == 0.5

    @pytest.mark.parametrize("slack, expected_status", [
        (0.5, "MET"),
        (-0.1, "VIOLATED"),
        (0.0, "MET"),
        (None, "UNKNOWN"),
    ])
    def test_status_determination(self, slack, expected_status):
        """Test status determination for various slack values."""
        path = TimingPath(slack=slack)
        assert path.status == expected_status


# @pytest.mark.unit
class TestTimingReport:
    """Test suite for TimingReport class."""
    
    def test_report_initialization(self):
        """Test TimingReport initializes with empty paths list."""
        report = TimingReport()
        assert report.paths == []
        assert report.worst_min_path_index is None
        assert report.worst_max_path_index is None
