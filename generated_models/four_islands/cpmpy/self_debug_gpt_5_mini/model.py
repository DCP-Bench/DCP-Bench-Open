
import cpmpy as cp
import json

# Positions: 0=A (top-left), 1=B (top-right), 2=C (bottom-left), 3=D (bottom-right)

# Model definition
model = cp.Model()

# Decision Variables
# Island name positions: Pwana, Quero, Rayou, Skern
Pwana, Quero, Rayou, Skern = cp.intvar(0, 3, shape=4, name="name_pos")
# Exports positions: alabaster, bananas, coconuts, durian
alabaster, bananas, coconuts, durian = cp.intvar(0, 3, shape=4, name="export_pos")
# Attractions positions: hotel, ice skating rink, jai alai stadium, koala preserve
hotel, ice, jai, koala = cp.intvar(0, 3, shape=4, name="attr_pos")

# Constraints
# All positions within each category are a permutation of the 4 islands
model += cp.AllDifferent(Pwana, Quero, Rayou, Skern)
model += cp.AllDifferent(alabaster, bananas, coconuts, durian)
model += cp.AllDifferent(hotel, ice, jai, koala)

# Helper boolean expressions for adjacency (explicit pairs)
# Horizontal adjacency pairs: (0,1) and (2,3)
def is_horizontal_pair(x, y):
    return ((x == 0) & (y == 1)) | ((x == 1) & (y == 0)) | ((x == 2) & (y == 3)) | ((x == 3) & (y == 2))

# Vertical adjacency pairs: (0,2) and (1,3)
def is_vertical_pair(x, y):
    return ((x == 0) & (y == 2)) | ((x == 2) & (y == 0)) | ((x == 1) & (y == 3)) | ((x == 3) & (y == 1))

# 1. The koala preserve is due south of Pwana.
# south means vertical neighbor with koala below Pwana: (Pwana,koala) in {(0,2),(1,3)}
model += ((Pwana == 0) & (koala == 2)) | ((Pwana == 1) & (koala == 3))

# 2. The alabaster quarry is due west of Quero.
# west means horizontal neighbor with alabaster to the left of Quero: (alabaster, Quero) in {(0,1),(2,3)} as (left,right)
model += ((alabaster == 0) & (Quero == 1)) | ((alabaster == 2) & (Quero == 3))

# 3. The resort hotel is due east of the one that exports durian fruit.
# east means hotel is to the right of durian: (durian,hotel) in {(0,1),(2,3)}
model += ((durian == 0) & (hotel == 1)) | ((durian == 2) & (hotel == 3))

# 4. Skern and the island with the jai alai stadium are connected by a north-south bridge.
# vertical neighbors
model += is_vertical_pair(Skern, jai)

# 5. Rayou and the island that exports bananas are connected by an east-west bridge.
# horizontal neighbors
model += is_horizontal_pair(Rayou, bananas)

# 6. The ice skating rink and the jai alai stadium are not connected by a bridge.
# i.e., they are neither horizontal nor vertical neighbors
model += ~(is_horizontal_pair(ice, jai) | is_vertical_pair(ice, jai))

# Solve and print
if model.solve():
    # island list order: Pwana, Quero, Rayou, Skern
    island = [int(Pwana.value()), int(Quero.value()), int(Rayou.value()), int(Skern.value())]
    # export list order: alabaster, bananas, coconuts, durian
    export = [int(alabaster.value()), int(bananas.value()), int(coconuts.value()), int(durian.value())]
    # attraction list order: hotel, ice skating rink, jai alai stadium, koala preserve
    attraction = [int(hotel.value()), int(ice.value()), int(jai.value()), int(koala.value())]

    solution = {
        "island": island,
        "export": export,
        "attraction": attraction
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
