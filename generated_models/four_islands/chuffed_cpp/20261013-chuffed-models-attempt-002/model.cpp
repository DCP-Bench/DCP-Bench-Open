// Four islands: match island names, exports and tourist attractions to the four map positions
// A=0, B=1, C=2, D=3 of a 2 x 2 map ((A) (B) on the north row, (C) (D) on the south row).
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // island[0..3] = Pwana, Quero, Rayou, Skern
  // export[0..3] = alabaster, bananas, coconuts, durian fruit
  // attraction[0..3] = resort hotel, ice skating rink, jai alai stadium, koala preserve
  vec<IntVar*> island, exports, attraction;
  createVars(island, 4, 0, 3, true);
  createVars(exports, 4, 0, 3, true);
  createVars(attraction, 4, 0, 3, true);

  // each island has a different name, a different primary export and a different attraction
  all_different(island);
  all_different(exports);
  all_different(attraction);

  // pairs (x, y) of map positions, as tables
  // x is due south of y (A is north of C, B is north of D)
  vec<vec<int>> south_of;
  const int south[2][2] = {{2, 0}, {3, 1}};
  for (auto& t : south) { south_of.push(); south_of.last().push(t[0]); south_of.last().push(t[1]); }
  // x is due west of y (A west of B, C west of D)
  vec<vec<int>> west_of;
  const int west[2][2] = {{0, 1}, {2, 3}};
  for (auto& t : west) { west_of.push(); west_of.last().push(t[0]); west_of.last().push(t[1]); }
  // x is due east of y
  vec<vec<int>> east_of;
  for (auto& t : west) { east_of.push(); east_of.last().push(t[1]); east_of.last().push(t[0]); }
  // x and y are connected by a north-south bridge
  vec<vec<int>> ns_bridge;
  const int ns[4][2] = {{0, 2}, {2, 0}, {1, 3}, {3, 1}};
  for (auto& t : ns) { ns_bridge.push(); ns_bridge.last().push(t[0]); ns_bridge.last().push(t[1]); }
  // x and y are connected by an east-west bridge
  vec<vec<int>> ew_bridge;
  const int ew[4][2] = {{0, 1}, {1, 0}, {2, 3}, {3, 2}};
  for (auto& t : ew) { ew_bridge.push(); ew_bridge.last().push(t[0]); ew_bridge.last().push(t[1]); }
  // x and y are different islands that are not connected by a bridge (diagonal positions)
  vec<vec<int>> no_bridge;
  const int diag[4][2] = {{0, 3}, {3, 0}, {1, 2}, {2, 1}};
  for (auto& t : diag) { no_bridge.push(); no_bridge.last().push(t[0]); no_bridge.last().push(t[1]); }

  // 1. The island noted for its koala preserve is due south of Pwana.
  { vec<IntVar*> p; p.push(attraction[3]); p.push(island[0]); table(p, south_of); }

  // 2. The island with the largest alabaster quarry is due west of Quero.
  { vec<IntVar*> p; p.push(exports[0]); p.push(island[1]); table(p, west_of); }

  // 3. The island with the resort hotel is due east of the one that exports durian fruit.
  { vec<IntVar*> p; p.push(attraction[0]); p.push(exports[3]); table(p, east_of); }

  // 4. Skern and the island with the jai alai stadium are connected by a north-south bridge.
  { vec<IntVar*> p; p.push(island[3]); p.push(attraction[2]); table(p, ns_bridge); }

  // 5. Rayou and the island that exports bananas are connected by an east-west bridge.
  { vec<IntVar*> p; p.push(island[2]); p.push(exports[1]); table(p, ew_bridge); }

  // 6. The islands with the ice skating rink and the jai alai stadium are not connected by a bridge.
  { vec<IntVar*> p; p.push(attraction[1]); p.push(attraction[2]); table(p, no_bridge); }

  vec<IntVar*> all;
  for (int i = 0; i < 4; ++i) all.push(island[i]);
  for (int i = 0; i < 4; ++i) all.push(exports[i]);
  for (int i = 0; i < 4; ++i) all.push(attraction[i]);
  branch(all, VAR_INORDER, VAL_MIN);

  json a = json::array(), b = json::array(), c = json::array();
  for (int i = 0; i < 4; ++i) {
    a.push_back(dcp::out(island[i]));
    b.push_back(dcp::out(exports[i]));
    c.push_back(dcp::out(attraction[i]));
  }
  outputs = {{"island", a}, {"export", b}, {"attraction", c}};
}
