from rich.console import Console
from rich.table import Table
import time
import os
import platform


def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def show_progress(get_progress):
    console = Console()
    while True:
        clear_screen()
        progress = get_progress()

        table = Table(title="Прогрес завантаження")
        table.add_column("Метрика", justify="left", style="cyan")
        table.add_column("Поточне", justify="right", style="green")
        table.add_column("Загальне", justify="right", style="magenta")

        table.add_row("Конференції",
                      str(progress['conversations_done']),
                      str(progress['conversations_total']))
        table.add_row("Фото",
                      str(progress['photos_done']),
                      str(progress['photos_total']))
        table.add_row("Відео",
                      str(progress['videos_done']),
                      str(progress['videos_total']))

        console.print(table)
        time.sleep(1)
