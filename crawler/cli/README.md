# RegulaAI CLI

A command-line tool for GDPR compliance scanning, rule management, and badge generation.

## < 5 min Quick Start

### 1. Start the stack with Docker Compose

```bash
git clone https://github.com/regulaai/regulaai.git
cd regulaai
cp .env.example .env  # if needed
docker compose up -d
```

- This will start the API, database, and dashboard (default: http://localhost:8000, dashboard: http://localhost:3000)

### 2. Create your first API token

```bash
# Register a user (via API or dashboard)
curl -X POST http://localhost:8000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email": "you@example.com", "password": "yourpass", "first_name": "You", "last_name": "User", "organisation_name": "YourOrg"}'

# Login to get a token
curl -X POST http://localhost:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email": "you@example.com", "password": "yourpass"}'

# Or create an API key via dashboard or API
```

### 3. Install the CLI and configure authentication

```bash
pip install --upgrade regulaai-cli
regulaai auth --api-key YOUR_API_KEY
```

### 4. Run your first scan

```bash
regulaai scan https://example.com
```

- See compliance score, violations, and cookies in the terminal.

### 5. View results in the dashboard

- Open [http://localhost:3000](http://localhost:3000) in your browser
- Log in with your credentials
- View scan history, compliance scores, and more

---

## CLI Commands

- `scan <url>`: Scan a website for GDPR compliance
- `rules list`: List available rule packs
- `rules add <file>`: Add a new rule pack
- `badge <site_id>`: Generate a compliance badge
- `auth --api-key <key>`: Configure authentication
- `status`: Show CLI status
- `version`: Show CLI version

See `regulaai --help` for all options. 