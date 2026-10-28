# ECHOME

**Your Voice. Your Mind. Your Digital Self.**

A local-first personal AI clone. Milestone 1: a working text chat assistant
connected to a local Ollama model. Everything runs on your laptop — no paid
APIs, no cloud, no GPU required.

## Current status (Milestone 1)

- FastAPI backend (`ECHOME/app/main.py`) connected to Ollama (`llama3.2:3b`)
- Chat web interface served by FastAPI at `http://127.0.0.1:7860`
  — this is a **custom inline-HTML/JS (Bootstrap) page, not Gradio**.
  Gradio was evaluated for Milestone 1 but is not used or imported by the code.
- Endpoints:
  - `GET  /healthz` — health + Ollama status
  - `POST /api/generate` — text generation, accepts
    `{ "prompt": "...", "model": "...", "system_prompt": "...", "conversation_history": [...] }`
  - `GET  /` — chat interface
- Interactive API docs at `/api/docs`

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) running locally (`ollama serve`) with a model, e.g.
  `ollama pull llama3.2:3b`
- Python packages: `fastapi`, `uvicorn`, `requests`, `python-dotenv` (already the
  environment default; install with `pip install fastapi uvicorn requests python-dotenv`)

## Run

```bash
cd ECHOME
python3 run.py
```

No `PYTHONPATH` needed — `run.py` adds the project root to `sys.path` itself.
The server binds to `127.0.0.1:7860` (private to your machine).

Optionally run the smoke test (requires Ollama running):

```bash
python3 test_app.py
```

## Configuration (environment variables)

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Ollama endpoint |
| `DEFAULT_MODEL` | `llama3.2:3b` | Model name |
| `ECHOME_HOST` / `ECHOME_PORT` | `127.0.0.1` / `7860` | Server binding |
| `ECHOME_DB_PATH` | `~/.echome/memory.db` | Future memory database |
| `ECHOME_MEMORY` | `true` | Future memory toggle |

## Privacy

- Server binds to `127.0.0.1` only; not exposed to the network.
- No telemetry, no external API calls other than local Ollama.
- `data/`, `recordings/`, `*.db`, model weights, and `.env` are git-ignored.

## Roadmap

- Milestone 2 — voice input (speech recognition for Kannada, Hindi, English)
- Milestone 3 — spoken responses (local TTS)
- Milestone 4 — SQLite personal memory with user approval
- Milestone 5 — optional consent-based voice cloning evaluation
