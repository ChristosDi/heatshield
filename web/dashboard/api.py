from django.conf import settings
import requests

BASE = settings.FLASK_API_URL.rstrip("/")


def get(path: str, **kwargs):
    return requests.get(f"{BASE}{path}", timeout=5, **kwargs)


def post(path: str, **kwargs):
    return requests.post(f"{BASE}{path}", timeout=5, **kwargs)