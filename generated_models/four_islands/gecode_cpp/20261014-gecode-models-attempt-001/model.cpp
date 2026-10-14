#include "dcp.h"

// Four islands on a 2x2 map: the name, primary export and tourist attraction of each.
// Map positions: A=0 (north-west), B=1 (north-east), C=2 (south-west), D=3 (south-east).
// Bridges: A-B and C-D run east-west, A-C and B-D run north-south.
// Names: Pwana=0, Quero=1, Rayou=2, Skern=3.
// Exports: alabaster=0, bananas=1, coconuts=2, durian fruit=3.
// Attractions: resort hotel=0, ice skating rink=1, jai alai stadium=2, koala preserve=3.
// The instance has no fields, so every value comes from the problem statement.
class FourIslands : public dcp::Space {
 protected:
  IntVarArray island;     // island[k]: map position of island k
  IntVarArray exportPos;  // exportPos[e]: map position of the island that exports e
  IntVarArray attrPos;    // attrPos[a]: map position of the island with attraction a
  IntVarArray exportOf;   // exportOf[k]: export of island k
  IntVarArray attrOf;     // attrOf[k]: attraction of island k

  // The map positions (x, y) must be one of the listed pairs (allowed = true),
  // or must not be any of them (allowed = false).
  void relate(IntVar x, IntVar y, const std::vector<std::pair<int, int>>& pairs, bool allowed) {
    TupleSet t(2);
    for (const auto& p : pairs) t.add(IntArgs({p.first, p.second}));
    t.finalize();
    IntVarArgs xy;
    xy << x << y;
    extensional(*this, xy, t, allowed);
  }

 public:
  explicit FourIslands(const json& instance) {
    (void)instance;

    // map positions of the four islands, export and attraction indices
    island = IntVarArray(*this, 4, 0, 3);
    exportPos = IntVarArray(*this, 4, 0, 3);
    attrPos = IntVarArray(*this, 4, 0, 3);
    exportOf = IntVarArray(*this, 4, 0, 3);
    attrOf = IntVarArray(*this, 4, 0, 3);

    // each island is on a different map position
    distinct(*this, island, IPL_DOM);
    // each island has a different primary export
    distinct(*this, exportOf, IPL_DOM);
    // each island has a different tourist attraction
    distinct(*this, attrOf, IPL_DOM);
    // each map position has one export and one attraction
    distinct(*this, exportPos, IPL_DOM);
    distinct(*this, attrPos, IPL_DOM);

    // island k exports exportOf[k], so the island with that export is at its position
    // island k has attraction attrOf[k], so the island with that attraction is at its position
    for (int k = 0; k < 4; ++k) {
      element(*this, exportPos, exportOf[k], island[k]);
      element(*this, attrPos, attrOf[k], island[k]);
    }

    // Map relations as position pairs (X, Y) with X related to Y.
    const std::vector<std::pair<int, int>> due_south = {{2, 0}, {3, 1}};
    const std::vector<std::pair<int, int>> due_east = {{1, 0}, {3, 2}};
    const std::vector<std::pair<int, int>> due_west = {{0, 1}, {2, 3}};
    const std::vector<std::pair<int, int>> north_south_bridge = {{0, 2}, {2, 0}, {1, 3}, {3, 1}};
    const std::vector<std::pair<int, int>> east_west_bridge = {{0, 1}, {1, 0}, {2, 3}, {3, 2}};
    std::vector<std::pair<int, int>> any_bridge = north_south_bridge;
    any_bridge.insert(any_bridge.end(), east_west_bridge.begin(), east_west_bridge.end());

    // 1. the island noted for its koala preserve is due south of Pwana
    relate(attrPos[3], island[0], due_south, true);

    // 2. the island with the largest alabaster quarry is due west of Quero
    relate(exportPos[0], island[1], due_west, true);

    // 3. the island with the resort hotel is due east of the one that exports durian fruit
    relate(attrPos[0], exportPos[3], due_east, true);

    // 4. Skern and the island with the jai alai stadium are connected by a north-south bridge
    relate(island[3], attrPos[2], north_south_bridge, true);

    // 5. Rayou and the island that exports bananas are connected by an east-west bridge
    relate(island[2], exportPos[1], east_west_bridge, true);

    // 6. the ice skating rink and the jai alai stadium are not connected by a bridge
    relate(attrPos[1], attrPos[2], any_bridge, false);

    // search: the island names, then their exports and attractions
    branch(*this, island, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, exportOf, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, attrOf, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("island", island);
    output("export", exportPos);
    output("attraction", attrPos);
  }

  FourIslands(FourIslands& s) : dcp::Space(s) {
    island.update(*this, s.island);
    exportPos.update(*this, s.exportPos);
    attrPos.update(*this, s.attrPos);
    exportOf.update(*this, s.exportOf);
    attrOf.update(*this, s.attrOf);
  }
  Gecode::Space* copy() override { return new FourIslands(*this); }
};

DCP_MODEL(FourIslands)
