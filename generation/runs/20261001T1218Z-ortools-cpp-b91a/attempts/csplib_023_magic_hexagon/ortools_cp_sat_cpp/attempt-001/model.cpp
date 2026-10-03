#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Magic hexagon (CSPLib 23): place the numbers 1..19 on the cells of a
// hexagon with sides of three cells so that each of its 15 lines (5 rows and
// 5 diagonals in each of the two directions) sums to the magic constant.
//
//       A B C
//      D E F G
//     H I J K L
//      M N O P
//       Q R S
//
// The cell layout and its lines are fixed by the problem; NUM_CELLS and
// MAGIC_SUM come from the instance.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int num_cells = instance.at("NUM_CELLS").get<int>();
  const int64_t magic_sum = instance.at("MAGIC_SUM").get<int64_t>();

  // LD[k]: the number in cell k (A = 0 .. S = 18).
  std::vector<IntVar> LD;
  for (int k = 0; k < num_cells; ++k) LD.push_back(model.NewIntVar(Domain(1, num_cells)));
  enum { a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s };

  // Every number is used exactly once.
  model.AddAllDifferent(LD);

  // Each of the 15 lines sums to the magic constant.
  const std::vector<std::vector<int>> lines = {
      // rows
      {a, b, c}, {d, e, f, g}, {h, i, j, k, l}, {m, n, o, p}, {q, r, s},
      // diagonals from top-left to bottom-right
      {a, d, h}, {b, e, i, m}, {c, f, j, n, q}, {g, k, o, r}, {l, p, s},
      // diagonals from top-right to bottom-left
      {c, g, l}, {b, f, k, p}, {a, e, j, o, s}, {d, i, n, r}, {h, m, q},
  };
  for (const std::vector<int>& line : lines) {
    LinearExpr sum;
    for (int cell : line) sum += LD[cell];
    model.AddEquality(sum, magic_sum);
  }

  json out = json::array();
  for (const IntVar& v : LD) out.push_back(v.index());
  outputs = {{"LD", out}};
}
