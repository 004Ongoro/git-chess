import pytest
import chess
from git_chess.visualization import generate_board_svg, BOARD_THEMES

def test_generate_board_svg_themes():
    board = chess.Board()
    for theme_name in BOARD_THEMES:
        svg = generate_board_svg(board, theme=theme_name)
        assert "<svg" in svg
        assert BOARD_THEMES[theme_name]["square dark"] in svg
