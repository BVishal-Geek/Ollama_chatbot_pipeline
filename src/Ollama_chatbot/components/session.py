# src/ollama_chatbot/components/session.py

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from uuid import uuid4
from Ollama_chatbot.client.client import get_openai_client
from Ollama_chatbot.constants.constant import MAX_RETRIES


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
    model: str = "gpt-3.5-turbo"
    session_id: str = field(default_factory=lambda: uuid4().hex)
    retry_count: int = 0 
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
            {"role": "user", "content": self.query}
        ]

    def run(self) -> Dict[str, Any]:
        """
        Execute the LLM call and return the response.

        Returns:
            Parsed response content as a dictionary-like object.
        """
        client = get_openai_client()
        messages = self.build_messages()

        stream = client.responses.create(
            model=self.model,
            input=messages,
            temperature=0,
            stream=True
        )

        final_response = None

        for event in stream:
            # This is the ONLY event that contains the full response
            if event.type == "response.completed":
                final_response = event.response

        if final_response is None:
            raise RuntimeError("LLM did not return a completed response")

        # Extract JSON text
        text = final_response.output[0].content[0].text

        self.last_response = final_response
        return text
       
        

       
       