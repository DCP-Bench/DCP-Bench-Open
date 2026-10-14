#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// KenKen: fill an n x n grid with the digits 1..n so that every row and every
// column holds each digit once, and every cage (a group of cells with a
// target number) reaches its target by one of the operations + - x /.
// Digits may repeat inside a cage. The operation is not given: a cage of two
// cells may use any of the four, a larger cage uses addition or multiplication.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();
  // problem[p] = [target, [[row, col], ...]] with 1-based cells. Cages differ in size.
  const json& problem = instance.at("problem");

  // x[i][j] is the digit in row i, column j.
  std::vector<std::vector<IntVar>> x(n);
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) x[i].push_back(model.NewIntVar(Domain(1, n)));

  // Each row holds each digit once.
  for (int i = 0; i < n; ++i) model.AddAllDifferent(x[i]);

  // Each column holds each digit once.
  for (int j = 0; j < n; ++j) {
    std::vector<IntVar> column;
    for (int i = 0; i < n; ++i) column.push_back(x[i][j]);
    model.AddAllDifferent(column);
  }

  for (const json& cage : problem) {
    const int64_t target = cage.at(0).get<int64_t>();
    std::vector<IntVar> cells;
    for (const json& cell : cage.at(1))
      cells.push_back(x[cell.at(0).get<int>() - 1][cell.at(1).get<int>() - 1]);

    // The cage target is reached by at least one allowed operation. Each
    // operation gets a Boolean that, when true, forces that operation to hold;
    // the cage needs at least one of them (a disjunction, so one direction of
    // the implication is enough).
    std::vector<BoolVar> options;
    auto new_option = [&]() {
      const BoolVar b = model.NewBoolVar();
      options.push_back(b);
      return b;
    };

    if (cells.size() == 2) {
      // Two cells a and b: a + b, a * b, a / b, b / a, a - b or b - a equals the target.
      const IntVar a = cells[0], b = cells[1];
      model.AddEquality(a + b, target).OnlyEnforceIf(new_option());
      const IntVar product = model.NewIntVar(Domain(1, static_cast<int64_t>(n) * n));
      model.AddMultiplicationEquality(product, {a, b});
      model.AddEquality(product, target).OnlyEnforceIf(new_option());
      model.AddEquality(b, target * a).OnlyEnforceIf(new_option());  // b / a == target
      model.AddEquality(a, target * b).OnlyEnforceIf(new_option());  // a / b == target
      model.AddEquality(a - b, target).OnlyEnforceIf(new_option());
      model.AddEquality(b - a, target).OnlyEnforceIf(new_option());
    } else {
      // Any other size: the digits add up to the target, or multiply to it.
      LinearExpr sum;
      for (const IntVar& c : cells) sum += c;
      model.AddEquality(sum, target).OnlyEnforceIf(new_option());

      // The product is built two factors at a time; every partial product is
      // at most n^k for a cage of k cells.
      IntVar product = cells[0];
      int64_t bound = n;
      for (size_t k = 1; k < cells.size(); ++k) {
        bound *= n;
        const IntVar next = model.NewIntVar(Domain(1, bound));
        model.AddMultiplicationEquality(next, {product, cells[k]});
        product = next;
      }
      model.AddEquality(product, target).OnlyEnforceIf(new_option());
    }
    model.AddBoolOr(options);
  }

  json out = json::array();
  for (int i = 0; i < n; ++i) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(x[i][j].index());
    out.push_back(row);
  }
  outputs = {{"x", out}};
}
