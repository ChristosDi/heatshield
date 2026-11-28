"""Tests for try_it, the command that shows what the AI suggests for one description.

The tests set AI_MODE themselves and switch off reading .env, so your own .env is never used
and nothing is ever sent to a real AI service.

Run from the api/ folder with: python -m pytest tests/test_ai_adapter_try_it.py
"""
import json
import sys

import pytest

from ai_adapter import try_it

DESCRIPTION = "My flat is too hot and I have nowhere cool to go this afternoon."


@pytest.fixture(autouse=True)
def ignore_your_env_file(monkeypatch):
    """autouse means this runs before every test in this file."""
    monkeypatch.setattr(try_it, "load_dotenv", lambda *args, **kwargs: None)


def run(monkeypatch, *arguments):
    monkeypatch.setattr(sys, "argv", ["try_it", *arguments])
    return try_it.main()


def test_it_prints_the_suggestion_as_json(monkeypatch, capsys):
    monkeypatch.setenv("AI_MODE", "fake")

    exit_code = run(monkeypatch, DESCRIPTION)

    printed = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert printed["suggested_category"] == "cooling_space"
    assert printed["source"] == "fake"


def test_it_explains_how_to_use_it_when_no_description_is_given(monkeypatch, capsys):
    exit_code = run(monkeypatch)

    assert exit_code == 1
    assert "Usage" in capsys.readouterr().out


def test_a_setting_problem_is_explained_not_crashed(monkeypatch, capsys):
    monkeypatch.setenv("AI_MODE", "maybe")

    exit_code = run(monkeypatch, DESCRIPTION)

    assert exit_code == 1
    assert "AI_MODE" in capsys.readouterr().out