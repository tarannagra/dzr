import json

with open('../config/config.json', 'r') as f:
    data = json.load(f)

def set_option(option, value) -> None:
    contents = data
    if value == "True":
        value = True
    else:
        value = False
    contents["tags"][option] = value
    with open("../config/config.json", 'w') as f:
        f.write(json.dumps(contents, indent=2))

while True:
    check = input("Enter option: ")

    if check == "set lyrics":
        choice = input(f"Lyrics is currently set to: {data["tags"]["lyrics"]}, enter new value: ")
        set_option("lyrics", choice)

    if check == "q":
        break
