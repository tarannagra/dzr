from rich.panel import Panel
from rich.console import Console

console = Console()
panel = Panel.fit(
    "THIS IS THE CONTENT",
    title="TITLE ON THE TOP OF THE PANEL",
    subtitle="SUBTITLE ON THE BOTTOM OF THE PANEL"
)
console.print(panel)