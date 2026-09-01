# AI Teacher

The repository now contains the first implementation slice: an optional Agora-powered live classroom around the planned local-first AI teacher.

## Run locally

Requirements: Python 3.12+, Node 22+, and an Agora Video Calling/RTC project.

```powershell
Copy-Item .env.example .env
# Fill AGORA_APP_ID and, when required, AGORA_TEMP_TOKEN in .env.

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
$env:FLASK_APP = "app:create_app"
flask run
```

In another terminal:

```powershell
Set-Location frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api` to Flask on port 5000.

The temporary-token provider is for development only. See [the Agora integration notes](docs/technical/agora_integration.md) before deploying.
