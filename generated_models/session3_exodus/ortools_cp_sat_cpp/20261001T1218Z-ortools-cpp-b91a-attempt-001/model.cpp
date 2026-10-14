#include <cstdint>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Exodus: five children (Bernice, Carl, Debby, Sammy, Ted) each tell a
// different part of the Exodus story, are of different ages (3, 5, 7, 8, 10)
// and come from different countries (Ethiopia, Kazakhstan, Lithuania, Morocco,
// Yemen). Each entity is given a slot 1..5; entities sharing a slot belong to
// the same child. Find the association from five clues.
// The problem has no instance data; the ages come from the statement.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int n = 5;
  const std::vector<int64_t> age_values = {3, 5, 7, 8, 10};

  auto slots = [&]() {
    std::vector<IntVar> v;
    for (int i = 0; i < n; ++i) v.push_back(model.NewIntVar(Domain(1, n)));
    return v;
  };
  const std::vector<IntVar> ages = slots();
  const std::vector<IntVar> children = slots();
  const IntVar &bernice = children[0], &debby = children[2], &sammy = children[3],
               &ted = children[4];
  const std::vector<IntVar> countries = slots();
  const IntVar &ethiopia = countries[0], &lithuania = countries[2], &morocco = countries[3],
               &yemen = countries[4];
  const std::vector<IntVar> stories = slots();
  const IntVar &moses_youth = stories[2], &passover = stories[3];

  // Within each category the entities occupy different slots.
  model.AddAllDifferent(ages);
  model.AddAllDifferent(children);
  model.AddAllDifferent(countries);
  model.AddAllDifferent(stories);

  // age_of_slot[s] is the age in years of the child in slot s+1: the age whose
  // slot is s+1. This turns "X is k years older than Y" into arithmetic on
  // ages looked up by slot, instead of enumerating all pairs of age values.
  std::vector<IntVar> age_of_slot;
  for (int s = 0; s < n; ++s) age_of_slot.push_back(model.NewIntVar(Domain::FromValues(age_values)));
  const std::vector<LinearExpr> age_table(age_of_slot.begin(), age_of_slot.end());
  for (int k = 0; k < n; ++k) {
    model.AddElement(ages[k] - 1, age_table, model.NewConstant(age_values[k]));
  }
  // The age in years of whichever child holds the given slot.
  auto age_of = [&](const IntVar& slot) {
    const IntVar years = model.NewIntVar(Domain::FromValues(age_values));
    model.AddElement(slot - 1, age_table, years);
    return years;
  };

  // 1. Debby's family is from Lithuania.
  model.AddEquality(debby, lithuania);

  // 2. The child who told the Passover story is two years older than Bernice.
  model.AddEquality(age_of(passover), age_of(bernice) + 2);

  // 3. The child from Yemen is younger than the child from Ethiopia.
  model.AddLessThan(age_of(yemen), age_of(ethiopia));

  // 4. The child from Morocco is three years older than Ted.
  model.AddEquality(age_of(morocco), age_of(ted) + 3);

  // 5. Sammy is three years older than the child who told of Moses's youth.
  model.AddEquality(age_of(sammy), age_of(moses_youth) + 3);

  auto leaves = [](const std::vector<IntVar>& v) {
    json a = json::array();
    for (const IntVar& x : v) a.push_back(x.index());
    return a;
  };
  outputs = {{"ages", leaves(ages)},
             {"children", leaves(children)},
             {"countries", leaves(countries)},
             {"stories", leaves(stories)}};
}
