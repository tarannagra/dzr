import os
import json

from typing import Union
from datetime import datetime

from lib.dzr import Dzr
from lib.ss import SmartSort
from lib.design import Design

from rich.table import Table
from rich.console import Console
from rapidfuzz import process, fuzz

class Main:
    def __init__(
            self, 
            song_file: str = "songs.txt", 
            bitrate: str = "FLAC",
            music_dir: str = "./music/"
        ) -> None:
        self.songs_file = song_file
        self.music_dir = music_dir
        self.bitrate = bitrate
        self.timeout = 30
        self.config_data = ""
        self.console = Console()
        self.dzr = Dzr(bitrate=self.bitrate, timeout=self.timeout)
        self.ss = SmartSort(music_dir=self.music_dir)

        self.links = []
        # there will be an equal number of links as there are titles
        self.titles = []

        self.invalid_arl_string = "[red]Invalid ARL. Change it.[reset]"

        self.clear = lambda: os.system('cls' if os.name == 'nt' else 'clear')

        self.__get_config()
    
    def __get_config(self) -> dict[str, str]:
        """
        !! To only be ran on initialisation of the object. !!
        Very simply appends the contents of `self.config_data`.

        Args:
            None

        Returns:
            dict[str, str]: Returns the contents.
        """
        with open('./config/config.json', 'r') as f:
            self.config_data = json.load(f)
        return self.config_data
    
    def __get_value_of(self, option: str, display: bool = True) -> Union[bool, str]:
        """
        Very simply returns the given option 
        from the available data (`self.config_data`) (with optional printing)

        Args:
            option (str): The option to display out from `self.config_data`
            display (bool): Default is True. If True then print it out using colouring.

        Returns:
            str: the plain value | printed out value with style
        """
        result = self.config_data["tags"][option]
        if display:
            # if result is bool and True then green
            if type(result) is bool and result:
                return f"[b green]{result}[reset]"
            # if result is bool but False, then red
            elif type(result) is bool and not result:
                return f"[b red]{result}[reset]"
            elif type(result) is str and result == "default":
                return f"[b white]{result}[reset]"
        # and finally, if display == False, display normally
        return result

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
    
        # INFO: needs to be re-worked. shows the title, but SHOULD say something else if downloading an album
        prompt = f" {title}"
        with self.console.status(initial_prompt + prompt, spinner="dots") as status:
            out = self.dzr.download(song_link=link)
        status.stop()
        if out:
            self.console.print(f"[green]Downloaded{prompt}[reset]")
            return
        self.console.print(self.invalid_arl_string)
    
    def __best_match(self, query: str, songs: list[str]) -> str:
        """ 
        Simple function to return the best match from the query and the given list of songs/albums.

        Args:
            query (str): The query (which has also been passed into the search function).
            songs (list[str]): The list of songs (gathered by said search function).
        
        Returns:
            str: The name of the track that best matches.
        """
        return process.extract(query, songs, scorer=fuzz.WRatio, limit=1)
    
    def search_query(self, query: str) -> str:
        results = self.dzr.search_query(query=query)
        if len(results) == 0:
            self.console.print(f"Nothing found for [bold red]{query}[reset]")
            return
        
        # could be the SAME song name (some are identicial), but different link, so key => link and value => title
        info = {}

        links = []

        table = Table(title="Choose your option:")
        if "album" not in query:
            placeholder = "Tracks"
        else:
            placeholder = "Albums"
        table.add_column(f"[u]Available {placeholder}[/u]", justify="left")

        # determine the best match using `rapidfuzz` then highlight it from the crowd
        if "album" not in query:
            song_list = [f"{result['artist']['name']} - {result['title']}" for result in results]
            best_match = self.__best_match(query=query, songs=song_list)[0][0]
        else:
            album_list = [f"{result['artist']['name']} - {result['album']['title']}" for result in results]
            best_match = self.__best_match(query=query, songs=album_list)[0][0]

        for index, result in enumerate(results, start=1):
            if "album" not in query:
                track_name = f"{result["artist"]["name"]} - {result["title"]}"
                if track_name == best_match:
                    # it will equal since the best match is the track name
                    track_name = f"[b green]{track_name}[reset]"
                links.append(result["link"])
                info.update({result["link"]: track_name})
                table.add_row(f"{index}. {track_name}")
            else:
                album_name = f"{result["artist"]["name"]} - {result["album"]["title"]}"
                album_url = f"https://www.deezer.com/en/album/{result["album"]["id"]}"
                if album_name == best_match:
                    album_name = f"[b green]{album_name}[reset]"
                links.append(album_url)
                info.update({album_url: album_name})
                table.add_row(f"{index}. {album_name}")
        table.add_section()
        table.add_row("[b red]99. Quit.[reset]")
        self.console.print(table)

        while True:
            try:
                choice = int(self.console.input("[b green](choice) ➜[/b green] "))
                if 1 <= choice <= len(links):
                    # chosen choice.
                    decided = links[choice - 1]
                    title = info[decided]
                    break
                elif choice == 99:
                    self.console.print("[b red]Aborted![reset]")
                    return
                else:
                    self.console.print("[yellow]Hey! Enter a valid number listed above!")
            
            except ValueError:
                self.console.print("[b red]You need to enter a valid number.[reset]")
        
        with self.console.status(f"Downloading '{title}'", spinner="dots") as status:
            out = self.dzr.download(song_link=decided)
        status.stop()
        if out:
            self.console.print(f"[green]Downloaded '{title}'![reset]")
            return
        self.console.print(self.invalid_arl_string)

    def set_arl(self, arl: str) -> bool:
        """
        Changes the ARL.

        Args:
            arl (str): The ARL to change it to.
        
        Returns:
            bool: Checks if the ARL has been set.
        """
        with open('./config/.arl', 'w') as f:
            f.write(arl)
        return arl == self.get_arl()
    
    def get_arl(self) -> str:
        """
        Returns the set ARL 

        Args:
            None

        Returns:
            str: The ARL.
        """
        with open("./config/.arl", 'r') as f:
            arl = f.read().strip()
        
        return arl
    
    def settings(self, option: str, value: bool) -> None:
        contents = self.config_data

        # TODO: handle other inputs instead of singling out bool
        contents["tags"][option] = value
        with open("./config/config.json", 'w') as f:
            f.write(json.dumps(contents, indent=2))
            self.console.print(f"[b green]Successfully[reset] set {option} ➜ {f"[b green] {value}" if value else f"[b red] {value}"}")
        
    def __get_days(self, end_date: str) -> str:
        """
        Returns the days in difference between DAYS_END and current days

        Args:
            end_date (datetime): END_DATE

        Returns:
            str: Days difference (int) since `rich.Table` requires it in str
        """
        try:
            curr_date = datetime.now()
            new_date = datetime.strptime(end_date, "%d-%m-%Y")
            return str((new_date - curr_date).days)
        except ValueError:
            return "N/A"

    def main(self) -> None:
        """
        `main` function of class `Main()`.
        This is used to allow user input and allow the user to navigate through the app!
        """
        self.clear()
        self.console.print(Design.main_menu())

        # this may be messy, but i will try and make it as optimal as possible!
        while True:
            check = self.console.input("[b green](menu) ➜[/b green] ").lower()
            match check:
                case "help" | "?" | "ls" | "hh":
                    self.console.print(Design.better_help_menu())
                case "q" | "exit" | "quit":
                    return
                
                case "sch" | "search":
                    self.search()
                
                case "ss":
                    query = self.console.input("[b blue](query) ➜[reset] ").lower()
                    if query == "q" or query == "exit":
                        continue
                    self.search_query(query=query)

                case "dr" | "direct":
                    link = self.console.input("[b blue](link) ➜[reset] ").lower()
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
                    self.console.print(f"[yellow]Purging {self.music_dir}*")
                    self.dzr.clean()
               
                case "clear":
                    self.clear()
                
                case "set timeout":
                    timeout = self.console.input("[b blue](timeout) ➜[reset] ")
                    if timeout == "q":
                        continue
                    try:
                        timeout = int(timeout)
                        self.timeout = timeout
                        self.console.print(f"[b green]Set timeout to {self.timeout}")
                    except ValueError:
                        self.console.print(f"[b red]Enter a number, not '{timeout}'!")
                        return
                
                case "set arl" | "arl set":
                    arl = self.console.input("[b blue](arl) ➜[reset] ")
                    if not len(arl) == 192:
                        self.console.print("Incorrect ARL length!")
                        continue
                    with self.console.status("Checking ARL...") as _:
                        if self.dzr.account_info(check_only=True):
                            self.console.print("ARL [b green]valid[reset]!")
                        else:
                            self.console.print("ARL is [b red]not valid[reset]!")
                    check = self.set_arl(arl=arl)
                    if check:
                        self.console.print("ARL set [b green]successfully[reset]!")
                    else:
                        self.console.print("Could [b red]not[reset] set the ARL!")
                
                case "arl info":
                    info = self.dzr.account_info()
                    if isinstance(info, str):
                        # !! ONLY returns str if INVALID ARL
                        self.console.print("[b red]ARL is invalid![reset]")
                        continue
                    table = Table(title="Account Information.")
                    table.add_column("Option", justify="left")
                    table.add_column("Value", justify="left")
                    table.add_row("First Name", self.dzr.firstname)
                    table.add_row("Last Name", self.dzr.lastname)
                    table.add_row("Email", self.dzr.email)
                    table.add_row("Country Code", self.dzr.country)
                    table.add_section()
                    table.add_row("Date Start", self.dzr.date_start)
                    table.add_row("Date End", self.dzr.date_end)
                    table.add_row("Days Left", self.__get_days(end_date=self.dzr.date_end))
                    table.add_row("Lossless Active?", "[b green]Yes[reset]" if self.dzr.is_lossless else "[b red]No[reset]")
                    self.console.print(table)
                    if self.dzr.date_start == "0000-00-00" or self.dzr.date_end == "0000-00-00":
                        self.console.print("Consider [b yellow]changing[reset] your ARL!")

                case "get arl":
                    arl = self.get_arl()
                    # trunicate the arl, it's long and don't want it fully shown for security
                    arl = arl[:20] + "..." + arl[172:192]
                    self.console.print(f"Find part of your ARL here:\n[b u white]{arl}[reset]")

                case "settings" | "set":
                    while True:
                        option = self.console.input("[b cyan](option) ➜[reset] ").lower()
                        if option == "q": 
                            break
                        elif option == "help" or option == "?" or option == "all":
                            table = Table(title="All currently set options.")
                            table.add_column("Option", justify="left")
                            table.add_column("Value", justify="left")
                            for key in self.config_data["tags"]:
                                table.add_row(key, self.__get_value_of(key))
                            self.console.print(table)
                        else:
                            # INFO: extra search to see if option is in the keys or not
                            for key in self.config_data["tags"]:
                                if option == key:
                                    self.console.print(f"Option is currently set to: {self.__get_value_of(key)}.")
                                    new_value = self.console.input("[b cyan](new) ➜[reset] ").strip().lower()
                                    if new_value == "q":
                                        self.console.print("[b red]Aborted![reset]")
                                        break
                                    elif new_value == "true":
                                        new_value = True
                                    elif new_value == "false":
                                        new_value = False
                                    self.settings(option=key, value=new_value)

                case _:
                    pass


if __name__ == '__main__':
    Main(bitrate="FLAC").main()
