import pytest
import chess
from git_chess.engine import GitChessEngine
from git_chess.ai import get_best_move, evaluate_board

def test_evaluation():
    board = chess.Board()
    # Initial board position evaluation: 0 material difference + 20 legal moves * 5 mobility bonus = 100
    score = evaluate_board(board)
    assert score == 100

def test_ai_best_move_returns_legal_move():
    board = chess.Board()
    move = get_best_move(board, depth=1)
    assert move in board.legal_moves

def test_ai_finds_m1():
    # White can mate in 1: 1. Qh7# or 1. Qf7#
    board = chess.Board("r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4")
    move = get_best_move(board, depth=1)
    assert move.uci() in ["h5f7", "h5h7"]
