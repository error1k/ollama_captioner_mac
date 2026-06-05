# macOS Port Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port ollama_captioner from Windows/Flask to macOS/FastAPI so it runs locally with a single shell command.

**Architecture:** Clone the upstream repo, rewrite `app.py` from Flask to FastAPI (same 3 endpoints, same JSON contracts), replace the Windows `.bat` launcher with a macOS `.sh` script, and trim dependencies to only what's actually used.

**Tech Stack:** Python 3.8+, FastAPI, Uvicorn, Jinja2, python-multipart, ollama Python client

---

## File Structure

```
ollama_captioner_mac/
├── app.py                  # FastAPI backend (rewritten from Flask)
├── requirements.txt        # Trimmed dependencies
├── setup_and_run.sh        # macOS launcher script
├── templates/
│   └── index.html          # Frontend (unchanged from upstream)
├── assets/
│   └── screenshot.png      # UI screenshot (unchanged from upstream)
├── .gitignore              # (unchanged from upstream)
├── README.md               # Updated for macOS + FastAPI
├── tests/
│   └── test_app.py         # API endpoint tests
└── docs/
    └── superpowers/
        ├── specs/
        │   └── 2026-06-05-macos-port-design.md
        └── plans/
            └── 2026-06-05-macos-port.md
```

---

### Task 1: Clone Upstream and Verify Unused Dependencies

**Files:**
- No file changes — exploratory task

- [ ] **Step 1: Fork and clone the upstream repo**

```bash
gh repo fork eddcgpro/ollama_captioner --clone=false
git clone https://github.com/erikhansen/ollama_captioner.git /Users/erikhansen/tools/ollama_captioner_mac_upstream
```

Note: We're cloning into a temporary location. We'll copy files into our working directory.

- [ ] **Step 2: Verify unused dependencies**

```bash
cd /Users/erikhansen/tools/ollama_captioner_mac_upstream
grep -r "torch\|torchvision\|transformers\|Pillow\|PIL" --include="*.py" --include="*.html"
```

Expected: No matches (confirming these are dead dependencies).

Also verify `requests` is unused at runtime:

```bash
grep -n "requests" app.py
```

Expected: Only the `import requests` line — never called.

- [ ] **Step 3: Copy upstream files to working directory**

```bash
cp /Users/erikhansen/tools/ollama_captioner_mac_upstream/templates/index.html /Users/erikhansen/tools/ollama_captioner_mac/templates/index.html
cp /Users/erikhansen/tools/ollama_captioner_mac_upstream/assets/screenshot.png /Users/erikhansen/tools/ollama_captioner_mac/assets/screenshot.png
cp /Users/erikhansen/tools/ollama_captioner_mac_upstream/.gitignore /Users/erikhansen/tools/ollama_captioner_mac/.gitignore
```

Create necessary directories first:

```bash
mkdir -p /Users/erikhansen/tools/ollama_captioner_mac/templates
mkdir -p /Users/erikhansen/tools/ollama_captioner_mac/assets
```

- [ ] **Step 4: Initialize git repo and commit upstream files**

```bash
cd /Users/erikhansen/tools/ollama_captioner_mac
git init
git add templates/index.html assets/screenshot.png .gitignore
git commit -m "feat: add upstream frontend and assets from eddcgpro/ollama_captioner"
```

---

### Task 2: Create `requirements.txt`

**Files:**
- Create: `requirements.txt`

- [ ] **Step 1: Create requirements.txt**

```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
jinja2
python-multipart
ollama
```

- [ ] **Step 2: Commit**

```bash
git add requirements.txt
git commit -m "feat: add requirements.txt with FastAPI stack and ollama client"
```

---

