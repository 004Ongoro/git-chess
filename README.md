# GitChess ♟️ Git-Driven Chess Engine

[![GitChess CI](https://github.com/004Ongoro/git-chess/actions/workflows/git-chess-ci.yml/badge.svg)](https://github.com/004Ongoro/git-chess/actions)
[![Live Board](https://img.shields.io/badge/Live_Board-GitHub_Pages-brightgreen)](https://004Ongoro.github.io/git-chess/)

**GitChess** is a complete, fully featured chess game where every chess move is performed directly through Git commits and operations. The Git repository **is** the game board and the full game history.

🌐 **Live Web Viewer**: [004Ongoro.github.io/git-chess](https://004Ongoro.github.io/git-chess/)

---

## 🎮 Current Game Board

<!-- BOARD_START -->
![GitChess Board](board.svg)

```
  a b c d e f g h
8 ♜ ♞ ♝ ♛ ♚ ♝ ♞ ♜ 8
7 ♟ ♟ ♟ ♟ · ♟ ♟ ♟ 7
6 · · · · · · · · 6
5 · · · · ♟ · · · 5
4 · · · · ♙ · · · 4
3 · · · · · · · · 3
2 ♙ ♙ ♙ ♙ · ♙ ♙ ♙ 2
1 ♖ ♘ ♗ ♕ ♔ ♗ ♘ ♖ 1
  a b c d e f g h

White to move
```
<!-- BOARD_END -->

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Installation
Clone the repository and install the package locally:
```bash
git clone https://github.com/004Ongoro/git-chess.git
cd git-chess
pip install -e .
```

### 3. Initialize Git Hooks
Enable automatic move validation and board rendering hooks in your repository:
```bash
git-chess init
```

---

## ♟️ How to Play

### Option A: Pure Git Workflow (Recommended)
You can play chess using standard `git commit` commands!

```bash
# Make a move using SAN (Standard Algebraic Notation)
git commit --allow-empty -m "move: e4"

# Or using UCI (Universal Chess Interface) notation
git commit --allow-empty -m "move: e2e4"

# Knight to f3
git commit --allow-empty -m "move: Nf3"
```

If an illegal move is attempted, the Git commit will be automatically rejected with legal move options:
```text
GitChess Commit Rejected: 'e9e10' is not a legal move.
Legal moves: Nh6, Nf6, Nc6, Na6, h6, g6, f6, e6...
```

### Option B: Using the `git-chess` CLI Wrapper

```bash
# Check current board status and active turn
git-chess status

# List legal moves in a styled table
git-chess moves

# Make a move (automates git commit)
git-chess move e4

# Play vs AI (automatically triggers AI countermove after your move)
git-chess move e4 --vs-ai

# Force AI to generate and commit a move
git-chess ai-move

# View complete move history parsed from Git commits
git-chess log

# Undo the last move (rewinds Git HEAD)
git-chess undo

# Export board visualization to HTML or SVG
git-chess export --fmt html
git-chess view
```

---

## 🤖 Modes

### 1. Single-Player (vs Built-in AI)
Play against the built-in Minimax evaluation engine locally:
```bash
git-chess move e4 --vs-ai
```

### 2. Two-Player (Shared Git Repository)
Clone a shared repository with a friend and push/pull commits to alternate turns!
- White makes a move: `git commit --allow-empty -m "move: e4"` && `git push`
- Black pulls and makes a move: `git pull` && `git commit --allow-empty -m "move: e5"` && `git push`

### 3. Asynchronous GitHub Actions Opponent
Push your moves to GitHub (`main`/`master` branch). The included `.github/workflows/ai-opponent.yml` GitHub Action will detect White's move, compute Black's countermove using AI, commit it, and push it back to the repository!

---

## 🛠️ Project Architecture

```
git-chess/
├── git_chess/
│   ├── __init__.py
│   ├── cli.py            # Rich CLI interface (git-chess)
│   ├── engine.py         # python-chess logic & FEN state management
│   ├── ai.py             # Minimax & Stockfish AI opponent engine
│   ├── visualization.py  # SVG & HTML board renderers
│   └── utils.py          # Workspace & repository helpers
├── hooks/                # Git hook templates
│   ├── commit-msg        # Move validation hook
│   ├── post-commit       # Automatic board.svg & README updater
│   └── prepare-commit-msg
├── .github/workflows/    # Automation workflows
│   ├── git-chess-ci.yml  # Unit test & FEN integrity CI
│   └── ai-opponent.yml   # Automated GitHub Action AI opponent
├── tests/                # Unit test suite (pytest)
├── board.fen             # Active board state stored as FEN string
├── board.svg             # Auto-generated SVG board visualization
├── pyproject.toml        # Package & script configuration
└── README.md             # Visual board display & project documentation
```

---

## 🧪 Testing

Run the automated test suite with `pytest`:
```bash
python3 -m pytest
```

---

## 📜 License
MIT License.
