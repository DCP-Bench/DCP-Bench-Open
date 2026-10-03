#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Contracting costs: a contractor knows what he pays to six pairs of
// tradesmen; find what each man charges.
// The problem has no instance data: the pair totals are part of the puzzle.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  // Each charge is a whole number of dollars between 1 and 5300 (the largest pair total).
  auto charge = [&]() { return model.NewIntVar(Domain(1, 5300)); };
  const IntVar paper_hanger = charge(), painter = charge(), plumber = charge(),
               electrician = charge(), carpenter = charge(), mason = charge();

  // $1,100 to the paper hanger and the painter.
  model.AddEquality(paper_hanger + painter, 1100);
  // $1,700 to the painter and plumber.
  model.AddEquality(painter + plumber, 1700);
  // $1,100 to the plumber and electrician.
  model.AddEquality(plumber + electrician, 1100);
  // $3,300 to the electrician and carpenter.
  model.AddEquality(electrician + carpenter, 3300);
  // $5,300 to the carpenter and mason.
  model.AddEquality(carpenter + mason, 5300);
  // $3,200 to the mason and painter.
  model.AddEquality(mason + painter, 3200);

  outputs = {{"paper_hanger", paper_hanger.index()}, {"painter", painter.index()},
             {"plumber", plumber.index()},           {"electrician", electrician.index()},
             {"carpenter", carpenter.index()},       {"mason", mason.index()}};
}
