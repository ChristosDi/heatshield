"""Tests for the real AI: what it sends to the AI service, and what it does with every kind of answer.

How the tests work:
- They never use the internet. `monkeypatch` swaps Python's own internet call (urllib.request.urlopen)
  for a pretend AI service, written below, that answers whatever each test needs.
- That way they can also pretend the service is slow, broken or confused, which the real one
  never does on demand.
- The address, model and key are made up, and all descriptions are fictional.

Run from the api/ folder with: python -m pytest tests/test_ai_adapter_real.py
"""
import dataclasses
import io
import json
import urllib.error
import urllib.request

import pytest

from ai_adapter import AiUnavailable, RealAdapter, Suggestion
from ai_adapter.prompt import CATEGORIES, PRIORITIES, RESPONSE_SCHEMA, SYSTEM_PROMPT

FAKE_KEY = "test-key-not-real"
DESCRIPTION = "My flat is too hot and I have nowhere cool to go this afternoon."

# A good answer, in the shape our instructions ask for.
GOOD_ANSWER = {
    "summary": "Resident's flat is too hot and they need somewhere cool this afternoon.",
    "missing_info": ["Which area does the resident live in?"],
    "medical_advice_flag": False,
    "suggested_category": "cooling_space",
    "suggested_priority": "high",
    "rationale": "The resident needs somewhere cool today.",
    "support_option": "Offer a place at the nearest open cooling centre.",
}


def service_reply(answer):
    """Wrap an answer the way a chat-completions service does: as text inside choices[0].message."""
    return {"choices": [{"message": {"role": "assistant", "content": json.dumps(answer)}}]}


class PretendService:
    """Stands in for urllib.request.urlopen. It remembers what was sent and gives back a chosen reply."""

    def __init__(self, reply=None, error=None):
        self.reply = reply  # what the service answers (a dict, or raw bytes)
        self.error = error  # or the error it raises instead
        self.request = None
        self.timeout = None

    def __call__(self, request, timeout=None):
        self.request = request
        self.timeout = timeout
        if self.error is not None:
            raise self.error
        if isinstance(self.reply, bytes):
            return io.BytesIO(self.reply)
        return io.BytesIO(json.dumps(self.reply).encode("utf-8"))


@pytest.fixture
def real_ai():
    return RealAdapter(base_url="https://ai.example.test/v1", model="test-model", api_key=FAKE_KEY)


@pytest.fixture
def service(monkeypatch):
    """A pretend service that gives a good answer. A test can change what it does before calling the AI."""
    pretend = PretendService(reply=service_reply(GOOD_ANSWER))
    monkeypatch.setattr(urllib.request, "urlopen", pretend)
    return pretend


def sent_body(service):
    return json.loads(service.request.data)


# --- A good answer ---

def test_a_good_answer_becomes_a_suggestion_marked_real(real_ai, service):
    suggestion = real_ai.suggest(DESCRIPTION)

    assert suggestion.suggested_category == "cooling_space"
    assert suggestion.suggested_priority == "high"
    assert suggestion.source == "real"


# --- What is sent ---

def test_it_posts_to_the_chat_completions_address(real_ai, service):
    real_ai.suggest(DESCRIPTION)

    assert service.request.full_url == "https://ai.example.test/v1/chat/completions"
    assert service.request.get_method() == "POST"


def test_the_key_is_sent_only_in_the_authorization_header(real_ai, service):
    real_ai.suggest(DESCRIPTION)

    assert service.request.get_header("Authorization") == f"Bearer {FAKE_KEY}"
    assert FAKE_KEY not in service.request.full_url
    assert FAKE_KEY not in service.request.data.decode("utf-8")


def test_it_sends_only_the_model_the_instructions_and_the_description(real_ai, service):
    """Nothing else about the request or the resident is sent (data minimisation)."""
    real_ai.suggest(DESCRIPTION)

    body = sent_body(service)
    assert set(body) == {"model", "messages", "response_format"}
    assert body["model"] == "test-model"
    assert body["messages"] == [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": DESCRIPTION},
    ]


