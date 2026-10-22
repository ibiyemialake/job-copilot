"""Thin wrapper around the Claude API that always returns parsed JSON."""
import json
import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")  # ANTHROPIC_API_KEY, COPILOT_MODEL

MODEL = os.getenv("COPILOT_MODEL", "claude-sonnet-5-5")
_client = Anthropic()  # reads ANTHROPIC_API_KEY from the environment


def ask_json(system: str, user: str, max_tokens: int = 2000) -> dict | list:
    """Send one prompt, expect JSON back, parse it."""
    resp = _client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system + "\n\nRespond with valid JSON only. No prose, no markdown fences.",
        messages=[{"role": "user", "content": user}],
    )
    if resp.stop_reason == "max_tokens":
        raise RuntimeError(f"Reply cut off at max_tokens={max_tokens}; raise the limit.")
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(text)
