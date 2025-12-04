from pathlib import Path

from sop2atomic.parser.sop_parser import parse_sop_document

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_parse_simple_sop_metadata():
    """
    Basic sanity check: the parser should extract SOP card metadata correctly
    from the simple synthetic SOP.
    """
    sop_path = FIXTURES_DIR / "sample_sop_simple.docx"

    sop_data = parse_sop_document(str(sop_path))

    assert "sop_card" in sop_data
    card = sop_data["sop_card"]

    assert card.get("SCHRODERS_ID") == "TEST001"
    assert card.get("CLIENT") == "Test Client"
    assert card.get("REPORT_NAME") == "Test Report"


def test_parse_simple_sop_steps():
    """
    The simple SOP contains 3 sequential steps; we expect those back as a list
    of dicts with step_number, action, and notes.
    """
    sop_path = FIXTURES_DIR / "sample_sop_simple.docx"

    sop_data = parse_sop_document(str(sop_path))
    steps = sop_data["steps"]

    assert len(steps) == 3

    # First step
    assert steps[0]["step_number"] == "1"
    assert "Open the shared mailbox" in steps[0]["action"]
    assert steps[0]["notes"] == ""

    # Third step
    assert steps[2]["step_number"] == "3"
    assert "Notify the operations team" in steps[2]["action"]


def test_parse_complex_sop_steps_and_notes():
    """
    The complex SOP includes a note in the second step and 5 total steps.
    We verify both count and that the Notes column is captured.
    """
    sop_path = FIXTURES_DIR / "sample_sop_complex.docx"

    sop_data = parse_sop_document(str(sop_path))
    steps = sop_data["steps"]

    assert len(steps) == 5

    # Check step numbers are sequential strings
    assert [s["step_number"] for s in steps] == ["1", "2", "3", "4", "5"]

    # Second step has a note in the synthetic SOP
    assert "reminder email" in steps[1]["action"]
    assert steps[1]["notes"] == "Conditional step"
