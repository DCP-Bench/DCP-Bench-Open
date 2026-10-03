#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Allergy logic puzzle: four friends (Debra, Janet, Hugh, Rick) each have a
// different surname (Baxter, Lemon, Malone, Fleet) and a different allergy
// (eggs, mold, nuts, ragweed). Match them using the clues.
// The problem has no instance data: names and clues are part of the puzzle.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int n = 4;
  const int Debra = 0, Janet = 1, Hugh = 2, Rick = 3;

  // foods[k] is the friend allergic to food k (eggs, mold, nuts, ragweed);
  // surnames[k] is the friend with surname k (baxter, lemon, malone, fleet).
  std::vector<IntVar> foods, surnames;
  for (int k = 0; k < n; ++k) {
    foods.push_back(model.NewIntVar(Domain(0, n - 1)));
    surnames.push_back(model.NewIntVar(Domain(0, n - 1)));
  }
  const IntVar &eggs = foods[0], &mold = foods[1], &nuts = foods[2], &ragweed = foods[3];
  const IntVar &baxter = surnames[0], &lemon = surnames[1], &malone = surnames[2],
               &fleet = surnames[3];

  // Each friend has a different allergy and a different surname.
  model.AddAllDifferent(foods);
  model.AddAllDifferent(surnames);

  // Rick is not allergic to mold.
  model.AddNotEqual(mold, Rick);
  // Baxter is allergic to eggs.
  model.AddEquality(eggs, baxter);
  // Hugh is neither surnamed Lemon nor Fleet.
  model.AddNotEqual(lemon, Hugh);
  model.AddNotEqual(fleet, Hugh);
  // Debra is allergic to ragweed.
  model.AddEquality(ragweed, Debra);
  // Janet (who isn't Lemon) is neither allergic to eggs nor to mold.
  model.AddNotEqual(lemon, Janet);
  model.AddNotEqual(eggs, Janet);
  model.AddNotEqual(mold, Janet);

  outputs = {{"eggs", eggs.index()},     {"mold", mold.index()},     {"nuts", nuts.index()},
             {"ragweed", ragweed.index()}, {"baxter", baxter.index()}, {"lemon", lemon.index()},
             {"malone", malone.index()}, {"fleet", fleet.index()}};
}
