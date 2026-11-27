"""The real AI: any chat-completions service in the OpenAI format. The team uses the Gemini API free tier.

The API key is kept in this object only. It is never put in an error message or a log.
"""
from .base import AiConfigError, AiUnavailable


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
        # The call to the service is the next step. Until then staff carry on by hand, as for any AI failure.
        raise AiUnavailable("The call to the real AI is not built yet")