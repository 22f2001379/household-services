# Household Services

Household Services is a two-tier web application for managing household service bookings. Customers can register, browse approved professionals, request services, close completed requests, and leave reviews. Administrators can manage services and approve or block service professionals. Professionals can accept or reject assigned work.

## Features

- Customer and professional registration
- Token-based login with role-aware routing
- Admin service catalog management
- Professional approval workflow
- Customer service request creation and closure
- Professional request acceptance/rejection
- Customer reviews and professional rating summaries
- Flask API with Vue 2 frontend
- Backend tests for authentication, authorization, service requests, and reviews

## Tech Stack

- Backend: Python, Flask, Flask-SQLAlchemy, Flask-Security, Flask-RESTful, Flask-Mail, Celery
- Frontend: Vue 2, Vue Router, Vuex, Vite, Bootstrap, Axios
- Database: SQLite for local development; any SQLAlchemy-compatible database can be used through `DATABASE_URL`
- Optional services: Redis for Celery broker/result backend, SMTP for email reminders

## Architecture Overview

The repository is split into two applications:

- `backend/` contains the Flask API, SQLAlchemy models, configuration, and tests.
- `frontend/` contains the Vue 2 single-page application.

The backend exposes JSON endpoints under `/api/*`. Authentication uses Flask-Security token auth with the `Authentication-Token` header. The frontend stores the returned auth token in `localStorage` and sends it on API requests.

## Project Structure

```text
.
├── AUDIT.md                    # Production-readiness audit and remediation notes
├── backend/
│   ├── app.py                  # Flask app factory, extension setup, seed logic
│   ├── requirements.txt        # Python dependencies
│   ├── application/
│   │   ├── config.py           # Environment-driven settings
│   │   ├── database.py         # SQLAlchemy extension
│   │   ├── models.py           # Database models
│   │   ├── resources.py        # Flask-RESTful API extension
│   │   └── routes.py           # JSON API routes
│   └── tests/
│       └── test_api.py         # Backend API tests
└── frontend/
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── components/         # Vue dashboard and form components
        ├── services/api.js     # Axios API client
        ├── utils/              # Browser storage helpers
        ├── App.vue
        └── main.js             # Router and Vuex setup
```

## Environment Variables

Copy `.env.example` to `.env` for local development and change secrets before running outside a disposable environment.

| Variable | Required | Description |
| --- | --- | --- |
| `SECRET_KEY` | Yes | Flask signing secret. Use a long random value in production. |
| `SECURITY_PASSWORD_SALT` | Yes | Flask-Security password/token salt. Use a long random value in production. |
| `DATABASE_URL` | No | SQLAlchemy database URL. Defaults to local SQLite. |
| `CORS_ORIGINS` | No | Comma-separated allowed frontend origins. |
| `ADMIN_EMAIL` | No | If set with `ADMIN_PASSWORD`, seeds an admin user on startup. |
| `ADMIN_PASSWORD` | No | Development/admin seed password. Use a strong value and rotate after first login. |
| `CELERY_BROKER_URL` | No | Redis broker URL for Celery tasks. |
| `CELERY_RESULT_BACKEND` | No | Redis result backend URL. |
| `MAIL_SERVER` | No | SMTP host for reminders. |
| `MAIL_PORT` | No | SMTP port. Defaults to `587`. |
| `MAIL_USE_TLS` | No | Whether SMTP uses TLS. Defaults to `true`. |
| `MAIL_USERNAME` | No | SMTP username. |
| `MAIL_PASSWORD` | No | SMTP password or app password. |
| `VITE_API_BASE_URL` | No | Frontend API base URL. Defaults to `http://127.0.0.1:5001`. |

## Installation

Prerequisites:

- Python 3.11 or newer
- Node.js 18 or newer
- npm
- Redis, only if running Celery tasks locally

