#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Zebra puzzle: five houses in a row (0..4, left to right), each with a
// different colour, nationality, pet, drink and job. Each variable is the house
// of that attribute; place every attribute from the clues.
// The problem has no instance data.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int n_houses = 5;
  auto houses = [&]() {
    std::vector<IntVar> v;
    for (int i = 0; i < n_houses; ++i) v.push_back(model.NewIntVar(Domain(0, n_houses - 1)));
    return v;
  };
  const std::vector<IntVar> colors = houses();  // yellow, green, red, white, blue
  const IntVar &green = colors[1], &red = colors[2], &white = colors[3], &blue = colors[4];
  const std::vector<IntVar> nations = houses();  // italy, spain, japan, england, norway
  const IntVar &italy = nations[0], &spain = nations[1], &japan = nations[2],
               &england = nations[3], &norway = nations[4];
  const std::vector<IntVar> jobs = houses();  // painter, sculptor, diplomat, pianist, doctor
  const IntVar &painter = jobs[0], &sculptor = jobs[1], &diplomat = jobs[2], &doctor = jobs[4];
  const std::vector<IntVar> pets = houses();  // cat, zebra, bear, snails, horse
  const IntVar &zebra = pets[1], &snails = pets[3], &horse = pets[4];
  const std::vector<IntVar> drinks = houses();  // milk, water, tea, coffee, juice
  const IntVar &milk = drinks[0], &coffee = drinks[3];

  // Each house has a different colour, inhabitant, pet, drink and job.
  model.AddAllDifferent(colors);
  model.AddAllDifferent(nations);
  model.AddAllDifferent(jobs);
  model.AddAllDifferent(pets);
  model.AddAllDifferent(drinks);

  // The painter owns the horse.
  model.AddEquality(painter, horse);
  // The diplomat drinks coffee.
  model.AddEquality(diplomat, coffee);
  // The one who drinks milk lives in the white house.
  model.AddEquality(white, milk);
  // The Spaniard is a painter.
  model.AddEquality(spain, painter);
  // The Englishman lives in the red house.
  model.AddEquality(england, red);
  // The snails are owned by the sculptor.
  model.AddEquality(snails, sculptor);
  // The green house is immediately to the left of the red one.
  model.AddEquality(green + 1, red);
  // The Norwegian lives immediately to the right of the blue house.
  model.AddEquality(blue + 1, norway);
  // The doctor drinks milk.
  model.AddEquality(doctor, milk);
  // The diplomat is Japanese.
  model.AddEquality(japan, diplomat);
  // The Norwegian owns the zebra.
  model.AddEquality(norway, zebra);
  // The green house is next to the white one.
  model.AddLinearConstraint(green - white, Domain::FromValues({-1, 1}));
  // The horse is owned by a neighbour of the diplomat.
  model.AddLinearConstraint(horse - diplomat, Domain::FromValues({-1, 1}));
  // The Italian lives in the red, white or green house.
  std::vector<BoolVar> italian_house;
  for (const IntVar& house : {red, white, green}) {
    const BoolVar here = model.NewBoolVar();
    model.AddEquality(italy, house).OnlyEnforceIf(here);
    italian_house.push_back(here);
  }
  model.AddBoolOr(italian_house);

  auto leaves = [](const std::vector<IntVar>& v) {
    json a = json::array();
    for (const IntVar& x : v) a.push_back(x.index());
    return a;
  };
  outputs = {{"colors", leaves(colors)},
             {"nations", leaves(nations)},
             {"jobs", leaves(jobs)},
             {"pets", leaves(pets)},
             {"drinks", leaves(drinks)}};
}
