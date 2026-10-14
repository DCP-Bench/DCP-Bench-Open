#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Added corners: place the digits 1..8 on the eight positions of a 3 x 3 ring
// (circles C on the corners, squares F on the edges) so that each square
// holds the sum of its two adjoining circles:
//
//   a b c        C F C
//   d   e        F   F
//   f g h        C F C
//
// The problem has no instance data: the layout and the digits 1..8 are part
// of the puzzle.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int n = 8;  // number of positions and largest digit
  std::vector<IntVar> positions;
  for (int i = 0; i < n; ++i) positions.push_back(model.NewIntVar(Domain(1, n)));
  const IntVar &a = positions[0], &b = positions[1], &c = positions[2], &d = positions[3],
               &e = positions[4], &f = positions[5], &g = positions[6], &h = positions[7];

  // Every digit is used once.
  model.AddAllDifferent(positions);

  // Each square equals the sum of its two adjoining circles.
  model.AddEquality(b, a + c);  // top edge
  model.AddEquality(d, a + f);  // left edge
  model.AddEquality(e, c + h);  // right edge
  model.AddEquality(g, f + h);  // bottom edge

  json out = json::array();
  for (const IntVar& p : positions) out.push_back(p.index());
  outputs = {{"positions", out}};
}
