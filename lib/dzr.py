import os
import re

from datetime import datetime
from typing import Union, Optional
from subprocess import PIPE, Popen, TimeoutExpired

import requests
from bs4 import BeautifulSoup

class Dzr:
    """
    Deezer download class to search and download the songs.

    Args:
        bitrate (str): Defaults to "FLAC". Changes the bitrate to download the songs into.
    """
    def __init__(
        self,
        bitrate: str = "FLAC",
        music_dir: str = "./music/",
        timeout: int = 30
    ) -> None:
        self.session = requests.Session()
        self.bitrate = bitrate
        self.music_dir = music_dir
        self.timeout = timeout

        self.search_url = "https://api.deezer.com/search?q={}&output=json&output=json&version=js-v1.0.0"
        self.album_url = "https://www.deezer.com/en/album/{}"

        self.download_query = "deemix --portable {} --path " + self.music_dir + " --bitrate " + self.bitrate + " > NUL "

        # arl account specific for ease of access to each property
        self.date_start = None
        self.date_end = None
        self.is_lossless = False
        self.firstname = None
        self.lastname = None
        self.email = None
        self.country = None
        self.plan = None


    def clean(self) -> None:
        """
        Removes all media files from the music path and their respective file extension.
        
        Args:
            None
            
        Returns:
            None
        
        """
        os.system(f"rm -rf {self.music_dir}*")

    def search(self, query: str) -> tuple[str]:
        """
        Searches the Deezer API using the provided query and returns the first link found.

        Args:
            query (str): The search query in the format "%track% %artist% (optional "album" to signify to download album)".

        Returns:
            str: The Deezer link of the first search result.
            str: The title of the song/album to show which song/album is being downloaded.

        Raises:
            Exception: If the request to the Deezer API fails.
        """
        if "album" in query:
            album = True
        else:
            album = False
        r = self.session.get(
            url=self.search_url.format(query.replace("album", "").replace(" ", "%20"))
        )
        if r.status_code == 200:
            try:
                if album:
                    # when album specified, download all of the album instead of the individiual song
                    return (
                        self.album_url.format(r.json()["data"][0]["album"]["id"]),
                        r.json()["data"][0]["album"]["title"],
                    )
                return (
                    r.json()["data"][0]["link"],
                    r.json()["data"][0]["title"]
                ) # TODO: Find best match for query -> songname
            except (IndexError, KeyError):
                return None
        raise Exception(f"Failed to make a request: {r.status_code}")
    
    def search_query(self, query: str) -> list[str]:
        """
        Searches using the Deezer API but this time around, it will prompt the user if this result is the correct one. If it is, then return those properties of the title and link (or id). So, it will all be done here.
        
        Args: 
            query (str): Query of the search item
        
        Returns:
            str: The Deezer link of the first search result.
            str: The title of the song/album to show which song/album is being downloaded.

        Raises:
            Exception: If the request to the Deezer API fails.

        High likelyhood that the song IS within the top 10 results. So only return 10.
        """
        r = self.session.get(
            url=self.search_url.format(query.replace("album", "").replace(" ", "%20"))
        )
        if not r.status_code == 200:
            raise Exception(f"Failed to make a request: {r.status_code}")
        
        # slice the list and only show the 10 results
        result = r.json()["data"][0:10]
        
        return result
            
    def download(self, song_link: str) -> bool:
        """
        Downloads the song by the link using Deemix.

        Args:
            song_link (str): The given track link returned from `self.search()`.
        
        Returns:
            bool: If process.wait is found, reached then True | False
        """
        
        # TODO: refactor this into subprocess.run and check if "Paste here your arl" is in the output,
        # TODO: if so, then raise Exception OR return None. then in `download` calls, then handle for exceptions
        
        process = Popen(self.download_query.format(song_link).split(), stdout=PIPE, stdin=PIPE)
        try:
            process.wait(self.timeout)
            return True
        except TimeoutExpired:
            process.kill()
            return False

    def account_info(self, check_only: bool = False) -> Union[str, None, bool]:
        """
        Using the ARL, returns the account information available.

        Args:
            check_only (bool): Defaults to False. Used for checking only if the ARL is valid.
        
        Returns:
            None: Properties assorted correctly
            OR
            str: If ARL is invalid, which it will return "Invalid"
            OR
            bool: if check_only is True
        """
        with open("config/.arl") as f:
            cookies = {
                "arl": f.read().strip()
            }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/jxl,image/webp,image/png,image/svg+xml,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            "Content-Type": "type/plain;charset=UTF-8"
        }
        r = self.session.post(
            url="https://www.deezer.com/ajax/gw-light.php?method=deezer.getUserData&input=3&api_version=1.0&api_token=&cid=361312840",
            headers=headers,
            cookies=cookies
        )
        if r.status_code == 200:
            if check_only:
                return r.status_code == 200
            
            # assorting the account information into variables (easier)
            try:
                # dates
                self.date_start = self.__strip_date(date=r.json()["results"]["USER"]["TRY_AND_BUY"]["DATE_START"])
                self.date_end = self.__strip_date(date=r.json()["results"]["USER"]["TRY_AND_BUY"]["DATE_END"])

                self.plan = r.json()["results"]["USER"]["OFFER_NAME"]

                # is music x or y?
                self.is_lossless = r.json()["results"]["USER"]["OPTIONS"]["web_lossless"]
                
                # personal information
                self.firstname = r.json()["results"]["USER"]["FIRSTNAME"]
                self.lastname = r.json()["results"]["USER"]["LASTNAME"]
                self.email = r.json()["results"]["USER"]["EMAIL"]
                self.country = r.json()["results"]["COUNTRY"]
            except KeyError:
                self.date_start = "0000-00-00"
                self.date_end = "0000-00-00"

                self.is_lossless = "N/A"
                self.plan = "N/A"
                
                # personal information
                self.firstname = "N/A"
                self.lastname = "N/A"
                self.email = "N/A"
                self.country = "N/A"

            return None
        return "Invalid"
    
    def __strip_date(self, date: str) -> str:
        new_date = re.match("....-..-..", date).group(0)
        try:
            output = datetime.strftime(datetime.strptime(new_date, "%Y-%m-%d"), "%d-%m-%Y")
        except ValueError:
            output = "0000-00-00"
        return output
    
    def init(self) -> None:
        """Initialises the directory for Deemix using a sample song."""
        os.system(
            f"deemix --portable https://www.deezer.com/track/2817137262 --path {self.music_dir} --bitrate FLAC > NUL"
        )

class Scrape:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/jxl,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-GB,en;q=0.5"
        }

        self.base_url = "https://rentry.co/firehawk52"

    def arl(self) -> Optional[list[str]]:
        tokens = []
        r = self.session.get(
            url=self.base_url,
            headers=self.headers
        )
        if not r.status_code == 200:
            print(r.content.decode())
            return None
        soup = BeautifulSoup(r.content, 'lxml')
        ntable = soup.find_all('table', class_="ntable")
        print(ntable)
        print("nothing?")

if __name__ == '__main__':
    dzr = Dzr()
    dzr.account_info()
    print(dzr.date_end)
    # # dzr.search_query(query="marshmello happier")
    # dzr.search_query("2Scratch Escape Plan album")

    # scrape = Scrape()
    # scrape.arl()