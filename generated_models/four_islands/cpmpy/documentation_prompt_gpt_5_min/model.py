
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

# 1. The koala preserve is due south of Pwana.
model += (koala == Pwana + 2)

# 2. The alabaster quarry is due west of Quero.
model += (alabaster == Quero - 1)

# 3. The resort hotel is due east of the one that exports durian fruit.
model += (hotel == durian + 1)

# 4. Skern and the island with the jai alai stadium are connected by a north-south bridge.
#    (vertical neighbors -> difference 2)
model += (cp.Abs(Skern - jai) == 2)

# 5. Rayou and the island that exports bananas are connected by an east-west bridge.
#    (horizontal neighbors -> difference 1)
model += (cp.Abs(Rayou - bananas) == 1)

# 6. The ice skating rink and the jai alai stadium are not connected by a bridge.
#    (not horizontally or vertically adjacent -> difference is not 1 or 2)
model += (cp.Abs(ice - jai) != 1)
model += (cp.Abs(ice - jai) != 2)

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
