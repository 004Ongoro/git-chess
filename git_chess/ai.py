import random
import shutil
from typing import Optional
import chess
import chess.engine

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000,
}

PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]

ROOK_TABLE = [
      0,  0,  0,  0,  0,  0,  0,  0,
      5, 10, 10, 10, 10, 10, 10,  5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
      0,  0,  0,  5,  5,  0,  0,  0
]

QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

KING_TABLE = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20
]

PST_MAP = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
    chess.KING: KING_TABLE,
}

def evaluate_board(board: chess.Board) -> int:
    """Evaluates board material, piece-square positions, and mobility from White's perspective."""
    if board.is_checkmate():
        return -99999 if board.turn == chess.WHITE else 99999
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_threefold_repetition():
        return 0

    score = 0
    for sq, p in board.piece_map().items():
        base_val = PIECE_VALUES.get(p.piece_type, 0)
        table = PST_MAP.get(p.piece_type, [])
        pst_val = table[sq] if p.color == chess.WHITE else table[chess.square_mirror(sq)] if table else 0

        total_piece_score = base_val + pst_val
        if p.color == chess.WHITE:
            score += total_piece_score
        else:
            score -= total_piece_score

    # Add mobility difference bonus
    if board.turn == chess.WHITE:
        score += board.legal_moves.count() * 3
    else:
        score -= board.legal_moves.count() * 3

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
    best_moves = []
    best_eval = -999999 if is_white else 999999

    for move in legal_moves:
        board.push(move)
        eval_val = minimax(board, depth - 1, -999999, 999999, not is_white)
        board.pop()

        if is_white:
            if eval_val > best_eval:
                best_eval = eval_val
                best_moves = [move]
            elif eval_val == best_eval:
                best_moves.append(move)
        else:
            if eval_val < best_eval:
                best_eval = eval_val
                best_moves = [move]
            elif eval_val == best_eval:
                best_moves.append(move)

    return random.choice(best_moves) if best_moves else legal_moves[0]
