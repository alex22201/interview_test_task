# Redirect Rule Service

A small Django/DRF service for managing short-link redirect rules with public and private
access levels.

## Stack

- Django 6 (`>=5` required by the spec) + Django REST Framework
- PostgreSQL
- JWT authentication (`djangorestframework-simplejwt`)
- WhiteNoise for serving admin and Swagger UI static files under gunicorn
- OpenAPI 3 schema and Swagger UI (`drf-spectacular`)
- [`uv`](https://docs.astral.sh/uv/) as the package manager
- Docker Compose for local orchestration
- pytest / pytest-django for tests
- `ruff` + `pre-commit` for linting and formatting
- GitHub Actions CI (lint, schema validation, tests)

## Project layout

```
.
├── pyproject.toml / uv.lock   # dependencies (managed by uv)
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .github/workflows/ci.yml
└── src/
    ├── manage.py
    ├── config/                # Django project (settings, root urls)
    └── redirects/              # RedirectRule model, API, redirect views, tests
```

## Running with Docker Compose

```bash
docker compose up --build
```

This starts a `db` (PostgreSQL) and a `web` (Django, via gunicorn) service. Migrations run
automatically on `web` startup, and admin static files are collected at image build time and
served by WhiteNoise.

No `.env` file is required — Compose falls back to development defaults. Copy
`cp .env.example .env` to override them. Note that `DJANGO_SECRET_KEY` has a fallback only
while `DJANGO_DEBUG=True`; with `DJANGO_DEBUG=False` the app refuses to start without a real
key rather than running on a publicly known one.

Create an admin user (users are provisioned via the admin panel only, no self-registration):

```bash
docker compose exec web python manage.py createsuperuser
```

Log into `http://localhost:8000/admin/` with that account to create additional users, or
manage them via `manage.py`.

## Running locally without Docker

```bash
uv sync
cp .env.example .env   # then point DATABASE_URL at a Postgres instance you have running
uv run --directory src python manage.py migrate
uv run --directory src python manage.py createsuperuser
uv run --directory src python manage.py runserver
```

## API

### Interactive docs

Swagger UI is available at `http://localhost:8000/api/docs/` and needs no authentication.
To try the authenticated endpoints from it, get a token from `/retrieve-token/`, click
**Authorize** and paste the `access` value.

### Obtain a JWT

```bash
curl --request POST \
  --url http://localhost:8000/retrieve-token/ \
  --header 'Content-Type: application/json' \
  --data '{"username": "username", "password": "password"}'
```

Returns `{"access": "...", "refresh": "..."}`. Use the access token as
`Authorization: Bearer <access>` on the endpoints below.

Exchange a refresh token for a fresh access token:

```bash
curl --request POST \
  --url http://localhost:8000/refresh-token/ \
  --header 'Content-Type: application/json' \
  --data '{"refresh": "<refresh>"}'
```

### Manage redirect rules (`/url/`)

Authenticated users can only see/edit/delete rules they created.

```bash
# Create
curl --request POST \
  --url http://localhost:8000/url/ \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{"redirect_url": "https://google.com", "is_private": false}'

# List own rules
curl --url http://localhost:8000/url/ --header 'Authorization: Bearer <token>'

# Update
curl --request PATCH \
  --url http://localhost:8000/url/<id>/ \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{"is_private": true}'

# Delete
curl --request DELETE \
  --url http://localhost:8000/url/<id>/ \
  --header 'Authorization: Bearer <token>'
```

`id`, `created`, `modified` and `redirect_identifier` are server-generated and read-only.
Endpoints use DRF's default routing, so the trailing slash is required: `/url/<id>/`.

Ownership is enforced by scoping the queryset to the caller, so another user's rule answers
`404` rather than `403` — it is not disclosed that the rule exists at all.

### Follow a redirect

```bash
# Public — no auth required
curl -I http://localhost:8000/redirect/public/<redirect_identifier>

# Private — requires a valid JWT
curl -I http://localhost:8000/redirect/private/<redirect_identifier> \
  --header 'Authorization: Bearer <token>'
```

Both return `302 Found` with a `Location` header pointing at `redirect_url`.

A private rule is reachable by *any* authenticated user, not only its owner: the assignment
ties privacy to "the user must be authenticated", while the owner-only restriction is stated
for editing and deleting. Restricting private links to their owner would make them
unshareable, which defeats the purpose of a short link.

## Tests

```bash
uv run pytest
```

CI runs the same suite against a real PostgreSQL service container on every push/PR, plus the
pre-commit hooks and an OpenAPI schema generation that fails on warnings — see
`.github/workflows/ci.yml`.

## Linting

Hooks are defined in `.pre-commit-config.yaml`: `ruff check --fix`, `ruff format`, a
`uv lock` consistency check, and the usual file hygiene (trailing whitespace, final newline,
YAML/TOML syntax, stray `breakpoint()` calls). Enable them once per clone:

```bash
uv run pre-commit install
```

They then run on every `git commit`. To check the whole tree at any time — which is exactly
what CI does:

```bash
uv run pre-commit run --all-files
```

The `ruff` revision pinned in the hook config matches the one in the dev dependency group, so
the hook and a local `uv run ruff` cannot disagree.
