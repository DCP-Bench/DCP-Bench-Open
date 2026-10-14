#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Huey, Dewey and Louie: from the three nephews' statements, all true, decide
// which of them (if any) are guilty.
// The problem has no instance data.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const BoolVar huey = model.NewBoolVar();   // Huey is guilty
  const BoolVar dewey = model.NewBoolVar();  // Dewey is guilty
  const BoolVar louie = model.NewBoolVar();  // Louie is guilty

  // Huey: Dewey and Louie share equally; if one is guilty, so is the other.
  model.AddEquality(dewey, louie);

  // Dewey: if Huey is guilty, then so am I.
  model.AddImplication(huey, dewey);

  // Louie: Dewey and I are not both guilty.
  model.AddBoolOr({dewey.Not(), louie.Not()});

  outputs = {{"huey", huey.index()}, {"dewey", dewey.index()}, {"louie", louie.index()}};
}
