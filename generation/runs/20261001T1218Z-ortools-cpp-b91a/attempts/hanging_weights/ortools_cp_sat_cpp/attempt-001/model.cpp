#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Hanging weights: thirteen weights A-M, each a different integer from 1 to 13,
// hang from a system of bars. On every bar the weights on either side of the
// pivot balance when multiplied by their distance, and a bar hanging beneath
// another counts as a single weight equal to its total.
// The problem has no instance data; the bar geometry is the statement's diagram.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int N = 13;
  std::vector<IntVar> x;
  for (int i = 0; i < N; ++i) x.push_back(model.NewIntVar(Domain(1, N)));
  const IntVar &a = x[0], &b = x[1], &c = x[2], &d = x[3], &e = x[4], &f = x[5], &g = x[6],
               &h = x[7], &i = x[8], &j = x[9], &k = x[10], &l = x[11], &m = x[12];

  // Each weight has a different value.
  model.AddAllDifferent(x);

  // Bottom bar under the left middle bar: A at distance 4, B at distance 1.
  model.AddEquality(4 * a, b);
  // Bottom right bar: C at distance 5, D at distance 1.
  model.AddEquality(5 * c, d);
  // Bar holding E and F: E at distance 3, F at distance 2.
  model.AddEquality(3 * e, 2 * f);
  // Bar holding G and the C-D bar: G at distance 3, the C-D bar at distance 2.
  model.AddEquality(3 * g, 2 * (c + d));
  // Bar holding the A-B bar, J, K and the G-C-D bar.
  model.AddEquality(3 * (a + b) + 2 * j, k + 2 * (g + c + d));
  // Bar holding H, the E-F bar and I.
  model.AddEquality(3 * h, 2 * (e + f) + 3 * i);
  // Bar holding the H-I-E-F bar, L and M.
  model.AddEquality(h + i + e + f, l + 4 * m);
  // Top bar: the left assembly at distance 4, the right one at distance 3.
  model.AddEquality(4 * (l + m + h + i + e + f), 3 * (j + k + g + a + b + c + d));

  outputs = {{"a", a.index()}, {"b", b.index()}, {"c", c.index()}, {"d", d.index()},
             {"e", e.index()}, {"f", f.index()}, {"g", g.index()}, {"h", h.index()},
             {"i", i.index()}, {"j", j.index()}, {"k", k.index()}, {"l", l.index()},
             {"m", m.index()}};
}
