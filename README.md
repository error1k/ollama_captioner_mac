# Ollama Local Image Captioner (macOS)

A local web application for captioning image datasets using Ollama vision models. Ideal for building ML/AI/Stable Diffusion/LoRA training pipelines where privacy and local control matter.

Forked from [eddcgpro/ollama_captioner](https://github.com/eddcgpro/ollama_captioner) and ported to macOS with FastAPI.

## Changes from Upstream

- **Flask → FastAPI + Uvicorn** — async backend, better performance
- **Vision-only model filter** — the model dropdown only shows vision-capable models (detected via `ollama.show()` capabilities at startup)
- **macOS launcher script** — replaces the Windows `.bat` with `setup_and_run.sh` (venv, deps, browser open)
- **Trimmed dependencies** — removed unused `torch`, `torchvision`, `transformers`, `Pillow`, and `requests`
- **Default port 5050** — avoids conflict with macOS AirPlay Receiver on port 5000
- **Frontend unchanged** — `index.html` is identical to upstream; API contracts are the same

## Features

- Live Ollama connection monitor
- Dynamic model selector (vision-capable models only)
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

This creates a virtual environment, installs dependencies, starts the server, and opens your browser to `http://localhost:5050`.

## Manual Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --port 5050
```

Then open http://localhost:5050 in your browser.

## Usage

1. Select a vision model from the dropdown
2. Set your captioning prompt (can include a trigger word)
3. Upload images (drag & drop or browse)
4. Click "Generate All" or caption individually
5. Edit captions inline
6. Export in your preferred format
