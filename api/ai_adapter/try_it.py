"""Show what the AI suggests for one description, with no Flask, Django or database.

Run from the api/ folder:
    python -m ai_adapter.try_it "My flat is too hot and I have nowhere cool to go this afternoon."

It follows AI_MODE in .env, so the same command shows the fake answer or the real one.
Only use fictional descriptions: in "real" mode the text is sent to the AI service.
"""
import json
import sys
from dataclasses import asdict
from pathlib import Path

from dotenv import load_dotenv

from . import AiConfigError, AiUnavailable, get_adapter

# .env sits in the project folder, two folders above this file.
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


def main():
    if len(sys.argv) != 2:
        print('Usage: python -m ai_adapter.try_it "a fictional request description"')
        return 1

    load_dotenv(ENV_FILE)
    try:
        suggestion = get_adapter().suggest(sys.argv[1])
    except (AiConfigError, AiUnavailable) as error:
        print(f"No suggestion: {error}")
        return 1

    print(json.dumps(asdict(suggestion), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())