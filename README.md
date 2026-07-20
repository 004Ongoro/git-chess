# GitChess ♟️ Git-driven Chess Engine

Welcome to **GitChess**, a chess game where every chess move is performed through Git commits and operations.

## Current Game State

<!-- BOARD_START -->
```
r n b q k b n r
p p p p p p p p
. . . . . . . .
. . . . . . . .
. . . . . . . .
. . . . . . . .
P P P P P P P P
R N B Q K B N R

White to move
```
<!-- BOARD_END -->

## Quick Start

1. Install dependencies:
   ```bash
   pip install -e .
   ```
2. Initialize repository and Git hooks:
   ```bash
   git-chess init
   ```
3. Make moves using git commit messages or `git-chess move`:
   ```bash
   git commit --allow-empty -m "move: e2e4"
   ```
