import itertools
import json

movies = [
    ["Tarjan of the Jungle", 4, 13],
    ["The Four Volume Problem", 17, 27],
    ["The President's Algorist", 1, 10],
    ["Steiner's Tree", 12, 18],
    ["Process Terminated", 23, 30],
    ["Halting State", 9, 16],
    ["Programming Challenges", 19, 25],
    ["Discrete Mathematics", 2, 7],
    ["Calculated Bets", 26, 31],
]
best = None
for bits in itertools.product([False, True], repeat=len(movies)):
    valid = True
    for i in range(len(movies)):
        for j in range(i + 1, len(movies)):
            if bits[i] and bits[j]:
                if not (movies[i][2] < movies[j][1] or movies[j][2] < movies[i][1]):
                    valid = False
                    break
        if not valid:
            break
    if valid:
        count = sum(bits)
        if best is None or count > best[0]:
            best = (count, list(bits))
print(json.dumps({"selected_movies": best[1]}))
