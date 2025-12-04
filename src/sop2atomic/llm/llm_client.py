"""
Wrapper for OpenAI API calls using the Responses API.

This client is used by the SopToAtomicTransformer in production. For tests,
LLMClient is typically monkeypatched with a fake implementation.
"""

import os
from openai import OpenAI
from sop2atomic.llm.prompt_builder import build_system_prompt


class LLMClient:
    """A thin wrapper around the OpenAI Responses API."""

    def __init__(self, model: str = "gpt-5.1"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Environment variable OPENAI_API_KEY is not set")

        # The OpenAI client will pick up the key from here
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def call(self, user_prompt: str) -> str:
        """
        Send a prompt to the LLM and return the raw JSON string.

        The actual parsing into Python objects is handled by the response
        interpreter (parse_llm_json), so this method only returns a string.
        """
        response = self.client.responses.create(
            model=self.model,
            instructions=build_system_prompt(),
            input=[{"role": "user", "content": user_prompt}],
            temperature=0.1,
        )

        # Depending on the exact SDK version, the path to the content may differ.
        # For the current Responses API, the JSON payload is returned as text content.
        #
        # Here we assume a structure like:
        #   response.output[0].content[0].text
        #
        # If you ever see an AttributeError here, you can print(response)
        # once locally and adjust this field access accordingly.
        return response.output[0].content[0].text  # type: ignore[union-attr]
