#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// The abbot's puzzle: 100 bushels of corn are shared among 100 people, each
// man getting 3 bushels, each woman 2 and each child half a bushel, and there
// are five times as many women as men. How many men, women and children?
// The problem has no instance data: every number below is part of the puzzle.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const IntVar men = model.NewIntVar(Domain(0, 100));
  const IntVar women = model.NewIntVar(Domain(0, 100));
  const IntVar children = model.NewIntVar(Domain(0, 100));

  // There are 100 people in total.
  model.AddEquality(men + women + children, 100);

  // 100 bushels are distributed: 3 per man, 2 per woman, 1/2 per child,
  // doubled to keep the coefficients integral (6, 4, 1 and 200).
  model.AddEquality(6 * men + 4 * women + children, 200);

  // There are five times as many women as men.
  model.AddEquality(women, 5 * men);

  outputs = {{"men", men.index()}, {"women", women.index()}, {"children", children.index()}};
}
