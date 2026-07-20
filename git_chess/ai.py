import random
import shutil
import subprocess
from typing import Optional
import chess
import chess.engine

# Piece material values
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000,
}

def evaluate_board(board: chess.Board) -> int:
    """Evaluates board material and mobility balance from White's perspective."""
    if board.is_checkmate():
        return -99999 if board.turn == chess.WHITE else 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    for square, piece in board.piece_map().items():
        val = PIECE_VALUES.get(piece.piece_type, 0)
        if piece.color == chess.WHITE:
            score += val
        else:
            score -= val

    # Add small bonus for legal move mobility
    white_mobility = board.legal_moves.count() if board.turn == chess.WHITE else 0
    score += white_mobility * 5
    return score

def minimax(board: chess.Board, depth: int, alpha: int, beta: int, maximizing: bool) -> int:
    """Minimax search with alpha-beta pruning."""
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing:
        max_eval = -999999
        for move in board.legal_moves:
            board.push(move)
            eval_val = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval_val)
            alpha = max(alpha, eval_val)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = 999999
        for move in board.legal_moves:
            board.push(move)
            eval_val = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval_val)
            beta = min(beta, eval_val)
            if beta <= alpha:
                break
        return min_eval

def get_best_move(board: chess.Board, depth: int = 3) -> chess.Move:
    """Calculates best move using Minimax engine, falling back to Stockfish if available."""
    stockfish_path = shutil.which("stockfish")
    if stockfish_path:
        try:
            with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
                result = engine.play(board, chess.engine.Limit(time=0.5))
                if result.move:
                    return result.move
        except Exception:
            pass

    # Built-in Minimax fallback
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        raise ValueError("No legal moves available.")

    is_white = board.turn == chess.WHITE
    best_move = legal_moves[0]
    best_eval = -999999 if is_white else 999999

    for move in legal_moves:
        board.push(move)
        eval_val = minimax(board, depth - 1, -999999, 999999, not is_white)
        board.pop()

        if is_white and eval_val > best_eval:
            best_eval = eval_val
            best_move = move
        elif not is_white and eval_val < best_eval:
            best_eval = eval_val
            best_move = move

    return best_move
