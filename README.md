# AgriGuard AI

AgriGuard AI is a responsive multi-agent farmer advisor supporting SDG 2, 12, 13, and 15. It routes requests to weather, crop-health, market, and sustainability specialists, then creates a clear farm action brief.

## What changed

- Replaced the slow Granite 3.1 8B path with an optional local **Llama 3.2 3B** Ollama model. It is free, runs on the user's computer, and needs no API key.
- Agent routing and report synthesis are now deterministic and fast. The application keeps working when Ollama is not running, instead of making every chat wait for two model calls.
- Reports now preserve their all-agent selection, so Weather, Crop Doctor, Market, and Sustainability always run.
- Farm profiles validate required inputs and update an existing user/location/crop profile instead of creating duplicates.
- Chat and reports use the farm profile saved in the browser; there are no hard-coded profile IDs or duplicate optimistic messages.
- Open-Meteo weather and geocoding are free and keyless. A town/city or latitude/longitude can be used for location.

## Stack

- Frontend: Next.js 16, TypeScript, Tailwind CSS, React Query, Framer Motion, shadcn-style UI
- Backend: FastAPI, SQLite, SQLAlchemy, LangGraph, ChromaDB
- Free services: Open-Meteo weather/geocoding; local agricultural text knowledge base
- Optional local AI: Ollama + `llama3.2:3b`

## Run on Windows

Install [Python 3.11+](https://www.python.org/downloads/), [Node.js LTS](https://nodejs.org/), and optionally [Ollama](https://ollama.com/download). In PowerShell:

```powershell
cd C:\Users\Kenzo68\Desktop\agriguard-ai
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r .\backend\requirements.txt
cd .\frontend
npm install
```

Optional, for the local Llama model:

```powershell
ollama pull llama3.2:3b
```

Start the backend in one terminal:

```powershell
cd C:\Users\Kenzo68\Desktop\agriguard-ai\backend
..\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Start the frontend in another terminal:

```powershell
cd C:\Users\Kenzo68\Desktop\agriguard-ai\frontend
npm run dev
```

Open `http://localhost:3000`, create a farm profile, then use Chat or Farm Report. API documentation is at `http://localhost:8000/docs`.

## Verification

```powershell
cd C:\Users\Kenzo68\Desktop\agriguard-ai\frontend
npm run lint
npm run build
```

For backend checks, activate the project virtual environment and run `python -m compileall -q app` from `backend`.
