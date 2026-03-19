import os
import sys
import typer
import requests
import json
import logging
from rich.console import Console
from rich.table import Table
from typing import Optional

# Ensure the root directory is on the path so we can import shared
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from shared.constants import EKMAN_EMOTIONS, get_emotion_display_name, get_valid_emotions

# Configure logging
logging.basicConfig(
    filename="cli.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = typer.Typer(help="Netrunner Emotion Tracker CLI")
console = Console()

API_URL = "http://127.0.0.1:8000"

def get_valid_emotion(emotion_input: str) -> Optional[str]:
    emotion_input = emotion_input.lower()

    if emotion_input in EKMAN_EMOTIONS:
        return emotion_input

    for key, (emoji, es_name, en_name) in EKMAN_EMOTIONS.items():
        if emotion_input == emoji or emotion_input == es_name.lower() or emotion_input == en_name.lower():
            return key

    return None

def format_prompt() -> str:
    parts = []
    for key, (emoji, es_name, en_name) in EKMAN_EMOTIONS.items():
        parts.append(f"{emoji} {es_name} ({key})")
    return "Emoción (" + ", ".join(parts) + ")"

@app.command()
def log(
    emotion: str = typer.Option(None, prompt=format_prompt()),
    level: int = typer.Option(None, prompt="Nivel (1-5)", min=1, max=5)
):
    """
    Registra una nueva emoción.
    """
    valid_emotion = get_valid_emotion(emotion)

    while not valid_emotion:
        logger.warning("Invalid emotion entered: %s", emotion)
        console.print("[red]Emoción no válida. Usa una de las permitidas, su emoji o nombre.[/red]")
        emotion = typer.prompt("Emoción")
        valid_emotion = get_valid_emotion(emotion)

    logger.info("Registering emotion: %s, level: %d", valid_emotion, level)
    try:
        response = requests.post(f"{API_URL}/log", json={"emotion": valid_emotion, "level": level})
        response.raise_for_status()
        logger.info("Emotion successfully registered via CLI")
        display_name = get_emotion_display_name(valid_emotion)
        console.print(f"[green]¡Emoción '{display_name}' con nivel {level} registrada con éxito![/green]")
    except requests.exceptions.RequestException as e:
        logger.error("Error connecting to server: %s", e)
        console.print(f"[bold red]Error al conectar con el servidor:[/bold red] {e}")


@app.command()
def history(
    as_json: bool = typer.Option(False, "--json", help="Muestra la salida en formato JSON bruto")
):
    """
    Muestra el historial de emociones registradas.
    """
    logger.info("Fetching history from CLI")
    try:
        response = requests.get(f"{API_URL}/logs")
        response.raise_for_status()
        logs = response.json()
        logger.info("Successfully fetched %d logs", len(logs))

        if as_json:
            console.print(json.dumps(logs, indent=2))
            return

        if not logs:
            console.print("[yellow]No hay emociones registradas aún.[/yellow]")
            return

        table = Table(title="Historial de Emociones")

        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Emoción", style="magenta")
        table.add_column("Nivel", justify="right", style="green")
        table.add_column("Fecha/Hora", style="blue")

        for entry in logs:
            table.add_row(
                str(entry["id"]),
                entry["emotion"],
                str(entry["level"]),
                entry["timestamp"]
            )

        console.print(table)

    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error al conectar con el servidor:[/bold red] {e}")


if __name__ == "__main__":
    app()
