"""What every AI adapter returns, the errors it can raise, and the check on each answer."""
from dataclasses import dataclass
from typing import Protocol


class AiUnavailable(Exception):
    """The AI could not give a usable suggestion (timeout, error, bad answer).
    Callers catch this one error and let staff carry on by hand."""


class AiConfigError(Exception):
    """An AI setting in .env is missing or wrong. The message names the setting, never its value."""


@dataclass(frozen=True)
class Suggestion:
    """One AI triage suggestion (ERD page 4, AI suggestion). Staff decide what happens to it."""

    summary: str
    missing_info: tuple[str, ...]
    medical_advice_flag: bool
    suggested_category: str
    suggested_priority: str
    rationale: str
    support_option: str
    source: str  # "fake" or "real"


class AiAdapter(Protocol):
    """The one interface the rest of HeatShield uses, whichever AI is behind it."""

    def suggest(self, description: str) -> Suggestion: ...


TEXT_FIELDS = ("summary", "suggested_category", "suggested_priority", "rationale", "support_option")


def parse_suggestion(data, source):
    """Turn an AI answer (a dict) into a Suggestion, or raise AiUnavailable if its shape is wrong.
    Whether the category and priority are allowed values is checked later by triage."""
    if not isinstance(data, dict):
        raise AiUnavailable("AI answer is not a JSON object")
    for name in TEXT_FIELDS:
        value = data.get(name)
        if not isinstance(value, str) or not value.strip():
            raise AiUnavailable(f"AI answer has a missing or empty field: {name}")
    if type(data.get("medical_advice_flag")) is not bool:
        raise AiUnavailable("AI answer has a missing or invalid field: medical_advice_flag")
    missing_info = data.get("missing_info")
    if not isinstance(missing_info, list) or not all(isinstance(item, str) for item in missing_info):
        raise AiUnavailable("AI answer has a missing or invalid field: missing_info")
    return Suggestion(
        summary=data["summary"].strip(),
        missing_info=tuple(missing_info),
        medical_advice_flag=data["medical_advice_flag"],
        suggested_category=data["suggested_category"].strip(),
        suggested_priority=data["suggested_priority"].strip(),
        rationale=data["rationale"].strip(),
        support_option=data["support_option"].strip(),
        source=source,
    )
