"""arazzo-ai CLI."""

import typer
from rich import print
import typer
import uvicorn
from pathlib import Path
import subprocess
import signal
import os

app = typer.Typer()
server_process = None


def get_pid_file():
    return Path("oauth_server.pid")


def read_pid():
    pid_file = get_pid_file()
    if pid_file.exists():
        return int(pid_file.read_text())
    return None


def write_pid(pid: int):
    pid_file = get_pid_file()
    pid_file.write_text(str(pid))


def delete_pid_file():
    pid_file = get_pid_file()
    if pid_file.exists():
        pid_file.unlink()


@app.command()
def start():
    """Start the Example OAuth API server."""
    global server_process
    pid = read_pid()
    if pid:
        typer.echo(f"Server is already running with PID {pid}. Use 'stop' to stop it first.")
        return

    typer.echo("Starting the Example OAuth API server...")
    server_process = subprocess.Popen(
        ["uvicorn", "example_oauth_production_api:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    write_pid(server_process.pid)
    typer.echo(f"Server started with PID {server_process.pid}.")


@app.command()
def stop():
    """Stop the Example OAuth API server."""
    pid = read_pid()
    if not pid:
        typer.echo("Server is not running.")
        return

    typer.echo(f"Stopping server with PID {pid}...")
    try:
        os.kill(pid, signal.SIGTERM)
        typer.echo(f"Server with PID {pid} has been stopped.")
    except ProcessLookupError:
        typer.echo(f"Process with PID {pid} not found.")
    finally:
        delete_pid_file()


@app.command()
def restart():
    """Restart the Example OAuth API server."""
    typer.echo("Restarting the Example OAuth API server...")
    stop()
    start()


@app.command()
def status():
    """Check the status of the Example OAuth API server."""
    pid = read_pid()
    if pid:
        typer.echo(f"Server is running with PID {pid}.")
    else:
        typer.echo("Server is not running.")


if __name__ == "__main__":
    app()
