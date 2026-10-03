#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Dinner: take 1-6 grandparents, 1-10 parents and 1-40 children to dinner.
// Grandparents cost $3, parents $2 and children $0.50; there must be 20
// people and the bill must be $20. How many of each go?
// The problem has no instance data; every number comes from the statement.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  // 1-6 grandparents, 1-10 parents and 1-40 children.
  const IntVar grandparents = model.NewIntVar(Domain(1, 6));
  const IntVar parents = model.NewIntVar(Domain(1, 10));
  const IntVar children = model.NewIntVar(Domain(1, 40));

  // The dinner costs $20; prices are doubled ($6, $4, $1 against $40) so that
  // the children's $0.50 becomes an integer coefficient.
  model.AddEquality(6 * grandparents + 4 * parents + children, 40);

  // There are 20 people in total.
  model.AddEquality(grandparents + parents + children, 20);

  outputs = {{"grandparents", grandparents.index()},
             {"parents", parents.index()},
             {"children", children.index()}};
}
