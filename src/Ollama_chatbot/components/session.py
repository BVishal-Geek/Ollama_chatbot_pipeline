# src/ollama_chatbot/components/session.py

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from uuid import uuid4
from ollama import chat, ChatResponse


@dataclass
class Session:
    """
    Represents a single evaluation session for a research paper.

    The session is application-stateful:
    - Holds the system prompt (rules / schema)
    - Holds the current query (paper text)
    - Sends both together to the LLM
    """

    system_prompt: str
    model: str = "gemma3:12b"
    session_id: str = field(default_factory=lambda: uuid4().hex)

    query: Optional[str] = None
    last_response: Optional[Dict[str, Any]] = None

    def build_messages(self) -> list[dict]:
        """
        Build Ollama-compatible messages.
        """
        if self.query is None:
            raise RuntimeError("Query is not set for the session")

        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.query},
        ]

    def run(self) -> Dict[str, Any]:
        """
        Execute the LLM call and return the response.

        Returns:
            Parsed response content as a dictionary-like object.
        """
        messages = self.build_messages()

        response: ChatResponse = chat(
            model=self.model,
            messages=messages
        )

        # Store raw response for debugging / auditing
        self.last_response = response

        # Ollama ChatResponse usually returns text here
        return response["message"]["content"]