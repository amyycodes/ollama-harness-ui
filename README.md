# Ollama Harness UI

A local, lightweight Ollama agent harness UI for small models.

## Why this exists
This project lets you run a compact coding agent locally with a minimal tool loop. It is designed for small models, fast responses, and simple repository tasks such as reading, searching, and editing files.

## Features
- Local Ollama chat integration
- Minimal browser UI
- Tool loop with `read_file`, `list_dir`, `search_files`, and `write_file`
- Short system prompt for speed and reliability
- Works with small models like `llama3.2:3b`

## Quick start

1. Install Ollama and pull a model:

```bash
ollama pull llama3.2:3b
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the app:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

5. Open http://localhost:8000

## Default system prompt

The app uses a compact prompt tuned for small models:

> You are a fast local coding agent. Read files before writing. Use tools sparingly. Keep responses concise and finish the task once evidence supports it.

## Notes
- This assumes Ollama is running on `http://localhost:11434`
- You can change the model in the UI
- The tool loop is intentionally small and safe for experimentation
