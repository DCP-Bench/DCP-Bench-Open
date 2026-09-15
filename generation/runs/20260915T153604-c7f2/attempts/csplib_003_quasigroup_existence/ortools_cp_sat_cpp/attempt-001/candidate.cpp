#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Quasigroup existence, QG3: a Latin square in which (a*b)*(b*a) = a for every
// pair of elements.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int m = instance.at("m").get<int>();

  std::vector<std::vector<IntVar>> q(m);
  for (int i = 0; i < m; ++i) {
    for (int j = 0; j < m; ++j) q[i].push_back(model.NewIntVar(Domain(0, m - 1)));
  }

  for (int i = 0; i < m; ++i) {
    std::vector<IntVar> row;
    std::vector<IntVar> col;
    for (int j = 0; j < m; ++j) {
      row.push_back(q[i][j]);
      col.push_back(q[j][i]);
    }
    model.AddAllDifferent(row);
    model.AddAllDifferent(col);
  }

  // The QG3 property indexes the table by two of its own entries, so the table
  // is flattened and read with a single element constraint at row * m + col.
  std::vector<LinearExpr> flat;
  for (int i = 0; i < m; ++i) {
    for (int j = 0; j < m; ++j) flat.push_back(q[i][j]);
  }

  for (int a = 0; a < m; ++a) {
    for (int b = 0; b < m; ++b) {
      IntVar cell = model.NewIntVar(Domain(0, m * m - 1));
      model.AddEquality(cell, m * q[a][b] + q[b][a]);
      IntVar value = model.NewIntVar(Domain(0, m - 1));
      model.AddElement(cell, flat, value);
      model.AddEquality(value, a);
    }
  }

  json out = json::array();
  for (int i = 0; i < m; ++i) {
    json row = json::array();
    for (int j = 0; j < m; ++j) row.push_back(q[i][j].index());
    out.push_back(row);
  }
  outputs = {{"quasigroup", out}};
}
