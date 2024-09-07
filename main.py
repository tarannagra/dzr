import os

from lib.dzr import Dzr
from lib.ss import SmartSort
from lib.design import Design

from rich.table import Table
from rich.console import Console


class Main:
    def __init__(self, song_file: str = "songs.txt", bitrate: str = "FLAC") -> None:
        self.songs_file = song_file
        self.console = Console()
        self.bitrate = bitrate
        self.dzr = Dzr(bitrate=self.bitrate)
        self.ss = SmartSort(music_dir="./music/")

        self.links = []
        # there will be an equal number of links as there are titles
        self.titles = []

        self.clear = lambda: os.system('cls' if os.name == 'nt' else 'clear')
    
    def search(self) -> list[str]:
        self.links = []
        self.could_not_find = []
        with self.console.status("Searching songs...", spinner="dots") as status:
            with open("songs.txt", 'r') as f:
                songs = f.read().splitlines(keepends=False)
            if len(songs) == 0:
                status.stop()
                self.console.print("[red]There are no songs in the file!")
                return
            for song in songs:
                if "https://www.deezer.com" in song or "https://deezer.com" in song:
                    status.update(f"Found {song} in songs.txt!")
                    # assume if the user adds a link to songs.txt then
                    # automatically add it to the array of found links
                    self.links.append(song)
                else:
                    search, title = self.dzr.search(query=song)
                    if search is None:
                        status.update(f"[red]Could not find {song}!")
                        self.could_not_find.append(song)
                    else:
                        status.update(f"Found: {title}")
                        self.titles.append(title)
                        self.links.append(search)
            status.stop()
        if len(self.links) == 1:
            extra_detail = f"There is {len(self.links)} song available to download!"
        else:
            extra_detail = f"There are {len(self.links)} songs available to download!"
        self.console.print(f"[light_green]{extra_detail}")
        with open('could_not_find.txt', 'w') as f:
            for line in self.could_not_find:
                f.write(f"{line}\n")
        return self.links
    
    def download(self) -> None:
        """ 
        Downloads the songs!
        """
        local_count = 0
        if len(self.links) == 0:
            self.console.print("[yellow]Please run 'sch' to search the links then download!")
            return
        with self.console.status("[yellow]Downloading[/yellow]", spinner="dots") as status:
            for song in self.links:
                local_count += 1
                if "album" in song:
                    status.update("[yellow]Downloading album. This may take some time.[/yellow]")
                else:
                    status.update(f"[light_green]Downloading song {local_count}/{len(self.links)}[/light_green]")
                
                try:
                    self.dzr.download(song_link=song)
                except UnicodeEncodeError:
                    status.update(f"[red]Could not download: {song}[/red]")
            status.stop()
            # remove the links and have the user search again for new ones
            self.links.clear()
            
        self.console.print(f"[green]Downloaded [b u]{self.__get_total()}[/b u] songs in total![/green]")
    
    def __get_total(self) -> int:
        """Returns the amount of songs in the music directory."""
        amount = 0
        for _, _, files in os.walk("music"):
            for file in files:
                if file.endswith(f".{self.bitrate.lower()}"):
                    amount += 1
        return amount

    def direct_download(self, link: str) -> None:
        initial_prompt = "Downloading"
        title = ""
        prompt = ""
        if "https://www.deezer.com" not in link:
            # then assume it's a query and search, then return the link for download
            with self.console.status(f"Searching {link}...", spinner="dots") as status:
                result = self.dzr.search(query=link)
                if result is None:
                    self.console.print(f"Could [red]not[/red] find a match for [b]{link}[/b]")
                    return
                link, title = result
                status.update(f"Found a match for {link}!")
        if "album" in link:
            prompt += " album"
        elif title:
            prompt += f" {title}"
        else:
            prompt += " the song"
        with self.console.status(initial_prompt + prompt, spinner="dots") as status:
            self.dzr.download(song_link=link)
            status.update("Downloaded!")
        status.stop()
        self.console.print(f"[green]Downloaded{prompt}[reset]")
    
    def search_query(self, query: str) -> str:
        results = self.dzr.search_query(query=query)
        if len(results) == 0:
            self.console.print(f"Nothing found for [bold red]{query}[reset]")
            return
        links = []
        table = Table(title="Choose your option:")
        table.add_column("[u]Available Tracks[/u]", justify="left")

        for index, result in enumerate(results, start=1):
            track_name = f"{result["artist"]["name"]} - {result["title"]}"
            links.append(result["link"])
            table.add_row(f"{index}. {track_name}")
        table.add_section()
        table.add_row("[b red]99. Quit.[reset]")
        self.console.print(table)
        
        while True:
            try:
                choice = int(self.console.input("[b u green]choice::ss::[/b u green] "))
                if 1 <= choice <= len(links):
                    # chosen choice. 
                    decided = links[choice - 1]
                    break
                elif choice == 99:
                    self.console.print("[b red]Aborted![reset]")
                    return
                else:
                    self.console.print("[yellow]Hey! Enter a valid number listed above!")
            
            except ValueError:
                self.console.print("[b red]You need to enter a valid number.[reset]")
        
        with self.console.status("Downloading", spinner="dots") as status:
            self.dzr.download(song_link=decided)
            status.update("Downloaded!")
        status.stop()
        self.console.print("[green]Downloaded![reset]")


    def set_arl(self, arl: str) -> bool:
        with open('./config/.arl', 'w') as f:
            f.write(arl)
        if arl == self.get_arl():
            return True
        return False
    
    def get_arl(self) -> str:
        """Simply returns the ARL"""
        with open("./config/.arl", 'r') as f:
            arl = f.read().strip()
        
        return arl

    def main(self) -> None:
        """
        `main` function of class `Main()`.
        This is used to allow user input and allow the user to navigate through the app!
        """
        self.clear()
        self.console.print(Design.main_menu())

        # this may be messy, but i will try and make it as optimal as possible!
        while True:
            check = self.console.input("[b u green]dzrDL::Input::[/b u green] ").lower()
            match check:
                case "help" | "?"| "ls" | "hh":
                    self.console.print(Design.better_help_menu())
                case "q" | "exit" | "quit":
                    return
                
                case "sch" | "search":
                    self.search()
                
                case "ss":
                    query = self.console.input("[b u blue]ss::query::[reset] ").lower()
                    if query == "q" or query == "exit":
                        continue
                    self.search_query(query=query)

                case "dr" | "direct":
                    link = self.console.input("[b u blue]direct::link::[reset] ").lower()
                    if link == "q" or link == "exit":
                        continue
                    self.direct_download(link=link)
               
                case "dl" | "download":
                    self.download()
               
                case "srt" | "sort":
                    self.ss.sort()
               
                case "init":
                    self.console.print("Downloading initial file.")
                    self.dzr.init()
               
                case "clean" | "purge":
                    self.console.print("[yellow]Purging ./music/*")
                    self.dzr.clean()
               
                case "clear":
                    self.clear()
                
                case "set arl":
                    arl = self.console.input("Enter your ARL: ")
                    if not len(arl) == 192:
                        self.console.print("Incorrect ARL length!")
                        continue
                    check = self.set_arl(arl=arl)
                    if check:
                        self.console.print("ARL set [b green]successfully[reset]!")
                    else:
                        self.console.print("Could [b red]not[reset] set the ARL!")
 
                case "get arl":
                    arl = self.get_arl()
                    # trunicate the arl, it's long and don't want it fully shown for security
                    arl = arl[:20] + "..." + arl[172:192]
                    self.console.print(f"Find part of your ARL here:\n[b u white]{arl}[reset]")
               
                case _:
                    pass


if __name__ == '__main__':
    Main(bitrate="FLAC").main()
