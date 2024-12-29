""" 
This works. But......

When it comes for downloading it, then on the exception, assume the ARL is `invalid`

But but but, could add a settting in `settings` I guess to change the timeout, keeping the timeout as an option like:

class Download:
    timeout = 30

    def __init__(self, ...) -> None:
        ...

    def change_timeout(self, timeout: int) -> None:
        timeout = self.timeout
"""


import subprocess

download_query = "deemix --portable https://www.deezer.com/track/2817137262 --path ./music/ --bitrate FLAC > NUL"

# out = subprocess.run(download_query.split(), capture_output=True)
process = subprocess.Popen(download_query.split(), stdout=subprocess.PIPE, stdin=subprocess.PIPE)
try:
    process.wait(30)
    print(f"Finished\n{process.stdout.read().decode()}")
except Exception as e:
    print(f"Timed out after 10s\nException: {e}")
    process.kill()