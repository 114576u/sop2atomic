"""
Wrapper for OpenAI API calls using the Responses API.
"""

from typing import Dict, Any
from openai import OpenAI
from sop2atomic.llm.prompt_builder import build_system_prompt


class LLMClient:
    """A thin wrapper around the OpenAI Responses API."""

    def __init__(self, model: str = "gpt-5.1"):
        self.client = OpenAI()
        self.model = model

    def call(self, user_prompt: str) -> Dict[str, Any]:
        """
        Send a prompt to the LLM and return parsed JSON.
        """
        response = self.client.responses.create(
            model=self.model,
            instructions=build_system_prompt(),
            input=[{"role": "user", "content": user_prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,
        )

        # Extract the JSON text
        content = response.output[0].content[0].text
        return content
