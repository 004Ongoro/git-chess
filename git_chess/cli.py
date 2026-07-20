import sys
import shutil
import subprocess
from pathlib import Path
import click
import chess
from rich.console import Console
from git_chess.engine import GitChessEngine
from git_chess.utils import get_repo_root

console = Console()

@click.group()
def cli():
    """GitChess: Play chess using Git commands and hooks."""
    pass

@cli.command()
def status():
    """Show current board state and turn info."""
    engine = GitChessEngine()
    side = "White" if engine.board.turn == chess.WHITE else "Black"
    console.print(f"[bold green]GitChess Board[/bold green] | Active Turn: [bold cyan]{side}[/bold cyan]\n")
    console.print(engine.render_ascii() + "\n")
    
    if engine.board.is_checkmate():
        console.print("[bold red]CHECKMATE![/bold red]")
    elif engine.board.is_check():
        console.print("[bold yellow]CHECK![/bold yellow]")

@cli.command()
@click.argument("move_str")
def move(move_str: str):
    """Attempt a chess move in UCI (e2e4) or SAN (e4) format."""
    engine = GitChessEngine()
    success, message = engine.apply_move(move_str)
    if success:
        engine.update_readme()
        console.print(f"[bold green]{message}[/bold green]")
    else:
        console.print(f"[bold red]{message}[/bold red]")
        sys.exit(1)

@cli.command()
def reset():
    """Reset board state to initial starting position."""
    engine = GitChessEngine()
    engine.reset_state()
    engine.update_readme()
    console.print("[bold green]Board reset to initial position.[/bold green]")

@cli.command()
def moves():
    """List available legal moves."""
    engine = GitChessEngine()
    legal_moves = engine.get_legal_moves()
    console.print(f"[bold cyan]Legal Moves ({len(legal_moves)}):[/bold cyan]")
    console.print(", ".join(legal_moves))

@cli.command()
@click.argument("msg_file", type=click.Path(exists=True))
def validate_commit_msg(msg_file: str):
    """Git commit-msg hook handler to validate move in commit message."""
    raw_msg = Path(msg_file).read_text().strip()
    first_line = raw_msg.splitlines()[0] if raw_msg else ""
    
    # Extract move from formats: "move: e4", "Move e2e4", "e4", "move e4"
    candidate = first_line.strip()
    if candidate.lower().startswith("move:"):
        candidate = candidate[5:].strip()
    elif candidate.lower().startswith("move "):
        candidate = candidate[5:].strip()

    engine = GitChessEngine()
    
    # Check if candidate is a chess move
    move_obj = engine.parse_move(candidate)
    if not move_obj:
        # If it wasn't prefixed with 'move:' and isn't a chess move, allow non-move commits (e.g. repo maintenance)
        if not first_line.lower().startswith("move"):
            sys.exit(0)
            
        console.print(f"[bold red]GitChess Commit Rejected:[/bold red] '{candidate}' is not a legal move.")
        legal_moves = engine.get_legal_moves()
        console.print(f"[yellow]Legal moves:[/yellow] {', '.join(legal_moves[:10])}...")
        sys.exit(1)

    # Valid move: apply move and stage updated board.fen
    success, message = engine.apply_move(candidate)
    if success:
        repo_root = get_repo_root()
        subprocess.run(["git", "add", str(repo_root / "board.fen")], check=False)
        console.print(f"[bold green]GitChess Move Accepted:[/bold green] {message}")
        sys.exit(0)
    else:
        console.print(f"[bold red]GitChess Commit Rejected:[/bold red] {message}")
        sys.exit(1)

@cli.command()
def update_readme():
    """Update README board visualization."""
    engine = GitChessEngine()
    engine.update_readme()

@cli.command()
def init():
    """Install Git hooks into current repository."""
    repo_root = get_repo_root()
    git_hooks_dir = repo_root / ".git" / "hooks"
    source_hooks_dir = repo_root / "hooks"
    
    if not git_hooks_dir.exists():
        console.print("[bold red]Error: .git/hooks directory not found. Initialize git first.[/bold red]")
        sys.exit(1)

    for hook in ["commit-msg", "post-commit", "prepare-commit-msg"]:
        src = source_hooks_dir / hook
        dst = git_hooks_dir / hook
        if src.exists():
            shutil.copy(src, dst)
            dst.chmod(0o755)
            console.print(f"Installed hook: [bold cyan]{hook}[/bold cyan]")
    
    console.print("[bold green]GitChess hooks successfully installed![/bold green]")

def main():
    cli()

if __name__ == "__main__":
    main()
