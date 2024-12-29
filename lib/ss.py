"""
ss -> Smart Sort for sorting the media files based on their artist name & album name.
"""

import os
import re
import shutil

from tinytag import TinyTag
from rich.console import Console

class SmartSort:
    def __init__(self, music_dir: str) -> None:
        self.music_dir = music_dir

        self.console = Console()

    def get_artist(self, filename: str) -> str:
        try:
            return TinyTag.get(filename).artist
        except PermissionError:
            # if filename isnt a file name but is a folder instead
            return None

    def create_folder(self, foldername: str) -> bool:
        """Make a folder based on the artist and return if made or determine if made already."""
        try:
            os.mkdir(foldername)
        except FileExistsError:
            pass
        return os.path.isdir(foldername)

    def sort(self) -> None:
        songs = os.listdir(self.music_dir)
        os.chdir(self.music_dir)
        
        with self.console.status("[yellow]Moving songs...", spinner="line") as status:
            for song in songs:
                # INFO: perform the check here if "song" is a dir and if it is, match with regex
                # INFO: if it is, then create the folder & then move it into the newly made folder
                # check = re.search(r"\S+-\S+", song)
                check = re.search(r"(.+?)\s*-\s*", song)
                if check:
                    artist = check.group(1).strip()
                    if len(artist) == 1:
                        # a bug with the above regex which doesnt match n-aa artists
                        # hacky workaround for checking the song's artist afterwards
                        artist = re.search(r"\S+-\S+", song).group().split()
                    # INFO: this gets the artist name and knows that this object is an album
                    self.create_folder(artist)
                    shutil.move(song, artist)
                    status.update(f"[green]Moved {song} into {artist}")
                else:
                    artist = self.get_artist(song)
                    if artist is not None:
                        self.create_folder(artist)
                        shutil.move(song, artist)
                        status.update(f"[green]Moved {song} to {artist}!")
            status.stop()
        os.chdir("../")
        self.console.print("[green]Moved all songs into their respective folder!")
    
if __name__ == '__main__':
    ss = SmartSort(
        music_dir="../music/",
    )
    ss.get_artist_from_album()
