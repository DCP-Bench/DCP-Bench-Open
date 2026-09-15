#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Costas array: a permutation whose difference triangle has all-distinct rows.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();

  std::vector<IntVar> costas;
  for (int i = 0; i < n; ++i) costas.push_back(model.NewIntVar(Domain(1, n)));
  model.AddAllDifferent(costas);

  // Only the strict upper triangle of the difference matrix carries meaning:
  // the reference pins the lower triangle to a constant and never reads the
  // diagonal, and neither is part of the declared output.
  std::vector<std::vector<IntVar>> differences(n);
  for (int i = 0; i < n; ++i) {
    differences[i].resize(n, model.NewIntVar(Domain(0, 0)));
    for (int j = i + 1; j < n; ++j) {
      IntVar d = model.NewIntVar(Domain(-n + 1, n - 1));
      model.AddEquality(d, costas[j] - costas[j - i - 1]);
      differences[i][j] = d;
    }
  }

  for (int i = 0; i < n - 2; ++i) {
    std::vector<IntVar> row;
    for (int j = i + 1; j < n; ++j) row.push_back(differences[i][j]);
    if (row.size() > 1) model.AddAllDifferent(row);
  }

  json out = json::array();
  for (const IntVar& c : costas) out.push_back(c.index());
  outputs = {{"costas", out}};
}
