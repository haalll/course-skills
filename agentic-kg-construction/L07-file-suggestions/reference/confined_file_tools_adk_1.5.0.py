"""Confined file tools for an ADK agent (google-adk 1.5.0). Our own wording; checked with scripted fake models in the lab (round 9).
Pass the import root in; never take it from the model. Not covered: a link swapped between the check and the open (race),
hard links, files the OS lets the agent uid read but the root should not expose (use a dedicated uid or a read-only mount for that)."""
import os
from pathlib import Path
from google.adk.tools import ToolContext

MAX_BYTES = 20_000
MAX_LINES = 100

def make_tools(import_dir: str):
    root = Path(import_dir).resolve()

    def list_import_files(tool_context: ToolContext) -> dict:
        """List files under the import directory (relative paths) and remember them for suggestions."""
        files = sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file() and p.resolve().is_relative_to(root))
        tool_context.state["all_available_files"] = files
        return {"status": "success", "files": files}

    def sample_file(relative_path: str) -> dict:
        """Return the first lines (at most 100 lines and 20,000 bytes) of a text file under the import directory."""
        if "\x00" in relative_path or os.path.isabs(relative_path):
            return {"status": "error", "error_message": "Give a plain path relative to the import directory."}
        p = (root / relative_path).resolve()                  # resolves '..' and symlinks
        if not p.is_relative_to(root):                        # component-wise, not str.startswith
            return {"status": "error", "error_message": "That path leaves the import directory. Pick one from list_import_files."}
        if not p.is_file():
            return {"status": "error", "error_message": f"{relative_path} is not a file here. Pick one from list_import_files."}
        with open(p, "rb") as f: data = f.read(MAX_BYTES + 1)
        text = data[:MAX_BYTES].decode("utf-8", "replace")
        return {"status": "success", "content": "".join(text.splitlines(True)[:MAX_LINES]), "truncated": len(data) > MAX_BYTES}

    def set_suggested_files(files: list[str], tool_context: ToolContext) -> dict:
        """Record the files you suggest. Every path must come from list_import_files."""
        listed = tool_context.state.get("all_available_files")
        if listed is None: return {"status": "error", "error_message": "Call list_import_files first."}
        bad = [f for f in files if f not in listed]
        if bad: return {"status": "error", "error_message": f"Not in the listed files: {bad}."}
        tool_context.state["suggested_files"] = list(files); return {"status": "success"}

    def approve_suggested_files(tool_context: ToolContext) -> dict:
        """Call only after the user confirmed the suggested files. Takes no arguments."""
        if "suggested_files" not in tool_context.state:
            return {"status": "error", "error_message": "No files suggested yet."}
        tool_context.state["approved_files"] = list(tool_context.state["suggested_files"]); return {"status": "success"}

    return list_import_files, sample_file, set_suggested_files, approve_suggested_files
