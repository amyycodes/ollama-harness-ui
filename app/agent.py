import json
import re
from pathlib import Path

from app.config import DEFAULT_SYSTEM_PROMPT
from app.ollama_client import OllamaClient, extract_message_content


class ToolExecutionError(RuntimeError):
    pass


def list_dir(path: str) -> str:
    root = Path(path)
    if not root.exists():
        raise ToolExecutionError(f"Path does not exist: {path}")
    if root.is_file():
        return f"FILE {root.name}"

    entries = []
    for item in sorted(root.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
        entries.append(f"{'DIR' if item.is_dir() else 'FILE'} {item.name}")
    return "\n".join(entries) if entries else "(empty directory)"


def read_file(path: str, start: int = 0, end: int = 250) -> str:
    file_path = Path(path)
    if not file_path.exists():
        raise ToolExecutionError(f"File does not exist: {path}")
    if not file_path.is_file():
        raise ToolExecutionError(f"Not a file: {path}")

    text = file_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    subset = lines[start:end]
    if not subset:
        return "(empty file)"
    return "\n".join(f"{idx + 1}: {line}" for idx, line in enumerate(subset, start=start + 1))


def search_files(path: str, pattern: str, limit: int = 20) -> str:
    root = Path(path)
    if not root.exists():
        raise ToolExecutionError(f"Path does not exist: {path}")

    matches = []
    pattern_lc = pattern.lower()
    for item in root.rglob("*"):
        if item.is_file():
            try:
                content = item.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            if pattern_lc in content.lower():
                matches.append(str(item.relative_to(root)))
                if len(matches) >= limit:
                    break
    return "\n".join(matches) if matches else "No matches found."


def write_file(path: str, content: str) -> str:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return f"Wrote {path}"


TOOLS = {
    "list_dir": list_dir,
    "read_file": read_file,
    "search_files": search_files,
    "write_file": write_file,
}


def extract_tool_call(text: str):
    text = text.strip()
    if not text:
        return None

    # Accept a few common styles so small models can call tools reliably.
    for pattern in [
        r"tool_call\s*[:=]\s*(\{.*\})",
        r"tool\s*[:=]\s*(\{.*\})",
    ]:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                payload = json.loads(match.group(1))
                if isinstance(payload, dict) and "name" in payload:
                    return payload
            except json.JSONDecodeError:
                pass

    for name in TOOLS:
        match = re.search(rf"{name}\s*\((.*?)\)", text, re.DOTALL)
        if match:
            raw = match.group(1).strip()
            try:
                args = json.loads(f"{{{raw}}}") if raw else {}
            except Exception:
                args = {}
            return {"name": name, "arguments": args}

    return None


def call_tool(name: str, arguments: dict, workspace: str) -> str:
    func = TOOLS.get(name)
    if func is None:
        raise ToolExecutionError(f"Unknown tool: {name}")

    resolved = {}
    for key, value in arguments.items():
        resolved[key] = value.strip() if isinstance(value, str) else value

    if "path" in resolved and isinstance(resolved["path"], str):
        path_obj = Path(resolved["path"])
        if not path_obj.is_absolute():
            resolved["path"] = str((Path(workspace) / path_obj).resolve())

    return func(**resolved)


def run_agent(task: str, workspace: str = ".", model: str = "llama3.2:3b") -> str:
    client = OllamaClient(model=model)
    messages = [
        {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    for _ in range(6):
        resp = client.chat(messages)
        content = extract_message_content(resp)
        if not content:
            return "The model returned no usable response."

        tool_call = extract_tool_call(content)
        if tool_call is None:
            return content.strip()

        name = tool_call.get("name") or tool_call.get("tool")
        arguments = tool_call.get("arguments") or tool_call.get("args") or {}
        try:
            result = call_tool(name, arguments, workspace)
        except Exception as exc:
            result = f"Tool error: {exc}"

        messages.append({"role": "assistant", "content": content})
        messages.append({"role": "user", "content": f"Tool result for {name}:\n{result}"})

    return "The agent hit the max tool loop. Narrow the task and try again."
