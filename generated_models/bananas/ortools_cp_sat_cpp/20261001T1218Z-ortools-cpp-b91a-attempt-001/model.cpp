#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Bananas: five bananas cost $3, seven oranges $5, nine mangoes $7 and three
// apples $9. Buy 100 fruits for $100, at least one of each kind, with as few
// bananas plus apples as possible.
// The problem has no instance data: prices and totals are part of the puzzle.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  // Number of fruits of each kind bought; every kind is bought at least once.
  const IntVar bananas = model.NewIntVar(Domain(1, 100));
  const IntVar oranges = model.NewIntVar(Domain(1, 100));
  const IntVar mangoes = model.NewIntVar(Domain(1, 100));
  const IntVar apples = model.NewIntVar(Domain(1, 100));

  // The total cost is $100: 3/5 per banana, 5/7 per orange, 7/9 per mango and
  // 9/3 per apple, multiplied through by 945 = 5 * 7 * 9 * 3 to stay integral.
  model.AddEquality(3 * 189 * bananas + 5 * 135 * oranges + 7 * 105 * mangoes + 9 * 315 * apples,
                    100 * 945);

  // 100 fruits are bought.
  model.AddEquality(bananas + oranges + mangoes + apples, 100);

  // Minimize the number of bananas and apples together.
  model.Minimize(bananas + apples);

  outputs = {{"bananas", bananas.index()},
             {"oranges", oranges.index()},
             {"mangoes", mangoes.index()},
             {"apples", apples.index()}};
}