Backend setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
cp .env.example .env
```

Frontend setup:

```bash
cd frontend
npm ci
```

## Database Setup

The app creates database tables on startup using SQLAlchemy metadata. For local development, the default database is:

```text
backend/instance/homeservices.sqlite3
```

To use another database, set `DATABASE_URL`, for example:

```bash
export DATABASE_URL=postgresql+psycopg://user:password@host:5432/household_services
```

If `ADMIN_EMAIL` and `ADMIN_PASSWORD` are set, the app seeds an admin user when one does not already exist.

## Running Locally

Start the backend:

```bash
source .venv/bin/activate
python backend/app.py
```

Start the frontend in another terminal:

```bash
cd frontend
npm run serve
```

Open the Vite URL shown in the terminal, usually `http://localhost:3000` or `http://localhost:5173`.

## Development Mode

Use these settings for local development:

```bash
export FLASK_DEBUG=true
export SECRET_KEY=dev-secret-change-me
export SECURITY_PASSWORD_SALT=dev-salt-change-me
export ADMIN_EMAIL=admin@example.com
export ADMIN_PASSWORD=change-this-password
```

Then run the backend and frontend commands above.

## Production Mode

For production:

1. Set `FLASK_DEBUG=false`.
2. Use strong, unique `SECRET_KEY` and `SECURITY_PASSWORD_SALT` values.
3. Use a managed production database through `DATABASE_URL`.
4. Restrict `CORS_ORIGINS` to the deployed frontend origin.
5. Serve Flask behind a WSGI server such as Gunicorn or uWSGI.
6. Build the frontend with `npm run build` and serve `frontend/dist/` from a static host or reverse proxy.
7. Configure SMTP and Redis only if reminder jobs are enabled.
8. Rotate or remove any seeded admin password after deployment.

Example backend command:

```bash
gunicorn "backend.app:create_app()" --bind 0.0.0.0:5001
```

## Testing

Run backend tests:

```bash
source .venv/bin/activate
python -m pytest backend/tests
```

Run a production frontend build:

```bash
cd frontend
npm run build
```

Dependency audit:

```bash
cd frontend
npm audit --audit-level=high
```

Known audit status: non-breaking npm audit fixes have been applied. Remaining findings are tied to the Vue 2/Vite 2 toolchain and require a breaking Vue 3/Vite migration.

## Build Instructions

Backend syntax check:

```bash
python -m compileall backend
```

Frontend build:

```bash
cd frontend
npm run build
```

The frontend output is written to `frontend/dist/`.

## Deployment Instructions

One practical deployment shape:

1. Deploy the Flask backend to a Python host using Gunicorn.
2. Set all required environment variables in the host secret manager.
3. Point `DATABASE_URL` at a production database.
4. Build the frontend with `VITE_API_BASE_URL` set to the backend URL.
5. Serve `frontend/dist/` with Nginx, a static hosting service, or the same platform that hosts the API.
6. Configure HTTPS and restrict CORS to the frontend origin.
7. Run backend tests and frontend build in CI before deployment.

## Troubleshooting

- `401 Unauthorized` from API calls: confirm the frontend has a token in `localStorage.auth_token` and sends `Authentication-Token`.
- Admin login does not work: set `ADMIN_EMAIL` and `ADMIN_PASSWORD`, delete the local SQLite database if needed, then restart the backend so the seed can run.
- SQLite cannot open database: ensure `backend/instance/` is writable or set `DATABASE_URL` to another location.
- CORS errors: add the frontend origin to `CORS_ORIGINS`.
- Frontend cannot reach backend: set `VITE_API_BASE_URL` and rebuild/restart the frontend.
- `npm audit` reports Vue/Vite issues: plan the Vue 3 migration; do not use `npm audit fix --force` without testing the migration.

## Future Improvements

- Migrate from Vue 2 to Vue 3 and current Vite tooling.
- Add database migrations with Flask-Migrate/Alembic.
- Replace duplicate `role_id` state with role relationships only.
- Add frontend component tests and end-to-end tests for core user flows.
- Add CI for backend tests, frontend build, and dependency audits.
- Improve dashboard empty/loading/error states and modal focus handling.
- Add pagination/filtering for larger user, service, and request datasets.
