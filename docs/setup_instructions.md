# Setup instructions

## Prerequisites

- Windows, macOS or Linux with Python 3.11+.
- Node.js/npm compatible with the committed `frontend/package-lock.json`.
- Blender 5.x only for Blender render regeneration; the API and analysis pipeline can run without it.

## Python environment

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` only if local overrides are needed; never commit secrets. The default SQLite path is `data/q3.sqlite3`. `BLENDER_EXECUTABLE` may identify the installed Blender binary.

## Frontend dependencies

```powershell
cd frontend
npm ci
```

The checked-in GLB is under `frontend/public/assets/supermarket/`; no external 3D asset download is required.
