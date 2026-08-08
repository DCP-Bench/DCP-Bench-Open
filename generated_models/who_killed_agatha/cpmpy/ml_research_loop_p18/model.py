import json
names = ["Agatha herself", "the butler", "Charles"]
killer = names.index("Agatha herself")
print(json.dumps(dict(killer=killer)))
