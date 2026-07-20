import pytest
import chess
from pathlib import Path
from git_chess.pgn import export_pgn_string, import_pgn_file
from git_chess.engine import GitChessEngine

def test_export_pgn_string():
    engine = GitChessEngine()
    pgn_str = export_pgn_string()
    assert "[Event \"GitChess Match\"]" in pgn_str

def test_import_pgn_file(tmp_path):
    pgn_file = tmp_path / "game.pgn"
    pgn_file.write_text("""[Event "Test Game"]
[Site "Local"]
[Date "2026.07.20"]
[Round "1"]
[White "Player1"]
[Black "Player2"]
[Result "*"]

1. e4 e5 2. Nf3 Nc6 *
""")
    count = import_pgn_file(pgn_file)
    assert count == 4
