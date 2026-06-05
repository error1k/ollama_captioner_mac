import ollama
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
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
    return templates.TemplateResponse(name="index.html", request=request)


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
