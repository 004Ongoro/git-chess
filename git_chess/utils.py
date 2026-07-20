import os
from pathlib import Path

def get_repo_root() -> Path:
    """Returns the root directory of the Git project."""
    curr = Path.cwd()
    for p in [curr] + list(curr.parents):
        if (p / "board.fen").exists() or (p / ".git").exists():
            return p
    return curr

def get_board_fen_path() -> Path:
    """Returns absolute path to board.fen file."""
    return get_repo_root() / "board.fen"
