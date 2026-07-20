import pytest
import chess
from git_chess.engine import GitChessEngine

def test_engine_initialization(tmp_path):
    fen_file = tmp_path / "board.fen"
    engine = GitChessEngine(fen_path=fen_file)
    assert engine.board.fen() == chess.STARTING_FEN
    assert fen_file.exists()

def test_valid_move_uci_and_san(tmp_path):
    fen_file = tmp_path / "board.fen"
    engine = GitChessEngine(fen_path=fen_file)
    
    # Apply White e2e4
    success, msg = engine.apply_move("e2e4")
    assert success is True
    assert "e4" in msg
    assert engine.board.turn == chess.BLACK

    # Apply Black e7e5 via SAN
    success, msg = engine.apply_move("e5")
    assert success is True
    assert "e5" in msg
    assert engine.board.turn == chess.WHITE

def test_invalid_move_rejection(tmp_path):
    fen_file = tmp_path / "board.fen"
    engine = GitChessEngine(fen_path=fen_file)
    
    success, msg = engine.apply_move("e9e10")
    assert success is False
    assert "Invalid move" in msg

def test_fool_checkmate(tmp_path):
    fen_file = tmp_path / "board.fen"
    engine = GitChessEngine(fen_path=fen_file)
    
    # 1. f3 e5 2. g4 Qh4#
    engine.apply_move("f3")
    engine.apply_move("e5")
    engine.apply_move("g4")
    success, msg = engine.apply_move("Qh4")
    
    assert success is True
    assert "[CHECKMATE]" in msg
    assert engine.board.is_checkmate() is True

def test_git_log_replay_consistency():
    engine = GitChessEngine()
    fen_disk = engine.fen_path.read_text().strip()
    assert engine.board.fen() == fen_disk
