"""The real AI: any chat-completions service in the OpenAI format. The team uses the Gemini API free tier.

The API key is kept in this object only. It is never put in an error message or a log.
"""
import json
import urllib.error
import urllib.request

from .base import AiConfigError, AiUnavailable, parse_suggestion
from .prompt import RESPONSE_SCHEMA, SYSTEM_PROMPT

# Seconds to wait for an answer. If the AI is slower, staff carry on by hand.
TIME_LIMIT = 10


class RealAdapter:
    """Sends a request description to the real AI service and checks its answer."""

    def __init__(self, base_url, model, api_key):
        # Plain http:// would send the API key unencrypted.
        if not base_url.startswith("https://"):
            raise AiConfigError("AI_BASE_URL must start with https://")

        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key

    def suggest(self, description):
        """Ask the AI for a suggestion. Any problem becomes AiUnavailable, so staff can carry on by hand."""
        reply = self.send(description)
        answer = read_answer(reply)
        return parse_suggestion(answer, source="real")

    def send(self, description):
        """Send the instructions and the description to the service and return its reply."""
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": description},
            ],
            "response_format": {"type": "json_schema", "json_schema": RESPONSE_SCHEMA},
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=TIME_LIMIT) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as error:
            raise AiUnavailable(f"The AI service answered with HTTP {error.code}") from error
        except TimeoutError as error:
            raise AiUnavailable(f"The AI service took longer than {TIME_LIMIT} seconds") from error
        except OSError as error:
            raise AiUnavailable("The AI service could not be reached") from error
        except ValueError as error:
            raise AiUnavailable("The AI service did not reply with JSON") from error


def read_answer(reply):
    """Take the AI's answer out of the service's reply. The answer is JSON text in choices[0].message.content."""
    try:
        content = reply["choices"][0]["message"]["content"]
        return json.loads(content)
    except (KeyError, IndexError, TypeError, ValueError) as error:
        raise AiUnavailable("The AI answer was not in the expected format") from error