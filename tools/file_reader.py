from pathlib import Path

from langchain.tools import tool

from config import DATA_DIR
from logging_config import get_logger

logger = get_logger()

ALLOWED_EXTENSIONS = {".txt", ".md", ".json"}
MAX_CHARACTERS = 12_000


def _safe_path(filename: str) -> Path:
    requested_path = (DATA_DIR / filename).resolve()
    safe_root = DATA_DIR.resolve()

    if safe_root not in requested_path.parents and requested_path != safe_root:
        raise ValueError("Only files inside the data folder can be read.")

    if requested_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise ValueError(f"Only these file types are allowed: {allowed}")

    return requested_path


@tool
def read_study_file(filename: str) -> str:
    """Read a study file from the project's data folder.

    Use only a file name such as 'notes.txt', not a full computer path.
    Supported file types: .txt, .md, .json.
    """
    try:
        path = _safe_path(filename)

        if not path.exists() or not path.is_file():
            available_files = [
                item.name for item in DATA_DIR.iterdir()
                if item.is_file() and item.suffix.lower() in ALLOWED_EXTENSIONS
            ]
            return (
                f"File '{filename}' was not found. "
                f"Available files: {available_files or 'none'}"
            )

        content = path.read_text(encoding="utf-8", errors="replace")
        if len(content) > MAX_CHARACTERS:
            content = content[:MAX_CHARACTERS] + "\n\n[File shortened for safety.]"

        logger.info("TOOL read_study_file | file=%r | characters=%s", filename, len(content))
        return f"Contents of {path.name}:\n\n{content}"

    except (OSError, ValueError) as exc:
        logger.warning("TOOL read_study_file failed | file=%r | error=%s", filename, exc)
        return f"File reader error: {exc}"
