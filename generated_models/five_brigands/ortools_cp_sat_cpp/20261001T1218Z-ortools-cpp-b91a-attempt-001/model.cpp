#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// The five brigands (Dudeney 133): Alfonso, Benito, Carlos, Diego and Esteban
// hold 200 doubloons together, and would still hold 200 if Alfonso had twelve
// times as much, Benito three times, Carlos the same, Diego half and Esteban a
// third. Each has at least one doubloon. How many has each?
// The problem has no instance data; every number comes from the statement.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  // No brigand has less than one doubloon, and none more than the 200 total.
  const Domain range(1, 200);
  const IntVar A = model.NewIntVar(range);
  const IntVar B = model.NewIntVar(range);
  const IntVar C = model.NewIntVar(range);
  const IntVar D = model.NewIntVar(range);
  const IntVar E = model.NewIntVar(range);

  // Altogether they captured exactly 200 doubloons.
  model.AddEquality(A + B + C + D + E, 200);

  // 12A + 3B + C + D/2 + E/3 is also 200; multiplied by 6 to keep it integral.
  model.AddEquality(72 * A + 18 * B + 6 * C + 3 * D + 2 * E, 6 * 200);

  outputs = {{"A", A.index()}, {"B", B.index()}, {"C", C.index()}, {"D", D.index()},
             {"E", E.index()}};
}
