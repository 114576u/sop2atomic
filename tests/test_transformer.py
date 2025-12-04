import json

import sop2atomic.transformers.sop_to_atomic_transformer as tr_mod
from sop2atomic.transformers.sop_to_atomic_transformer import SopToAtomicTransformer


class FakeLLMClient:
    """
    Fake LLM client used for tests.

    It records the last prompt it received and returns a fixed JSON payload
    that mimics the structure we expect from the real LLM.
    """

    def __init__(self, model: str = "gpt-5.1"):
        self.model = model
        self.last_prompt: str | None = None

    def call(self, user_prompt: str) -> str:
        self.last_prompt = user_prompt

        # A minimal, valid JSON response in the agreed schema
        fake_response = {
            "sop_id": None,  # we want the transformer to inject it from SOP Card
            "steps": [
                {
                    "step_number": "1",
                    "original_action": "Open the shared mailbox.",
                    "notes": "",
                    "atomic_actions": [
                        {
                            "component_id": "1,1",
                            "component_name": "OPEN_FOLDER",
                            "category": "Files & Folders",
                            "parameters": {
                                "path": r"X:\\SharedMailbox",
                            },
                        }
                    ],
                }
            ],
        }
        return json.dumps(fake_response)


def test_transformer_uses_llm_and_injects_sop_id(monkeypatch):
    """
    The transformer should:
      - build a prompt from SOP + catalogue
      - call the LLM client once
      - parse the JSON
      - inject SOP ID from the SOP card if it is missing in the response
    """

    # Arrange: synthetic SOP data
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
            }
        ],
    }

    # Arrange: minimal catalogue with one component
    catalogue = [
        {
            "id": "1,1",
            "id_name": "OPEN_FOLDER",
            "category": "Files & Folders",
            "description": "Open a local or network folder",
            "parameters": ["path"],
        }
    ]

    # Monkeypatch the LLMClient used inside the transformer module
    monkeypatch.setattr(tr_mod, "LLMClient", FakeLLMClient)

    transformer = SopToAtomicTransformer(model="gpt-5.1")

    # Act
    result = transformer.transform(sop_data, catalogue)

    # Assert: the result structure
    assert result["sop_id"] == "TEST001"  # injected from SOP card
    assert "steps" in result
    assert len(result["steps"]) == 1

    step = result["steps"][0]
    assert step["step_number"] == "1"
    assert step["original_action"] == "Open the shared mailbox."
    assert len(step["atomic_actions"]) == 1

    atomic = step["atomic_actions"][0]
    assert atomic["component_id"] == "1,1"
    assert atomic["component_name"] == "OPEN_FOLDER"
    assert atomic["category"] == "Files & Folders"
    assert atomic["parameters"]["path"] == r"X:\\SharedMailbox"

    # Assert: the fake client actually received a prompt containing SOP info
    # (we don't deeply inspect it here, just sanity-check some key strings)
    assert transformer.llm.last_prompt is not None
    assert "SCHRODERS_ID" in transformer.llm.last_prompt
    assert "TEST001" in transformer.llm.last_prompt
    assert "Open the shared mailbox." in transformer.llm.last_prompt
    assert "OPEN_FOLDER" in transformer.llm.last_prompt
