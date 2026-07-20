import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional
import click
import chess
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
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
@click.option("--vs-ai", is_flag=True, help="Automatically trigger AI countermove after your move.")
@click.option("--engine", default="minimax", type=click.Choice(["minimax", "stockfish", "auto"]), help="AI engine choice")
def move(move_str: str, vs_ai: bool, engine: str):
    """Make a move via Git commit (executes git commit -m 'move: <MOVE>')."""
    commit_msg = f"move: {move_str}"
    res = subprocess.run(["git", "commit", "--allow-empty", "-m", commit_msg], check=False)
    if res.returncode != 0:
        sys.exit(1)

    if vs_ai:
        engine_obj = GitChessEngine()
        if not engine_obj.board.is_game_over():
            from git_chess.ai import get_best_move
            ai_move_obj = get_best_move(engine_obj.board, depth=2, engine_type=engine)
            ai_san = engine_obj.board.san(ai_move_obj)
            console.print(f"[bold cyan]AI calculating countermove... playing {ai_san}[/bold cyan]")
            subprocess.run(["git", "commit", "--allow-empty", "-m", f"move: {ai_san} [AI]"], check=False)

@cli.command()
@click.option("--depth", default=2, type=int, help="Search depth for AI engine")
@click.option("--engine", default="minimax", type=click.Choice(["minimax", "stockfish", "auto"]), help="AI engine choice")
def ai_move(depth: int, engine: str):
    """Calculate and commit AI move for current turn."""
    engine_obj = GitChessEngine()
    if engine_obj.board.is_game_over():
        console.print("[yellow]Game is already over.[/yellow]")
        return

    from git_chess.ai import get_best_move
    move_obj = get_best_move(engine_obj.board, depth=depth, engine_type=engine)
    san_move = engine_obj.board.san(move_obj)
    
    console.print(f"[bold cyan]AI playing move: {san_move}[/bold cyan]")
    res = subprocess.run(["git", "commit", "--allow-empty", "-m", f"move: {san_move} [AI]"], check=False)
    if res.returncode != 0:
        sys.exit(1)

@cli.command()
def reset():
    """Reset board state to initial starting position."""
    # Commit reset marker so history replay starts fresh from here
    subprocess.run(["git", "commit", "--allow-empty", "--no-verify", "-m", "reset: game"], check=False)
    engine = GitChessEngine()
    engine.reset_state()
    engine.update_readme()
    subprocess.run(["git", "add", "board.fen", "board.svg", "README.md"], check=False)
    subprocess.run(["git", "commit", "--amend", "--no-edit", "--no-verify"], check=False)
    console.print("[bold green]Board reset to initial position and committed.[/bold green]")

@cli.command()
def moves():
    """List available legal moves in a styled table."""
    engine = GitChessEngine()
    legal_moves = list(engine.board.legal_moves)
    
    table = Table(title=f"Legal Moves ({len(legal_moves)})", show_header=True, header_style="bold magenta")
    table.add_column("SAN", style="cyan")
    table.add_column("UCI", style="green")
    table.add_column("Piece", style="yellow")

    for m in legal_moves:
        san = engine.board.san(m)
        uci = m.uci()
        piece = engine.board.piece_at(m.from_square)
        piece_name = piece.symbol() if piece else ""
        table.add_row(san, uci, piece_name)

    console.print(table)

@cli.command()
@click.option("--vs-ai", is_flag=True, help="Play interactively against AI opponent")
def play(vs_ai: bool):
    """Interactive TUI to play chess move by move."""
    engine = GitChessEngine()
    
    while not engine.board.is_game_over():
        side = "White" if engine.board.turn == chess.WHITE else "Black"
        console.print(f"\n[bold green]GitChess Interactive Mode[/bold green] | Active Turn: [bold cyan]{side}[/bold cyan]")
        console.print(engine.render_unicode() + "\n")
        
        legal_moves = [engine.board.san(m) for m in engine.board.legal_moves]
        if not legal_moves:
            break

        table = Table(title="Available Legal Moves", show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim")
        table.add_column("SAN Move", style="cyan")

        for idx, san in enumerate(legal_moves, 1):
            table.add_row(str(idx), san)

        console.print(table)
        choice = click.prompt("Select move number (or type SAN move / 'q' to quit)", type=str)
        
        if choice.strip().lower() == "q":
            console.print("[yellow]Exited interactive play.[/yellow]")
            return

        selected_move = ""
        if choice.isdigit() and 1 <= int(choice) <= len(legal_moves):
            selected_move = legal_moves[int(choice) - 1]
        else:
            selected_move = choice.strip()

        res = subprocess.run(["git", "commit", "--allow-empty", "-m", f"move: {selected_move}"], check=False)
        if res.returncode == 0:
            if vs_ai:
                engine = GitChessEngine()
                if not engine.board.is_game_over():
                    from git_chess.ai import get_best_move
                    ai_move_obj = get_best_move(engine.board, depth=2)
                    ai_san = engine.board.san(ai_move_obj)
                    console.print(f"[bold cyan]AI calculating countermove... playing {ai_san}[/bold cyan]")
                    subprocess.run(["git", "commit", "--allow-empty", "-m", f"move: {ai_san} [AI]"], check=False)
            engine = GitChessEngine()
        else:
            console.print("[bold red]Invalid selection. Try again.[/bold red]")

    console.print("[bold red]Game Over![/bold red]")

@cli.command(name="log")
def show_log():
    """Display game move history from Git commit log."""
    res = subprocess.run(
        ["git", "log", "--grep=^move:", "--pretty=format:%h %an: %s"],
        capture_output=True,
        text=True,
        check=False
    )
    if not res.stdout.strip():
        console.print("[yellow]No moves recorded in Git commit history yet.[/yellow]")
        return
        
    console.print("[bold green]GitChess Move History[/bold green]")
    lines = res.stdout.strip().splitlines()
    for idx, line in enumerate(reversed(lines), 1):
        console.print(f"{idx}. {line}")

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

    if "[" in candidate:
        candidate = candidate.split("[")[0].strip()

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
@click.option("--fmt", default="svg", type=click.Choice(["svg", "html"]), help="Export format (svg or html)")
@click.option("--output", default=None, help="Output file path")
def export(fmt: str, output: Optional[str]):
    """Export current board state as SVG image or standalone HTML page."""
    engine = GitChessEngine()
    repo_root = get_repo_root()
    
    if fmt == "svg":
        from git_chess.visualization import generate_board_svg
        data = generate_board_svg(engine.board)
        out_path = Path(output) if output else repo_root / "board.svg"
    else:
        from git_chess.visualization import generate_board_html
        data = generate_board_html(engine.board)
        out_path = Path(output) if output else repo_root / "board.html"

    out_path.write_text(data)
    console.print(f"[bold green]Exported board to {out_path}[/bold green]")

@cli.command()
def view():
    """Open board HTML viewer in default browser."""
    import webbrowser
    engine = GitChessEngine()
    repo_root = get_repo_root()
    from git_chess.visualization import generate_board_html
    
    html_path = repo_root / "board.html"
    html_path.write_text(generate_board_html(engine.board))
    webbrowser.open(f"file://{html_path.resolve()}")
    console.print(f"[bold green]Opened viewer at {html_path.resolve()}[/bold green]")

@cli.command()
def update_readme():
    """Update README board visualization and board.svg."""
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
