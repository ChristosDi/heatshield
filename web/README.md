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

The dashboard gets its numbers from the Flask API, so run both servers, each in its own terminal with the virtual environment active.

1. The Flask API, from `api/`:
   ```
   flask --app run run --port 5000 --debug
   ```
   If port 5000 is taken on your machine, use another port, for example `--port 5001`, and set `FLASK_API_URL=http://127.0.0.1:5001` in your `.env`.
2. Django, from `web/`:
   ```
   python manage.py runserver
   ```

Open http://127.0.0.1:8000/ and sign in. Manage staff accounts and roles at http://127.0.0.1:8000/admin/. If the Flask API isn't running, the home page still loads and says the counts can't be loaded.

Django calls Flask only through `dashboard/api_client.py`, from the server. The browser never calls Flask directly.

## Staff roles

There are three roles, each a Django group created by a migration: `support_worker`, `coordinator` and `admin`. To give someone a role, open their user in the admin site and add them to the group.

## Tests

From `web/`:
```
python -m pytest
```
The tests use their own settings (`config/test_settings.py`), so they need no `.env`.They never call the real Flask API: `conftest.py` gives every test a fake one. Each app keeps its tests in its own `tests/` folder, next to the code they check, for example `staff/tests/test_sign_in.py`. Test files must be named `test_*.py`.

## Where code goes

| Folder | What goes there |
|---|---|
| `config/` | Settings, test settings and the main URL list |
| `staff/` | Sign-in and staff roles, with their tests in `staff/tests/` |
| `dashboard/` | Dashboard pages, with their templates in `dashboard/templates/dashboard/` and their tests in `dashboard/tests/` |
| `templates/` | Shared templates: `base.html` and the sign-in page (`registration/login.html`) |