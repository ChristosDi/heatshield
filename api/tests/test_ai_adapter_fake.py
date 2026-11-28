"""Tests for choosing the AI and for the fake AI.

What is tested:
- One setting, AI_MODE in .env, decides which AI the app uses:
  "fake" (or not set) gives the fake AI, "real" gives the real AI service.
- The fake AI gives the same recorded answer every time, with no internet and no API key.

How the tests work:
- `monkeypatch` is a pytest tool that changes a setting or a function for one test only,
  then puts it back. So these tests ignore your own .env and never affect each other.
- The settings for the real AI are made up, so nothing is ever sent anywhere.
- All descriptions are fictional.

Run from the api/ folder with: python -m pytest tests/test_ai_adapter_fake.py
"""
import json
import urllib.request

import pytest

from ai_adapter import AiConfigError, AiUnavailable, FakeAdapter, RealAdapter, get_adapter
from ai_adapter.base import parse_suggestion
from ai_adapter.fake import FIXTURES
from ai_adapter.prompt import CATEGORIES, PRIORITIES
from app.requests import constants

# A description that has a recorded answer in ai_adapter/fixtures/responses.json
HOT_FLAT_REQUEST = "My flat is too hot and I have nowhere cool to go this afternoon."


@pytest.fixture
def real_ai_settings(monkeypatch):
    """Pretend .env is set up for the real AI, with made-up values."""
    monkeypatch.setenv("AI_MODE", "real")
    monkeypatch.setenv("AI_BASE_URL", "https://ai.example.test/v1")
    monkeypatch.setenv("AI_MODEL", "test-model")
    monkeypatch.setenv("AI_API_KEY", "test-key-not-real")


# --- Choosing the AI with AI_MODE ---

def test_the_fake_is_used_when_ai_mode_is_not_set(monkeypatch):
    """A fresh clone with no .env must work, so the fake is the default."""
    monkeypatch.delenv("AI_MODE", raising=False)

    adapter = get_adapter()

    assert isinstance(adapter, FakeAdapter)


def test_ai_mode_fake_gives_the_fake(monkeypatch):
    monkeypatch.setenv("AI_MODE", "fake")

    adapter = get_adapter()

    assert isinstance(adapter, FakeAdapter)


def test_ai_mode_real_gives_the_real_ai(real_ai_settings):
    adapter = get_adapter()

    assert isinstance(adapter, RealAdapter)


def test_an_unknown_ai_mode_is_refused(monkeypatch):
    """A typo such as AI_MODE=maybe stops with a clear message instead of guessing."""
    monkeypatch.setenv("AI_MODE", "maybe")

    with pytest.raises(AiConfigError, match="AI_MODE"):
        get_adapter()


# This test runs three times, once for each setting the real AI needs.
@pytest.mark.parametrize("setting", ["AI_BASE_URL", "AI_MODEL", "AI_API_KEY"])
def test_the_real_ai_says_which_setting_is_missing(real_ai_settings, monkeypatch, setting):
    monkeypatch.delenv(setting)

    with pytest.raises(AiConfigError, match=setting):
        get_adapter()


def test_the_real_ai_refuses_an_address_without_https(real_ai_settings, monkeypatch):
    """Plain http:// would send the API key unencrypted."""
    monkeypatch.setenv("AI_BASE_URL", "http://ai.example.test/v1")

    with pytest.raises(AiConfigError, match="https"):
        get_adapter()


# --- The fake AI ---

def test_the_fake_returns_the_recorded_answer():
    suggestion = FakeAdapter().suggest(HOT_FLAT_REQUEST)

    assert suggestion.suggested_category == "cooling_space"
    assert suggestion.source == "fake"


def test_the_fake_gives_the_same_answer_every_time():
    first = FakeAdapter().suggest(HOT_FLAT_REQUEST)
    second = FakeAdapter().suggest(HOT_FLAT_REQUEST)

    assert first == second


def test_the_fake_ignores_capitals_and_extra_spaces():
    messy = "  my flat is TOO hot and I have   nowhere cool to go this afternoon. "

    assert FakeAdapter().suggest(messy) == FakeAdapter().suggest(HOT_FLAT_REQUEST)


def test_the_fake_gives_its_default_answer_for_anything_else():
    fake = FakeAdapter()

    suggestion = fake.suggest("Something nobody recorded")

    assert suggestion == fake.default


def test_the_fake_never_uses_the_internet(monkeypatch):
    """Swap the internet call for one that fails the test if anything calls it."""
    def no_internet(*args, **kwargs):
        raise AssertionError("the fake must not use the internet")

    monkeypatch.setattr(urllib.request, "urlopen", no_internet)

    FakeAdapter().suggest(HOT_FLAT_REQUEST)


def test_the_fake_can_pretend_the_ai_is_down():
    """Lets other features test what staff see when the AI is not available."""
    with pytest.raises(AiUnavailable):
        FakeAdapter(fail=True).suggest(HOT_FLAT_REQUEST)


def test_every_recorded_answer_is_valid_and_uses_allowed_values():
    """A mistake in responses.json is caught here, not in a demo."""
    recorded = json.loads(FIXTURES.read_text(encoding="utf-8"))
    answers = [recorded["default"]]
    for case in recorded["cases"]:
        answers.append(case["response"])

    for answer in answers:
        suggestion = parse_suggestion(answer, source="fake")
        assert suggestion.suggested_category in constants.CATEGORIES
        assert suggestion.suggested_priority in constants.PRIORITIES


def test_the_ai_instructions_list_the_same_values_as_the_app():
    """prompt.py keeps its own copy of these lists, because the AI code must not import the app.
    If someone changes the app's lists, this test fails until prompt.py is updated too."""
    assert CATEGORIES == constants.CATEGORIES
    assert PRIORITIES == constants.PRIORITIES