#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Diamond-free degree sequence: an undirected loopless graph whose every
// degree is a nonzero multiple of three, whose edge count is a multiple of
// twelve, and where no four vertices span more than four edges.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("N").get<int>();

  std::vector<std::vector<BoolVar>> matrix(n);
  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < n; ++j) matrix[i].push_back(model.NewBoolVar());
  }

  // Undirected, and no vertex adjacent to itself.
  for (int i = 0; i < n; ++i) {
    model.AddEquality(matrix[i][i], 0);
    for (int j = i + 1; j < n; ++j) {
      model.AddEquality(matrix[i][j], matrix[j][i]);
    }
  }

  // Every degree is positive and divisible by three.
  for (int i = 0; i < n; ++i) {
    LinearExpr degree;
    for (int j = 0; j < n; ++j) degree += matrix[i][j];
    IntVar degree_var = model.NewIntVar(Domain(0, n));
    model.AddEquality(degree_var, degree);
    model.AddGreaterThan(degree_var, 0);
    IntVar degree_mod = model.NewIntVar(Domain(0, 2));
    model.AddModuloEquality(degree_mod, degree_var, 3);
    model.AddEquality(degree_mod, 0);
  }

  // The whole matrix sums to a multiple of twelve.
  LinearExpr total;
  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < n; ++j) total += matrix[i][j];
  }
  IntVar total_var = model.NewIntVar(Domain(0, int64_t{n} * n));
  model.AddEquality(total_var, total);
  IntVar total_mod = model.NewIntVar(Domain(0, 11));
  model.AddModuloEquality(total_mod, total_var, 12);
  model.AddEquality(total_mod, 0);

  // No four vertices span more than four of the six edges between them.
  for (int a = 0; a < n; ++a) {
    for (int b = a + 1; b < n; ++b) {
      for (int c = b + 1; c < n; ++c) {
        for (int d = c + 1; d < n; ++d) {
          model.AddLessOrEqual(matrix[a][b] + matrix[a][c] + matrix[a][d] +
                                   matrix[b][c] + matrix[b][d] + matrix[c][d],
                               4);
        }
      }
    }
  }

  json out = json::array();
  for (int i = 0; i < n; ++i) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(matrix[i][j].index());
    out.push_back(row);
  }
  outputs = {{"matrix", out}};
}
