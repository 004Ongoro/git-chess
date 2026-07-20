# GitChess Hooks

This directory contains Git hooks for enforcing chess rules:
- `pre-commit`: Validates move legality from commit message or staged changes.
- `prepare-commit-msg`: Offers interactive or formatted move commit messages.
- `post-commit`: Updates FEN state and auto-generates README visualization.
