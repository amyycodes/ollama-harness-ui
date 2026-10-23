from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.agent import run_agent
from app.config import DEFAULT_MODEL, SETTINGS

app = FastAPI(title="Ollama Harness UI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


class ChatRequest(BaseModel):
    task: str
    model: str | None = None
    workspace: str = "."


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html", "r", encoding="utf-8") as fh:
        return HTMLResponse(content=fh.read())


@app.post("/api/chat")
async def chat(req: ChatRequest):
    if not req.task.strip():
        raise HTTPException(status_code=400, detail="Task is required.")

    try:
        answer = run_agent(req.task, workspace=req.workspace, model=req.model or DEFAULT_MODEL)
        return {"answer": answer}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/health")
async def health():
    return {"status": "ok", "model": SETTINGS.model}
