from pathlib import Path

import pandas as pd

from sop2atomic.catalogue.atomic_catalogue_loader import load_atomic_catalogue


def _create_test_catalogue(path: Path) -> None:
    """
    Helper: create a small synthetic atomic components catalogue as an Excel file.
    """
    data = {
        "Category": ["Files & Folders", "Email Operations", "Validations & Metadata"],
        "ID": ["1,1", "4,4", "5,1"],
        "ID_NAME": ["OPEN_FOLDER", "SET_EMAIL_RECIPIENTS", "VALIDATE_FILE_EXISTS"],
        "Description": [
            "Open a local or network folder",
            "Define To/Cc/Bcc addresses",
            "Confirm that a required file is available",
        ],
        # Parameters can be separated by newlines or commas;
        # the loader should handle both.
        "Parameters": [
            "path",  # single parameter
            "to\ncc\nbcc",  # multi-line style
            "",  # no parameters
        ],
    }
    df = pd.DataFrame(data)
    df.to_excel(path, index=False)


def test_load_atomic_catalogue_basic(tmp_path):
    """
    The loader should return a list of component dicts with the expected keys
    and parsed parameters.
    """
    xlsx_path = tmp_path / "atomic_catalogue_test.xlsx"
    _create_test_catalogue(xlsx_path)

    components = load_atomic_catalogue(str(xlsx_path))

    # We expect three components
    assert len(components) == 3

    first = components[0]
    assert first["id"] == "1,1"
    assert first["id_name"] == "OPEN_FOLDER"
    assert first["category"] == "Files & Folders"
    assert first["description"] == "Open a local or network folder"
    assert first["parameters"] == ["path"]

    second = components[1]
    # Ensure parameters are split correctly into a list
    assert second["id_name"] == "SET_EMAIL_RECIPIENTS"
    assert second["parameters"] == ["to", "cc", "bcc"]


def test_load_atomic_catalogue_empty_parameters(tmp_path):
    """
    When the 'Parameters' cell is empty, the loader should return an empty list
    for that component's parameters.
    """
    xlsx_path = tmp_path / "atomic_catalogue_test.xlsx"
    _create_test_catalogue(xlsx_path)

    components = load_atomic_catalogue(str(xlsx_path))

    third = components[2]
    assert third["id_name"] == "VALIDATE_FILE_EXISTS"
    assert third["parameters"] == []
