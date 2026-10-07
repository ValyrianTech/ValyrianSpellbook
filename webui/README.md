# Valyrian Spellbook Web UI

A FastAPI-based admin dashboard for managing the Valyrian Spellbook.

## Tech Stack

- **FastAPI** - Modern async Python web framework
- **Jinja2** - Server-side templating
- **TailwindCSS** - Utility-first CSS framework (standalone CLI, no Node.js required)
- **HTMX** - Client-side interactivity without heavy JavaScript
- **Uvicorn** - ASGI server

## Setup

### 1. Install Python dependencies

Make sure you have the required packages installed:

```bash
pip install fastapi uvicorn jinja2 python-multipart itsdangerous
```

Or add to your existing requirements.txt:
```
fastapi
uvicorn
jinja2
python-multipart
itsdangerous
```

### 2. Run the Web UI

```bash
cd webui
python main.py
```

The web UI will start on port 5001 by default. Access it at: http://localhost:5001

### 3. Session secret (optional)

The session signing secret is stable by default: it is generated once and persisted to `configuration/session_secret.key` (with file permissions `0600`), then reused on subsequent starts, so sessions survive restarts and are shared across worker processes. The file is created atomically (`O_CREAT|O_EXCL`) on first access; if several workers race to create it, the losers re-read the winner's file, so all workers share one key. If the key file already exists but is empty (for example, a previous writer crashed before writing its key), the Web UI now generates and persists a fresh key atomically rather than starting with an empty secret. If a non-empty secret still cannot be obtained, startup fails closed with a `RuntimeError` instead of running with an empty session secret.

To override the key, set the `SPELLBOOK_SESSION_SECRET` environment variable (useful for container or multi-worker deployments, or when the config directory is ephemeral or read-only). Generate one with:

```bash
python -c 'import secrets; print(secrets.token_hex(32))'
```

### 4. Login

Use your Spellbook API key and secret to log in. These are the same credentials used for the CLI and REST API. Credentials are compared with `hmac.compare_digest` on UTF-8-encoded bytes, so key/secret comparison is constant-time and does not leak timing information.

### 5. Session storage, cookies & error handling

Your API credentials are kept **server-side**, not in the cookie. On login, the key and secret are stored in a thread-safe, file-backed session store (`webui/auth.py`) keyed by an opaque `session_id` (generated with `secrets.token_urlsafe(32)`); only that `session_id` is placed in the signed session cookie, so secrets are never written into the cookie (which is signed but not encrypted). Session records are persisted as one JSON file per session id under `configuration/webui_sessions/`, so they are visible across multiple worker processes and survive restarts (they are not process-local). Records expire after 24 hours and are lazily purged on access, and logging out deletes the record.

A request is only treated as authenticated when **both** the signed session cookie carries the `authenticated` flag **and** a matching, non-expired server-side session record exists for the cookie's `session_id`. The session cookie is therefore never trusted on its own: if the cookie flag is set but the store record is missing, expired, deleted, or corrupt (for example after a restart that cleared in-process state, or when a record has been purged), the request is considered unauthenticated, the stale client session is cleared, and the user is redirected back to `/login`. This keeps `is_authenticated` and `get_api_client` in agreement after a restart, so a user can no longer be shown the dashboard while every API call fails for lack of credentials.

The `configuration/webui_sessions/` directory holds API credentials, so its files are created with `0o600` permissions (readable/writable only by the owner). For multi-host deployments, this directory can be placed on a shared filesystem so every Web UI instance shares the same session records.

The session cookie is set with `SameSite=Strict`. To make it HTTPS-only, set the `SPELLBOOK_SESSION_HTTPS_ONLY` environment variable (accepts `1`/`true`/`yes`/`on`, case-insensitive).

Debug mode is opt-in via the `SPELLBOOK_WEBUI_DEBUG` environment variable (accepts `1`/`true`/`yes`/`on`, case-insensitive) and is **off by default** (previously debug mode was always enabled).

Internal server errors render a generic 500 page and are logged server-side; exception details are no longer returned to the browser.

## Development

### Building CSS

The TailwindCSS standalone CLI is included. To rebuild CSS after modifying templates:

```bash
cd webui
./tailwindcss-linux-x64 -i static/css/input.css -o static/css/output.css --minify
```

For development with watch mode:

```bash
./tailwindcss-linux-x64 -i static/css/input.css -o static/css/output.css --watch
```

## Architecture

```
┌─────────────────────┐     ┌─────────────────────┐
│   FastAPI WebUI     │────▶│  Bottle REST API    │
│   (Port 5001)       │     │  (Port 5000)        │
│                     │     │                     │
│  - Admin Dashboard  │     │  - All existing     │
│  - Jinja2 Templates │     │    endpoints        │
│  - TailwindCSS      │     │                     │
└─────────────────────┘     └─────────────────────┘
```

The Web UI communicates with the existing Bottle REST API server. Both can run simultaneously.

## Directory Structure

```
webui/
├── main.py              # FastAPI app entry point
├── config.py            # Configuration settings
├── api_client.py        # Client for Bottle REST API
├── auth.py              # Authentication helpers
├── routers/             # Route handlers
│   ├── dashboard.py
│   ├── triggers.py
│   ├── actions.py
│   ├── llms.py
│   ├── explorers.py
│   └── blockchain.py
├── templates/           # Jinja2 templates
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── triggers/
│   ├── actions/
│   ├── llms/
│   ├── explorers/
│   ├── blockchain/
│   └── errors/
├── static/
│   ├── css/
│   │   ├── input.css    # TailwindCSS input
│   │   └── output.css   # Compiled CSS
│   └── js/
│       └── htmx.min.js
├── tailwind.config.js
└── tailwindcss-linux-x64  # Standalone Tailwind CLI
```
