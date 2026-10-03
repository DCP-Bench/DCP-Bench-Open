#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Five floors (Dinesman): Baker, Cooper, Fletcher, Miller and Smith live on the
// first five floors of an apartment house, on different floors. Find each
// person's floor from the clues.
// The problem has no instance data.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const Domain floors(1, 5);
  const IntVar B = model.NewIntVar(floors);  // Baker
  const IntVar C = model.NewIntVar(floors);  // Cooper
  const IntVar F = model.NewIntVar(floors);  // Fletcher
  const IntVar M = model.NewIntVar(floors);  // Miller
  const IntVar S = model.NewIntVar(floors);  // Smith

  // Baker does not live on the fifth floor.
  model.AddNotEqual(B, 5);
  // Cooper does not live on the first floor.
  model.AddNotEqual(C, 1);
  // Fletcher lives on neither the fifth nor the first floor.
  model.AddNotEqual(F, 5);
  model.AddNotEqual(F, 1);
  // Miller lives on a higher floor than Cooper.
  model.AddGreaterThan(M, C);
  // Smith does not live on a floor adjacent to Fletcher's: S - F is not +1 or -1.
  model.AddLinearConstraint(S - F, Domain::FromValues({-1, 1}).Complement());
  // Fletcher does not live on a floor adjacent to Cooper's.
  model.AddLinearConstraint(F - C, Domain::FromValues({-1, 1}).Complement());
  // They all live on different floors.
  model.AddAllDifferent(std::vector<IntVar>{B, C, F, M, S});

  outputs = {{"B", B.index()}, {"C", C.index()}, {"F", F.index()}, {"M", M.index()},
             {"S", S.index()}};
}
