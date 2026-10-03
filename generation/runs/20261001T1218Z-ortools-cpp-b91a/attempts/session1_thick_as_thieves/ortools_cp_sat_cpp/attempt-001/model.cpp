#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Thick as thieves: six suspects were interviewed after a jewel robbery. At
// most two did it, the innocent tell the truth and the guilty lie. Who is
// guilty? Each suspect is guilty exactly when their statement is false.
// The problem has no instance data.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const BoolVar artie = model.NewBoolVar();
  const BoolVar bill = model.NewBoolVar();
  const BoolVar crackitt = model.NewBoolVar();
  const BoolVar dodgy = model.NewBoolVar();
  const BoolVar edgy = model.NewBoolVar();
  const BoolVar fingers = model.NewBoolVar();
  const LinearExpr guilty_count = artie + bill + crackitt + dodgy + edgy + fingers;

  // The getaway car held at most two, so at most two are guilty.
  model.AddLessOrEqual(guilty_count, 2);

  // Artie: "It wasn't me." Guilty iff he did it: holds for any value, so no
  // constraint is needed.

  // Bill: "Crackitt was in it up to his neck." Bill is guilty iff Crackitt is not.
  model.AddEquality(bill, crackitt.Not());

  // Crackitt: "No I wasn't." Like Artie's, true for any value.

  // Dodgy: "If Crackitt did it, Bill did it with him." Dodgy is guilty iff the
  // statement is false, i.e. iff Crackitt is guilty and Bill is not.
  model.AddBoolAnd({crackitt, bill.Not()}).OnlyEnforceIf(dodgy);
  model.AddBoolOr({crackitt.Not(), bill}).OnlyEnforceIf(dodgy.Not());

  // Edgy: "Nobody did it alone" (more than one is guilty). Edgy is guilty iff
  // at most one is guilty.
  model.AddLessOrEqual(guilty_count, 1).OnlyEnforceIf(edgy);
  model.AddGreaterThan(guilty_count, 1).OnlyEnforceIf(edgy.Not());

  // Fingers: "It was Artie and Dodgy together." Fingers is guilty iff not both
  // Artie and Dodgy are guilty.
  model.AddBoolOr({artie.Not(), dodgy.Not()}).OnlyEnforceIf(fingers);
  model.AddBoolAnd({artie, dodgy}).OnlyEnforceIf(fingers.Not());

  outputs = {{"artie", artie.index()},       {"bill", bill.index()},
             {"crackitt", crackitt.index()}, {"dodgy", dodgy.index()},
             {"edgy", edgy.index()},         {"fingers", fingers.index()}};
}
