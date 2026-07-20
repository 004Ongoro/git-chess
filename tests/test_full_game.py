import pytest
import subprocess
import chess
from git_chess.engine import GitChessEngine
from git_chess.ai import get_best_move

def test_scholars_mate_sequence():
    """Test a short full game resulting in checkmate."""
    engine = GitChessEngine()
    engine.reset_state()
    
    # 1. e4 e5
    engine.apply_move("e4")
    engine.apply_move("e5")
    # 2. Bc4 Nc6
    engine.apply_move("Bc4")
    engine.apply_move("Nc6")
    # 3. Qh5 Nf6
    engine.apply_move("Qh5")
    engine.apply_move("Nf6")
    # 4. Qxf7#
    success, msg = engine.apply_move("Qxf7#")
    
    assert success is True
    assert "[CHECKMATE]" in msg
    assert engine.board.is_checkmate() is True

def test_full_ai_game_simulation():
    """Simulates a complete game played by AI until checkmate, draw, or 40 moves."""
    engine = GitChessEngine()
    engine.reset_state()
    
    move_count = 0
    while not engine.board.is_game_over() and move_count < 40:
        move_obj = get_best_move(engine.board, depth=2)
        san_str = engine.board.san(move_obj)
        success, msg = engine.apply_move(san_str)
        assert success is True, f"Move {san_str} failed: {msg}"
        move_count += 1

    # Verify that FEN is valid and board has progressed
    assert len(engine.board.move_stack) == move_count
    assert engine.fen_path.exists()
