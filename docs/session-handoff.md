# Session Handoff

## Status

**Phase:** Implementation complete, published to GitHub  
**Date:** 2026-06-05

## What's Done

- Cloned upstream, verified unused deps (torch/torchvision/transformers/Pillow/requests all dead)
- Created FastAPI backend (`app.py`) replacing Flask — same 3 endpoints, same JSON contracts
- Vision-only model filter: checks `ollama.show()` capabilities at startup, only lists vision models
- macOS launcher script (`setup_and_run.sh`) — venv, deps, browser open, graceful shutdown
- Trimmed `requirements.txt` to only what's used (fastapi, uvicorn, jinja2, python-multipart, ollama)
- Test suite: 6 async tests covering all endpoints (all passing)
- Changed default port to 5050 (macOS AirPlay Receiver occupies 5000)
- README with "Changes from Upstream" section
- Published to GitHub: https://github.com/error1k/ollama_captioner_mac
- Opened license request issue on upstream: https://github.com/eddcgpro/ollama_captioner/issues/1

## In Progress

- Nothing actively in progress

## Next Steps

1. Manual end-to-end verification (Task 7 from plan) — run the app, test captioning, test exports
2. Check if upstream author responds to license request
3. Optional: add a LICENSE file once upstream clarifies

## Open Questions

- Awaiting license clarification from upstream author

## Gotchas

- Port 5000 is taken by macOS ControlCenter (AirPlay Receiver) — use 5050 or pass custom port as arg
- `ollama.show()` returns a Pydantic model, not a dict — use `.capabilities` attribute, not `.get("model_info")`
- `TemplateResponse` in Starlette 0.40+ requires keyword args (`name=`, `request=`), not positional
- Vision models are loaded at startup — restart the server after pulling new models

## Resume Prompt

Read `docs/session-handoff.md`. Project is fully implemented and published. Remaining work: manual e2e verification and checking upstream license response.
