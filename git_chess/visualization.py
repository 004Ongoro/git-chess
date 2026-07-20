from pathlib import Path
from typing import Optional
import chess
import chess.svg

BOARD_THEMES = {
    "classic": {"square light": "#ffce9e", "square dark": "#d18b47"},
    "wood": {"square light": "#f0d9b5", "square dark": "#b58863"},
    "dark": {"square light": "#9e9e9e", "square dark": "#424242"},
    "neon": {"square light": "#80deea", "square dark": "#00838f"},
    "icy": {"square light": "#e0f7fa", "square dark": "#80deea"},
}

def generate_board_svg(board: chess.Board, last_move: Optional[chess.Move] = None, theme: str = "classic") -> str:
    """Generates styled SVG board string with move highlights and theme colors."""
    fill = {}
    if board.move_stack:
        last = board.peek()
        fill = {last.from_square: "#baca44", last.to_square: "#baca44"}
    
    if board.is_check():
        king_square = board.king(board.turn)
        if king_square is not None:
            fill[king_square] = "#e63946"

    arrows = []
    if board.move_stack:
        last = board.peek()
        arrows = [chess.svg.Arrow(last.from_square, last.to_square, color="#1e88e5")]

    colors = BOARD_THEMES.get(theme.lower(), BOARD_THEMES["classic"])

    svg_data = chess.svg.board(
        board=board,
        fill=fill,
        arrows=arrows,
        colors=colors,
        size=400,
        coordinates=True
    )
    return svg_data

def generate_board_html(board: chess.Board, theme: str = "classic") -> str:
    """Generates standalone HTML page showcasing current board SVG."""
    svg_content = generate_board_svg(board, theme=theme)
    side = "White" if board.turn == chess.WHITE else "Black"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitChess Viewer</title>
    <style>
        body {{
            background: #121212;
            color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
        }}
        .card {{
            background: #1e1e1e;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.5);
            text-align: center;
        }}
        h1 {{ margin-top: 0; font-size: 24px; color: #4CAF50; }}
        .status {{ font-size: 18px; margin-bottom: 16px; color: #bbb; }}
        .svg-container {{ display: inline-block; border-radius: 8px; overflow: hidden; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>GitChess Viewer</h1>
        <div class="status">Turn: <strong>{side}</strong> | Move: <strong>{board.fullmove_number}</strong></div>
        <div class="svg-container">
            {svg_content}
        </div>
    </div>
</body>
</html>
"""
