# Django UI

The staff website: pages, forms and staff sign-in. Django calls the Flask API from the server, and the browser never calls Flask directly. Django's own database holds only staff logins and sessions; HeatShield's data lives in the Flask API.

## First-time setup

Already have the repository? After pulling these changes, run steps 1-3.

From the repository root, with the virtual environment active (on macOS or Linux, use `python3` if `python` is not found):

1. Install the requirements. Flask and Django share one file.
   ```
   pip install -r requirements.txt
   ```
2. Create your own `.env` with a new secret key. Never commit `.env` or share its key; `.env.example` lists every setting.
   ```
   python -c "from django.core.management.utils import get_random_secret_key as k; open('.env','w').write(f'DJANGO_SECRET_KEY={k()}\nDJANGO_DEBUG=True\n')"
   ```
3. Create Django's database (staff logins, sessions and the three staff roles), then a staff account for yourself:
   ```
   cd web
   python manage.py migrate
   python manage.py createsuperuser
   ```

## Run

From `web/`:
```
python manage.py runserver
```
Open http://127.0.0.1:8000/ and sign in. Manage staff accounts and roles at http://127.0.0.1:8000/admin/.

## Staff roles

There are three roles, each a Django group created by a migration: `support_worker`, `coordinator` and `admin`. To give someone a role, open their user in the admin site and add them to the group.

## Tests

From `web/`:
```
python -m pytest
```
The tests use their own settings (`config/test_settings.py`), so they need no `.env`.

## Where code goes

| Folder | What goes there |
|---|---|
| `config/` | Settings and the main URL list |
| `staff/` | Sign-in and staff roles |
| `dashboard/` | Dashboard pages |
| `templates/` | Shared templates: `base.html` and the sign-in page |
| `tests/` | Tests for the Django UI |