def test_it_asks_for_the_strict_answer_shape(real_ai, service):
    real_ai.suggest(DESCRIPTION)

    response_format = sent_body(service)["response_format"]
    assert response_format == {"type": "json_schema", "json_schema": RESPONSE_SCHEMA}


def test_the_answer_shape_matches_the_suggestion_and_the_allowed_values():
    """If someone adds a field to Suggestion, or changes the lists, this fails until the shape is updated."""
    schema = RESPONSE_SCHEMA["schema"]
    suggestion_fields = {field.name for field in dataclasses.fields(Suggestion)} - {"source"}

    assert RESPONSE_SCHEMA["strict"] is True
    assert set(schema["properties"]) == suggestion_fields
    assert set(schema["required"]) == suggestion_fields
    assert schema["additionalProperties"] is False
    assert schema["properties"]["suggested_category"]["enum"] == CATEGORIES
    assert schema["properties"]["suggested_priority"]["enum"] == PRIORITIES


def test_it_waits_ten_seconds_at_most(real_ai, service):
    real_ai.suggest(DESCRIPTION)

    assert service.timeout == 10


# --- Every kind of problem becomes AiUnavailable, so staff can carry on by hand ---

def http_error(code):
    return urllib.error.HTTPError("https://ai.example.test/v1/chat/completions", code, "Error", {}, io.BytesIO(b""))


PROBLEMS = {
    "too slow": PretendService(error=TimeoutError("timed out")),
    "cannot be reached": PretendService(error=urllib.error.URLError("no route to host")),
    "connection dropped": PretendService(error=ConnectionResetError("reset")),
    "refuses the request (400)": PretendService(error=http_error(400)),
    "wrong key (401)": PretendService(error=http_error(401)),
    "too many requests (429)": PretendService(error=http_error(429)),
    "server error (500)": PretendService(error=http_error(500)),
    "reply is not JSON": PretendService(reply=b"<html>Service unavailable</html>"),
    "reply has no choices": PretendService(reply={"error": {"message": "something went wrong"}}),
    "reply has an empty list of choices": PretendService(reply={"choices": []}),
    "answer is plain text, not JSON": PretendService(
        reply={"choices": [{"message": {"content": "Sure! The category is cooling_space."}}]}
    ),
    "answer has no text": PretendService(reply={"choices": [{"message": {"content": None}}]}),
    "answer is missing a field": PretendService(
        reply=service_reply({key: value for key, value in GOOD_ANSWER.items() if key != "summary"})
    ),
}


# This test runs once for each problem above.
@pytest.mark.parametrize("problem", PROBLEMS)
def test_every_problem_becomes_ai_unavailable_without_showing_the_key(real_ai, monkeypatch, problem):
    monkeypatch.setattr(urllib.request, "urlopen", PROBLEMS[problem])

    with pytest.raises(AiUnavailable) as caught:
        real_ai.suggest(DESCRIPTION)

    assert FAKE_KEY not in str(caught.value)


@pytest.mark.parametrize(
    ("problem", "message"),
    [
        ("too slow", "10 seconds"),
        ("wrong key (401)", "HTTP 401"),
        ("too many requests (429)", "HTTP 429"),
        ("cannot be reached", "could not be reached"),
    ],
)
def test_the_message_says_what_went_wrong(real_ai, monkeypatch, problem, message):
    """A clear message tells whoever reads the log what to fix, for example a wrong key or too many requests."""
    monkeypatch.setattr(urllib.request, "urlopen", PROBLEMS[problem])

    with pytest.raises(AiUnavailable, match=message):
        real_ai.suggest(DESCRIPTION)


def test_the_key_is_not_shown_when_the_ai_is_printed(real_ai):
    """Logs and error pages often print objects, so printing the AI must not reveal the key."""
    assert FAKE_KEY not in repr(real_ai)
    assert FAKE_KEY not in str(real_ai)