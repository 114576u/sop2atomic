from sop2atomic.llm.prompt_builder import build_system_prompt, build_user_prompt


def test_build_system_prompt_contains_json_schema_keywords():
    """Ensure the system prompt clearly defines JSON schema and key fields."""
    system_prompt = build_system_prompt()

    # Basic sanity checks: important keywords and structure
    assert "STRICT JSON" in system_prompt
    assert "\"sop_id\"" in system_prompt
    assert "\"steps\"" in system_prompt
    assert "\"atomic_actions\"" in system_prompt
    assert "\"component_id\"" in system_prompt
    assert "\"parameters\"" in system_prompt


def test_build_user_prompt_includes_sop_card_and_steps():
    """The user prompt should include SOP card fields and step text."""
    sop_data = {
        "sop_card": {
            "SCHRODERS_ID": "TEST001",
            "CLIENT": "Test Client",
        },
        "steps": [
            {
                "step_number": "1",
                "action": "Open the shared mailbox.",
                "notes": "",
            },
            {
                "step_number": "2",
                "action": "Download the instruction file.",
                "notes": "Be careful with the filename.",
            },
        ],
    }

    catalogue = [
        {
            "id": "1,1",
            "id_name": "OPEN_FOLDER",
            "category": "Files & Folders",
            "description": "Open a local or network folder",
            "parameters": ["path"],
        }
    ]

    user_prompt = build_user_prompt(sop_data, catalogue)

    # SOP card info must be present
    assert "SCHRODERS_ID" in user_prompt
    assert "TEST001" in user_prompt
    assert "CLIENT" in user_prompt
    assert "Test Client" in user_prompt

    # Steps must be present
    assert "Step 1: Open the shared mailbox." in user_prompt
    assert "Step 2: Download the instruction file." in user_prompt
    assert "Notes: Be careful with the filename." in user_prompt

    # Catalogue info must be present
    assert "OPEN_FOLDER" in user_prompt
    assert "Files & Folders" in user_prompt
    assert "params=['path']" in user_prompt
