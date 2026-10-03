# Four islands: four islands A, B (north) and C, D (south), joined by bridges A-B, C-D, A-C, B-D.
# Find each island's name, export and tourist attraction from six clues.
from pychoco.model import Model

# The puzzle has no instance data; the map and the clues are its statement.
# Map positions: A is north of C and west of B; C is west of D; B is north of D.
A, B, C, D = range(4)
SOUTH_OF = [(A, C), (B, D)]                          # (north, south) pairs
WEST_OF = [(A, B), (C, D)]                           # (west, east) pairs
NORTH_SOUTH_BRIDGE = SOUTH_OF + [(s, n) for n, s in SOUTH_OF]
EAST_WEST_BRIDGE = WEST_OF + [(e, w) for w, e in WEST_OF]
NO_BRIDGE = [(A, D), (D, A), (B, C), (C, B)]         # diagonal pairs


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    # Each list gives the map position of each item.
    island = [model.intvar(0, 3, name=f"island_{k}") for k in range(4)]
    pwana, quero, rayou, skern = island
    export = [model.intvar(0, 3, name=f"export_{k}") for k in range(4)]
    alabaster, bananas, coconuts, durian_fruit = export
    attraction = [model.intvar(0, 3, name=f"attraction_{k}") for k in range(4)]
    resort_hotel, ice_skating_rink, jai_alai_stadium, koala_preserve = attraction

    # Each island has one name, one export and one attraction.
    for group in (island, export, attraction):
        model.all_different(group).post()

    # 1. The island with the koala preserve is due south of Pwana.
    model.table([pwana, koala_preserve], SOUTH_OF).post()
    # 2. The island with the alabaster quarry is due west of Quero.
    model.table([alabaster, quero], WEST_OF).post()
    # 3. The island with the resort hotel is due east of the one exporting durian fruit.
    model.table([durian_fruit, resort_hotel], WEST_OF).post()
    # 4. Skern and the jai alai stadium island are connected by a north-south bridge.
    model.table([skern, jai_alai_stadium], NORTH_SOUTH_BRIDGE).post()
    # 5. Rayou and the banana-exporting island are connected by an east-west bridge.
    model.table([rayou, bananas], EAST_WEST_BRIDGE).post()
    # 6. The ice skating rink and jai alai stadium islands are not connected by a bridge.
    model.table([ice_skating_rink, jai_alai_stadium], NO_BRIDGE).post()

    return model, {"island": island, "export": export, "attraction": attraction}
