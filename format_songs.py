with open('songs.txt', 'r') as f:
    data = f.read()

lines = [line for line in data.splitlines() if line.strip()]
with open('songs.txt', 'w') as f:
    for line in lines:
        f.write(f"{line}\n")