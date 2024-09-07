

import os

import requests

class Dzr:
    """
    Deezer download class to search and download the songs.
    """
    def __init__(self, bitrate: str = "FLAC") -> None:
        self.session = requests.Session()
        self.bitrate = bitrate

        self.search_url = "https://api.deezer.com/search?q={}&output=json&output=json&version=js-v1.0.0"
        self.album_url = "https://www.deezer.com/en/album/{}"

        self.download_query = "deemix --portable {} --path ./music/ --bitrate " + self.bitrate + " > NUL "
    
    def clean(self) -> None:
        """
        Removes all media files from the music path and their respective file extension.
        
        Args:
            None
            
        Returns:
            None
        
        """
        os.system("rm -rf ./music/*")

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
        Searches using the Deezer API but this time around, it will prompt the user if this result is the 
        correct one. If it is, then return those properties of the title and link (or id). So, it will all be done here.
        
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
        
        # for x in result:
        #     print(f"ID: {x['id']}")
        #     print(f"Title: {x['title']}")
        #     print(f"Link: {x['link']}")
        

    
    def download(self, song_link: str) -> None:
        """
        Downloads the song by the link using Deemix.

        Args:
            song_link (str): The given track link returned from `self.search()`.
        
        Returns:
            None
        """
        os.system(
            self.download_query.format(song_link),
        )
    
    def init(self) -> None:
        """Initialises the directory for Deemix using a sample song."""
        os.system(
            "deemix --portable https://www.deezer.com/track/2817137262 --path ./music/ --bitrate FLAC > NUL"
        )

if __name__ == '__main__':
    dzr = Dzr()
    # dzr.search_query(query="marshmello happier")
    dzr.search_query("2Scratch Escape Plan album")
