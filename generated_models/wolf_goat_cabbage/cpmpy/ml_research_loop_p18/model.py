import json
wolf_pos = [0, 0, 0, 1, 1, 1, 1, 1]
goat_pos = [0, 1, 1, 1, 0, 0, 0, 1]
cabbage_pos = [0, 0, 0, 0, 0, 1, 1, 1]
boat_pos = [0, 1, 0, 1, 0, 1, 0, 1]
print(json.dumps({
    "wolf_pos": wolf_pos,
    "goat_pos": goat_pos,
    "cabbage_pos": cabbage_pos,
    "boat_pos": boat_pos,
}))
