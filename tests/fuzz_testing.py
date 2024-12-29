
# rapidfuzz over fuzzywuzzy since it's faster and i want this to be fast!

from rapidfuzz import fuzz, process

# Determine which is better for use case, fuzz or process

query = "symphony mikey"

song_results = [
    "All Elite Wrestling - Fight of the Valkyrie (Bryan Danielson Symphony) ",
    "LIKEBSNS - SYMPHONY",
    "Ahmed Helmy - Symphony (Mixed)",
    "Mike Tunes - Symphony",
    "Mikey Barreneche - Symphony",
    "Roma Symphony Orchestra - Flowers",
    "Christopher Willis - Springtime Symphony ",
]

out = process.extract(query, song_results, scorer=fuzz.WRatio, limit=1)


# out = process.extractOne(song_results, query, scorer=fuzz.WRatio)
print(out[0][0])