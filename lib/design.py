""" 
Design.py 

Using Rich.Table for a prettier menu & a better fitting table in the terminal
"""

from rich.table import Table


class Design:

    @staticmethod
    def help_menu() -> str:
        """
        Returns the rendered help menu for dzrDL
        """

        des = """
        ╔══════════════════════════════════════════════════════╗
        ║ [b u green]dzrDL::Help[/b u green]                   [b u blue]Created by Taran Nagra[/b underline blue] ║
        ╠════════════╦══════════════╦══════════════════════════╣
        ║ [u]NAME[/u]       ║ [u]ALIAS[/u]        ║ [u]DESCRIPTION[/u]              ║
        ╠════════════╬══════════════╬══════════════════════════╣
        ║ sch        ║ search       ║ Attempts to search songs ║
        ║ dr         ║ direct       ║ Enter Deezer link        ║
        ║ dl         ║ download     ║ Downloads the songs!     ║
        ║ [cyan]srt[reset]        ║ [cyan]sort[reset]         ║ [cyan]Sorts songs by artists![reset]  ║
        ╠════════════╬══════════════╬══════════════════════════╣
        ║ [red]clean[/red]      ║ [red]purge[/red]        ║ [red]Purges the music folder![/red] ║
        ║ [yellow]quit[/yellow]       ║ [yellow]exit | q[/yellow]     ║ [yellow]Quits the application![/yellow]   ║
        ╚════════════╩══════════════╩══════════════════════════╝
        """
        return des
    
    @staticmethod
    def better_help_menu() -> Table:
        """ 
        Returns the better rendered help menu with help from `rich.table` :)
        """
        table = Table(title="[b u green]DZR-DL Help!")
        
        # table.show_footer = True

        table.add_column("[u]NAME")
        table.add_column("[u]ALIAS")
        table.add_column("[u]DESCRIPTION")

        # Individual commands seperated by:
        # NAME | ALIAS | DESCRIPTION
        table.add_row("search", "sch", "[Legacy] Search songs from the text file, 'songs.txt'.")
        table.add_row("download", "dl", "[Legacy] Download the songs. Must run 'search' before!")
        table.add_row("direct", "dr", "[Legacy] Directly download a song/album given the query or URL!")
        table.add_row("sort", "srt", "Sort the songs (& albums) by the artists.")
        table.add_row("ss", "N/A", "A better search to refine your query.")
        table.add_section()
        table.add_row("get arl", "N/A", "Returns part of the ARL")
        table.add_row("set arl", "N/A", "Enter a new ARL to set")
        table.add_row("arl info", "N/A", "Get the expiry time of the current ARL.")
        table.add_row("settings", "set | set help", "Fine tine your own experience.")
        table.add_section()
        table.add_row("[red]clean", "[red]purge", "[red]!! Removes EVERYTHING in your download location. !!")
        table.add_row("[yellow]quit", "[yellow]exit | q", "[yellow]Quits the application!")
        return table

    @staticmethod
    def main_menu() -> str:
        """
        Returns the rendered main menu for dzrDL
        """

        des = """
        [b light_green]
                ______  ______  ______     ______        
                |     \  ____/ |_____/ ___ |     \ |     
                |_____/ /_____ |    \_     |_____/ |_____[/b light_green]

                 "Saving the sounds, one rip at a time."
        """
        return des