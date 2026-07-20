from pathlib import Path
from typing import List
import chess
import chess.pgn
import io
import subprocess
from git_chess.engine import GitChessEngine

def export_pgn_string() -> str:
    """Exports current game from Git history as a PGN string."""
    engine = GitChessEngine()
    game = chess.pgn.Game.from_board(engine.board)
    game.headers["Event"] = "GitChess Match"
    game.headers["Site"] = "Git Repository"
    game.headers["White"] = "White Player"
    game.headers["Black"] = "Black Player"
    
    exporter = chess.pgn.StringExporter(headers=True, variations=False, comments=False)
    return game.accept(exporter)

def import_pgn_file(pgn_path: Path) -> int:
    """Reads moves from a PGN file and applies them as Git commits."""
    if not pgn_path.exists():
        raise FileNotFoundError(f"PGN file not found: {pgn_path}")

    content = pgn_path.read_text()
    game = chess.pgn.read_game(io.StringIO(content))
    if not game:
        raise ValueError("Invalid or empty PGN file.")

    # Reset game board first
    subprocess.run(["git", "commit", "--allow-empty", "--no-verify", "-m", "reset: game"], check=False)
    
    board = game.board()
    count = 0
    for move in game.mainline_moves():
        san_str = board.san(move)
        board.push(move)
        res = subprocess.run(["git", "commit", "--allow-empty", "-m", f"move: {san_str}"], check=False)
        if res.returncode == 0:
            count += 1

    return count
