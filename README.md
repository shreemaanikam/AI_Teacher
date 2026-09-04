# AI Teacher

The repository contains the first implementation slice of the planned local-first AI teacher.

## Run locally

Requirements: Python 3.12+ and Node 22+.

```powershell
Copy-Item .env.example .env

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
