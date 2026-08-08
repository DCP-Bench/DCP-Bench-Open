
import cpmpy as cp
import json

# Data (orderings)
# island names: [Pwana, Quero, Rayou, Skern]
# exports:      [alabaster, bananas, coconuts, durian]
# attractions:  [hotel, ice_rink, jai_alai, koala]
# island indices: A=0, B=1, C=2, D=3

# Model definition
model = cp.Model()

# Decision Variables
# Each array maps item index -> island index (0..3)
island = cp.intvar(0, 3, shape=4, name="island")
export = cp.intvar(0, 3, shape=4, name="export")
attraction = cp.intvar(0, 3, shape=4, name="attraction")

# Constraints
# Each category must be a permutation of islands
model += cp.AllDifferent(island)
model += cp.AllDifferent(export)
model += cp.AllDifferent(attraction)

# Helpers: allowed adjacency pairs for directions
# south_of: (north_island, south_island)
south_pairs = [[0,2], [1,3]]
# west_of: (east_island, west_island)
west_pairs = [[1,0], [3,2]]
# east_of: (west_island, east_island)
east_pairs = [[0,1], [2,3]]
# vertical adjacency (north-south), unordered (both directions)
ns_pairs = [[0,2], [2,0], [1,3], [3,1]]
# horizontal adjacency (east-west), unordered (both directions)
ew_pairs = [[0,1], [1,0], [2,3], [3,2]]
# diagonal non-adjacent pairs (not connected by a bridge)
diag_pairs = [[0,3], [3,0], [1,2], [2,1]]

# 1. Koala preserve is due south of Pwana.
# island[Pwana] -> attraction[koala] with south relation
model += cp.Table([island[0], attraction[3]], south_pairs)

# 2. Alabaster is due west of Quero.
# island[Quero] -> export[alabaster] with west relation
model += cp.Table([island[1], export[0]], west_pairs)

# 3. Hotel is due east of Durian.
# export[durian] -> attraction[hotel] with east relation
model += cp.Table([export[3], attraction[0]], east_pairs)

# 4. Skern and Jai Alai connected by a north-south bridge.
# island[Skern] and attraction[jai_alai] are vertical neighbors
model += cp.Table([island[3], attraction[2]], ns_pairs)

# 5. Rayou and Bananas connected by an east-west bridge.
# island[Rayou] and export[bananas] are horizontal neighbors
model += cp.Table([island[2], export[1]], ew_pairs)

# 6. Ice rink and Jai Alai are not connected by a bridge (i.e., diagonal)
model += cp.Table([attraction[1], attraction[2]], diag_pairs)

# Solve and print
if model.solve():
    solution = {
        'island': island.value().tolist(),
        'export': export.value().tolist(),
        'attraction': attraction.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
