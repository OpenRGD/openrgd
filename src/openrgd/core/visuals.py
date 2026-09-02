import os
import random
import sys
import time
from datetime import datetime

from rich.align import Align
from rich.panel import Panel
from rich.progress import track

from .config import QUOTES, console, state


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def log(msg: str, level: str = "INFO", delay: float = 0.05):
    """Smart logger with deterministic plain-text quiet-mode errors."""

    if state["quiet"]:
        if level == "ERROR":
            print(f"ERROR: {msg}", file=sys.stderr)
        return

    if level == "DEBUG" and not state["verbose"]:
        return

    if state["cinematic"]:
        time.sleep(delay)

    timestamp = datetime.now().strftime("%H:%M:%S")
    icons = {
        "SUCCESS": "✅",
        "WARN": "⚠️",
        "ERROR": "❌",
        "SYSTEM": "🖥️",
        "AI": "🤖",
        "DEBUG": "🔍",
    }
    styles = {
        "SUCCESS": "bold green",
        "WARN": "yellow",
        "ERROR": "bold red",
        "SYSTEM": "bold cyan",
        "AI": "italic purple",
        "DEBUG": "dim italic",
    }

    icon = icons.get(level, "🔹")
    style = styles.get(level, "dim")
    console.print(f"[dim]{timestamp}[/] {icon} [{style}]{msg}[/]")


def print_header():
    if state["quiet"]:
        return
    clear_screen()
    ascii_art = r"""
   ____                    ____  _____ ____  
  / __ \____  ___  ____   / __ \/ ___// __ \ 
 / / / / __ \/ _ \/ __ \ / /_/ / / __/ / / / 
/ /_/ / /_/ /  __/ / / // _, _/ /_/ / /_/ /  
\____/ .___/\___/_/ /_//_/ |_|\____/_____/   
    /_/                                      
    """
    console.print(
        Panel(
            Align.center(
                f"[bold red]{ascii_art}[/]\n"
                "[italic white]v0.1 - The Cognitive BIOS[/]"
            ),
            border_style="red",
            subtitle="[dim]Waking up...[/]",
        )
    )
    time.sleep(state["delay"])


def smart_track(sequence, description: str):
    if state["quiet"] or not state["cinematic"]:
        return sequence
    return track(sequence, description=description)
