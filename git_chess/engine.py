from pathlib import Path
from typing import Tuple, List, Optional
import chess
from git_chess.utils import get_board_fen_path

UNICODE_PIECES = {
    'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙',
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
    '.': '·'
}

class GitChessEngine:
    """Manages chess board state, move validation, and FEN persistence."""

    def __init__(self, fen_path: Optional[Path] = None):
        self.fen_path = fen_path or get_board_fen_path()
        self.board = chess.Board()
        self.load_state()

    def load_state(self) -> chess.Board:
        """Reads current FEN from file, defaulting to initial chess position if missing."""
        if self.fen_path.exists():
            fen_str = self.fen_path.read_text().strip()
            if fen_str:
                self.board = chess.Board(fen_str)
        else:
            self.board = chess.Board()
            self.save_state()
        return self.board

    def save_state(self) -> None:
        """Flushes active board state FEN back to disk."""
        self.fen_path.write_text(self.board.fen() + "\n")

    def reset_state(self) -> None:
        """Resets board to initial standard setup."""
        self.board = chess.Board()
        self.save_state()

    def parse_move(self, move_str: str) -> Optional[chess.Move]:
        """Attempts to parse move_str as UCI first, then SAN."""
        clean_str = move_str.strip()
        
        # Try UCI (e.g. e2e4, g1f3)
        try:
            move = chess.Move.from_uci(clean_str)
            if move in self.board.legal_moves:
                return move
        except ValueError:
            pass

        # Try Standard Algebraic Notation (e.g. e4, Nf3, O-O)
        try:
            return self.board.parse_san(clean_str)
        except ValueError:
            pass

        return None

    def apply_move(self, move_str: str) -> Tuple[bool, str]:
        """Validates move_str, applies it to board, saves FEN, and returns status message."""
        move = self.parse_move(move_str)
        if not move:
            legal_san = [self.board.san(m) for m in self.board.legal_moves]
            preview = ", ".join(legal_san[:8])
            return False, f"Invalid move '{move_str}'. Legal moves: {preview}..."

        san_move = self.board.san(move)
        uci_move = move.uci()
        self.board.push(move)
        self.save_state()

        status = f"Move applied: {san_move} ({uci_move})"
        if self.board.is_checkmate():
            status += " [CHECKMATE]"
        elif self.board.is_check():
            status += " [CHECK]"
        elif self.board.is_stalemate():
            status += " [STALEMATE]"
        elif self.board.is_insufficient_material():
            status += " [DRAW: Insufficient Material]"
        elif self.board.can_claim_draw():
            status += " [DRAW: Claimable]"

        return True, status

    def get_legal_moves(self) -> List[str]:
        """Returns list of legal moves formatted as SAN (UCI)."""
        return [f"{self.board.san(m)} ({m.uci()})" for m in self.board.legal_moves]

    def render_ascii(self) -> str:
        """Returns ASCII representation of current board."""
        return str(self.board)

    def render_unicode(self) -> str:
        """Returns Unicode symbol representation of current board with ranks/files."""
        lines = []
        lines.append("  a b c d e f g h")
        for rank in range(7, -1, -1):
            row = [str(rank + 1)]
            for file in range(8):
                square = chess.square(file, rank)
                piece = self.board.piece_at(square)
                symbol = UNICODE_PIECES.get(piece.symbol(), '·') if piece else '·'
                row.append(symbol)
            row.append(str(rank + 1))
            lines.append(" ".join(row))
        lines.append("  a b c d e f g h")
        return "\n".join(lines)

    def update_readme(self) -> None:
        """Updates board block and board.svg in repo."""
        repo_root = self.fen_path.parent
        svg_path = repo_root / "board.svg"
        readme_path = repo_root / "README.md"

        # Generate SVG board
        from git_chess.visualization import generate_board_svg
        svg_content = generate_board_svg(self.board)
        svg_path.write_text(svg_content)

        if not readme_path.exists():
            return

        content = readme_path.read_text()
        start_marker = "<!-- BOARD_START -->"
        end_marker = "<!-- BOARD_END -->"

        if start_marker in content and end_marker in content:
            pre = content.split(start_marker)[0]
            post = content.split(end_marker)[1]
            board_str = self.render_unicode()
            turn_str = "White to move" if self.board.turn == chess.WHITE else "Black to move"
            new_block = (
                f"{start_marker}\n"
                f"![GitChess Board](board.svg)\n\n"
                f"```\n{board_str}\n\n{turn_str}\n```\n"
                f"{end_marker}"
            )
            readme_path.write_text(pre + new_block + post)
