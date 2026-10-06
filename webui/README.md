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

The session signing secret is stable by default: it is generated once and persisted to `configuration/session_secret.key` (with file permissions `0600`), then reused on subsequent starts, so sessions survive restarts and are shared across worker processes.

To override the key, set the `SPELLBOOK_SESSION_SECRET` environment variable (useful for container or multi-worker deployments, or when the config directory is ephemeral or read-only). Generate one with:

```bash
python -c 'import secrets; print(secrets.token_hex(32))'
```

### 4. Login

Use your Spellbook API key and secret to log in. These are the same credentials used for the CLI and REST API.

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
