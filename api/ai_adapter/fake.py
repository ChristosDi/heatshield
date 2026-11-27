"""The fake AI: recorded answers from fixtures/responses.json, so tests and demos need no internet or key.

Every answer it gives is marked source="fake", so staff can always tell it is a mock and not the real AI.
"""
import json
from pathlib import Path

from .base import AiUnavailable, parse_suggestion

FIXTURES = Path(__file__).parent / "fixtures" / "responses.json"


def normalise(description):
    """Lower case with single spaces, so small typing differences still find the recorded answer."""
    return " ".join(description.lower().split())


class FakeAdapter:
    """Gives the recorded answer for a known description, or the default answer for anything else."""

    def __init__(self, fail=False):
        # fail=True pretends the AI is down, so other features can test what staff see then.
        self.fail = fail

        recorded = json.loads(FIXTURES.read_text(encoding="utf-8"))
        self.default = parse_suggestion(recorded["default"], source="fake")
        self.answers = {}
        for case in recorded["cases"]:
            self.answers[normalise(case["description"])] = parse_suggestion(case["response"], source="fake")

    def suggest(self, description):
        if self.fail:
            raise AiUnavailable("The fake AI is set to fail")
        return self.answers.get(normalise(description), self.default)