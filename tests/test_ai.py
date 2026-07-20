import pytest
import chess
from git_chess.engine import GitChessEngine
from git_chess.ai import get_best_move, evaluate_board

def test_evaluation():
    board = chess.Board()
    # Initial board position evaluation: 0 material difference + 20 legal moves * 3 mobility bonus = 60
    score = evaluate_board(board)
    assert score == 60

def test_ai_best_move_returns_legal_move():
    board = chess.Board()
    move = get_best_move(board, depth=1)
    assert move in board.legal_moves

def test_ai_engine_types():
    board = chess.Board()
    move_minimax = get_best_move(board, depth=1, engine_type="minimax")
    assert move_minimax in board.legal_moves
    move_auto = get_best_move(board, depth=1, engine_type="auto")
    assert move_auto in board.legal_moves

def test_ai_finds_m1():
    # White can mate in 1: 1. Qh7# or 1. Qf7#
    board = chess.Board("r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4")
    move = get_best_move(board, depth=1)
    assert move.uci() in ["h5f7", "h5h7"]
