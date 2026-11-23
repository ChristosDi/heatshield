"""Settings for the automated tests: no .env needed."""
import os

# A throwaway key for tests only. Real keys live in .env, never in Git.
os.environ.setdefault("DJANGO_SECRET_KEY", "tests-only-not-a-real-secret")

from config.settings import *  # noqa: E402,F403

# Fast password hashing keeps the sign-in tests quick.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]