### Task 3: Write Failing Tests for API Endpoints

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_app.py`

- [ ] **Step 1: Add test dependencies to requirements**

Add `httpx` and `pytest` to a dev section or install them separately. For simplicity, add a `requirements-dev.txt`:

```
pytest
httpx
```

- [ ] **Step 2: Write the test file**

```python
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock
from app import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.anyio
async def test_index_returns_html(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.anyio
async def test_list_models_online(client):
    mock_model = MagicMock()
    mock_model.model = "gemma3:latest"
    mock_response = MagicMock()
    mock_response.models = [mock_model]

    with patch("app.ollama.list", return_value=mock_response):
        response = await client.get("/api/models")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "gemma3:latest" in data["models"]


@pytest.mark.anyio
async def test_list_models_offline(client):
    with patch("app.ollama.list", side_effect=Exception("Connection refused")):
        response = await client.get("/api/models")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "offline"
        assert data["models"] == []


@pytest.mark.anyio
async def test_caption_missing_model(client):
    response = await client.post("/api/caption", data={}, files={})
    assert response.status_code == 400


@pytest.mark.anyio
async def test_caption_missing_file(client):
    response = await client.post(
        "/api/caption",
        data={"model_name": "gemma3:latest", "prompt": "Describe this"},
    )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_caption_success(client):
    with patch("app.call_ollama_api", return_value="A photo of a cat"):
        fake_image = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        response = await client.post(
            "/api/caption",
            data={"model_name": "gemma3:latest", "prompt": "Describe this"},
            files={"file": ("test.png", fake_image, "image/png")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["caption"] == "A photo of a cat"
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd /Users/erikhansen/tools/ollama_captioner_mac
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/test_app.py -v
```

Expected: FAIL — `app` module does not exist yet (or has no FastAPI app).

- [ ] **Step 4: Commit test files**

```bash
git add tests/ requirements-dev.txt
git commit -m "test: add API endpoint tests for FastAPI migration"
```

---

### Task 4: Implement `app.py` with FastAPI

**Files:**
- Create: `app.py`

- [ ] **Step 1: Write the FastAPI application**

```python
import ollama
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

app = FastAPI()
templates = Jinja2Templates(directory="templates")


def call_ollama_api(model_name: str, prompt: str, image_bytes: bytes) -> str:
    response = ollama.generate(
        model=model_name,
        prompt=prompt,
        images=[image_bytes],
        stream=False,
    )
    return response.get("response", "").strip()


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/models")
async def list_models():
    try:
        res = ollama.list()
        model_names = [m.model for m in res.models]
        return {"models": model_names, "status": "online"}
    except Exception as e:
        print(f"[ERROR] Could not connect to local Ollama service: {e}")
        return {"models": [], "status": "offline", "error": str(e)}


@app.post("/api/caption")
async def caption_image(
    model_name: str = Form(None),
    prompt: str = Form("Describe this image in detail:"),
    file: UploadFile = File(None),
):
    if not model_name:
        return JSONResponse(
            {"error": "Model name missing. Please select a model."},
            status_code=400,
        )

    if file is None or file.filename == "":
        return JSONResponse(
            {"error": "No image file provided."},
            status_code=400,
        )

    try:
        image_bytes = await file.read()
        caption = call_ollama_api(model_name, prompt, image_bytes)
        return {"caption": caption}
    except Exception as e:
        print(f"\n*** SERVER-SIDE CAPTIONING ERROR ***")
        print(f"Details: {e}")
        print("************************************")
        return JSONResponse(
            {"error": f"Failed to generate caption: {str(e)}"},
            status_code=500,
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
```

- [ ] **Step 2: Run tests to verify they pass**

```bash
pytest tests/test_app.py -v
```

Expected: All 6 tests PASS.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: implement FastAPI backend replacing Flask"
```

---

### Task 5: Create `setup_and_run.sh`

**Files:**
- Create: `setup_and_run.sh`

- [ ] **Step 1: Write the launcher script**

```bash
#!/bin/bash
set -e

PORT=5000
VENV_DIR="venv"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

cleanup() {
    echo ""
    echo "Shutting down..."
    kill $SERVER_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed. Install Python 3.8+ and try again."
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

echo "Installing dependencies..."
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -r requirements.txt

echo "Starting server on http://localhost:$PORT"
"$VENV_DIR/bin/uvicorn" app:app --host 0.0.0.0 --port "$PORT" &
SERVER_PID=$!

sleep 1
open "http://localhost:$PORT"

echo "Press Ctrl+C to stop the server."
wait $SERVER_PID
```

- [ ] **Step 2: Make it executable**

```bash
chmod +x setup_and_run.sh
```

- [ ] **Step 3: Commit**

```bash
git add setup_and_run.sh
git commit -m "feat: add macOS launcher script"
```

---

### Task 6: Update `README.md`

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write the README**

```markdown
# Ollama Local Image Captioner (macOS)

A local web application for captioning image datasets using Ollama vision models. Ideal for building ML/AI/Stable Diffusion/LoRA training pipelines where privacy and local control matter.

Forked from [eddcgpro/ollama_captioner](https://github.com/eddcgpro/ollama_captioner) and ported to macOS with FastAPI.

## Features

- Live Ollama connection monitor
- Dynamic model selector (fetches locally installed vision models)
- Drag-and-drop image upload with batch processing
- Editable captions with queue control and abort
- Export: CSV, combined TXT, individual TXTs, ZIP (for Kohya/LoRA pipelines)

## Prerequisites

1. **Python 3.8+** (pre-installed on macOS or via `brew install python`)
2. **Ollama** installed and running:
   ```bash
   brew install ollama
   ollama serve
   ```
3. **A vision-capable model** pulled:
   ```bash
   ollama pull gemma3:latest
   ```

## Quick Start

```bash
chmod +x setup_and_run.sh
./setup_and_run.sh
```

This creates a virtual environment, installs dependencies, starts the server, and opens your browser to `http://localhost:5000`.

## Manual Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --port 5000
```

Then open http://localhost:5000 in your browser.

## Usage

1. Select a vision model from the dropdown
2. Set your captioning prompt (can include a trigger word)
3. Upload images (drag & drop or browse)
4. Click "Generate All" or caption individually
5. Edit captions inline
6. Export in your preferred format
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add macOS README with FastAPI setup instructions"
```

---

### Task 7: End-to-End Manual Verification

**Files:**
- No file changes — verification task

- [ ] **Step 1: Run the app**

```bash
cd /Users/erikhansen/tools/ollama_captioner_mac
./setup_and_run.sh
```

Expected: Browser opens to `http://localhost:5000` showing the captioner UI.

- [ ] **Step 2: Verify model list**

In the browser, check that the model dropdown populates with your locally installed Ollama vision models. If Ollama isn't running, the UI should show an offline indicator.

- [ ] **Step 3: Test captioning**

Upload any image, select a model, click "Generate". Verify a caption appears.

- [ ] **Step 4: Test export**

Caption at least 2 images, then test each export option (CSV, combined TXT, ZIP).

- [ ] **Step 5: Stop the server**

Press Ctrl+C in the terminal. Verify clean shutdown.

---

### Task 8: Clean Up Upstream Temp Directory

**Files:**
- No project file changes

- [ ] **Step 1: Remove the temporary upstream clone**

```bash
rm -rf /Users/erikhansen/tools/ollama_captioner_mac_upstream
```

- [ ] **Step 2: Final commit with docs**

```bash
cd /Users/erikhansen/tools/ollama_captioner_mac
git add docs/
git commit -m "docs: add design spec and implementation plan"
```
