# macOS Port of ollama_captioner

## Summary

Minimal port of [eddcgpro/ollama_captioner](https://github.com/eddcgpro/ollama_captioner) to run on macOS. The original is a Flask web app that uses local Ollama vision models to generate image captions via a browser UI. The Python backend and HTML frontend are already cross-platform — only the Windows batch launcher needs replacing. Additionally, we migrate from Flask to FastAPI + Uvicorn for consistency with other local projects and better async support.

## Source Repository

- **Upstream:** https://github.com/eddcgpro/ollama_captioner
- **Files:** `app.py` (Flask backend, 3 routes), `templates/index.html` (frontend, 1349 lines), `setup_and_run.bat` (Windows launcher), `assets/screenshot.png`, `.gitignore`, `README.md`

## Changes

### 1. Delete `setup_and_run.bat`

Windows-only launcher. Not needed in the macOS fork.

### 2. Rewrite `app.py` (Flask → FastAPI + Uvicorn)

Migrate the 3 routes from Flask to FastAPI:

| Flask (original) | FastAPI (new) |
|---|---|
| `@app.route('/')` | `@app.get('/')` returning `HTMLResponse` or `Jinja2Templates` |
| `@app.route('/api/models', methods=['GET'])` | `@app.get('/api/models')` |
| `@app.route('/api/caption', methods=['POST'])` | `@app.post('/api/caption')` with `UploadFile` |
| `request.form.get(...)` | FastAPI `Form(...)` parameters |
| `request.files['file']` | FastAPI `UploadFile` parameter |
| `jsonify(...)` | Direct dict return (auto-serialized) |
| `app.run(debug=True, port=5000)` | `uvicorn.run(app, port=5000)` |

The `templates/index.html` stays as-is — FastAPI supports Jinja2 templates with `Jinja2Templates` from `starlette`.

### 3. Add `setup_and_run.sh`

Bash script that:
- Checks for `python3` availability
- Creates a virtual environment (`venv/`) if not present
- Installs dependencies from `requirements.txt`
- Starts the Uvicorn server on `localhost:5000`
- Opens the default browser via `open http://localhost:5000`
- Traps SIGINT for clean shutdown

### 4. Add `requirements.txt`

```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
jinja2
python-multipart
ollama
```

- `fastapi` + `uvicorn`: web framework and ASGI server
- `jinja2`: template rendering (for `index.html`)
- `python-multipart`: required for `UploadFile` / form data parsing in FastAPI
- `ollama`: Ollama Python client

Dropped from original: `flask`, `torch`, `torchvision`, `transformers`, `Pillow`, `requests` — none used in the current code. Pending grep verification after cloning.

### 5. Update `README.md`

Replace Windows instructions with macOS equivalents:
- Prerequisites: Ollama installed (brew or ollama.com), a vision model pulled
- Launch: `chmod +x setup_and_run.sh && ./setup_and_run.sh`
- Manual alternative: create venv, pip install, `uvicorn app:app --port 5000`

### 6. No changes

- `templates/index.html` — browser-based, no OS specifics (endpoints stay the same)
- `.gitignore` — already covers `venv/`

## Prerequisites (for end user)

1. macOS with Python 3.8+
2. Ollama installed and running (`brew install ollama` or download from ollama.com)
3. At least one vision-capable model pulled (e.g., `ollama pull gemma3:latest`)

## Verification Plan

1. Clone upstream repo
2. `grep -r "torch\|torchvision\|transformers\|Pillow" --include="*.py" --include="*.html"` — confirm no usage
3. Rewrite `app.py` to FastAPI, replace `.bat` with `.sh`, add `requirements.txt`
4. Run `setup_and_run.sh`, verify server starts and UI loads
5. Upload an image, confirm captioning works with a local Ollama model
6. Test all 3 API endpoints (`/`, `/api/models`, `/api/caption`)
