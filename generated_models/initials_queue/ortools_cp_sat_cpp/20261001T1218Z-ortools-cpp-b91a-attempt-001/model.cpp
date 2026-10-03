#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Initials queue: ten people queue for a lecture. Each has initials that are
// an alphabetically ordered pair of distinct letters from A-E, no two share
// initials, and no one shares a letter with the person in front. BE is first,
// CD second and BD last. Find the queue. Letters are encoded A=0 .. E=4.
// The problem has no instance data; the given initials come from the statement.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int n = 10;
  const int A = 0, B = 1, C = 2, D = 3, E = 4;

  std::vector<std::vector<IntVar>> queue(n);
  for (int i = 0; i < n; ++i)
    for (int k = 0; k < 2; ++k) queue[i].push_back(model.NewIntVar(Domain(A, E)));

  // Each person's initials are two distinct letters in alphabetical order.
  for (int i = 0; i < n; ++i) model.AddLessThan(queue[i][0], queue[i][1]);

  // No two people have the same initials. The pair is coded as 5*first+second,
  // so distinct pairs are distinct codes.
  std::vector<LinearExpr> codes;
  for (int i = 0; i < n; ++i) codes.push_back(5 * queue[i][0] + queue[i][1]);
  model.AddAllDifferent(codes);

  // No one shares a letter with the person in front of them.
  for (int i = 0; i + 1 < n; ++i)
    for (int p = 0; p < 2; ++p)
      for (int q = 0; q < 2; ++q) model.AddNotEqual(queue[i][p], queue[i + 1][q]);

  // BE is at the front, CD right behind, and BD at the end.
  model.AddEquality(queue[0][0], B);
  model.AddEquality(queue[0][1], E);
  model.AddEquality(queue[1][0], C);
  model.AddEquality(queue[1][1], D);
  model.AddEquality(queue[n - 1][0], B);
  model.AddEquality(queue[n - 1][1], D);

  json leaves = json::array();
  for (int i = 0; i < n; ++i) leaves.push_back({queue[i][0].index(), queue[i][1].index()});
  outputs = {{"queue", leaves}};
}
