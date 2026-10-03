#include <utility>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Four islands: islands Pwana, Quero, Rayou and Skern sit at map positions
//   (A) -- (B)
//    |      |
//   (C) -- (D)
// and each has a different export and a different tourist attraction. Place
// every island, export and attraction on the map from six clues.
// The problem has no instance data.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int n = 4;
  const int A = 0, B = 1, C = 2, D = 3;  // map positions

  auto row = [&]() {
    std::vector<IntVar> v;
    for (int i = 0; i < n; ++i) v.push_back(model.NewIntVar(Domain(0, n - 1)));
    return v;
  };
  // Map position of each island, export and attraction.
  const std::vector<IntVar> island = row();
  const IntVar &Pwana = island[0], &Quero = island[1], &Rayou = island[2], &Skern = island[3];
  const std::vector<IntVar> exportv = row();
  const IntVar &alabaster = exportv[0], &bananas = exportv[1], &durian_fruit = exportv[3];
  const std::vector<IntVar> attraction = row();
  const IntVar &resort_hotel = attraction[0], &ice_skating_rink = attraction[1],
               &jai_alai_stadium = attraction[2], &koala_preserve = attraction[3];

  // Islands, exports and attractions each occupy different positions.
  model.AddAllDifferent(island);
  model.AddAllDifferent(exportv);
  model.AddAllDifferent(attraction);

  // Each clue is a disjunction of placements (first item at p, second at q).
  // One literal per placement implies both equalities; one must hold.
  auto one_of = [&](const IntVar& first, const IntVar& second,
                    const std::vector<std::pair<int, int>>& placements) {
    std::vector<BoolVar> options;
    for (const auto& [p, q] : placements) {
      const BoolVar option = model.NewBoolVar();
      model.AddEquality(first, p).OnlyEnforceIf(option);
      model.AddEquality(second, q).OnlyEnforceIf(option);
      options.push_back(option);
    }
    model.AddBoolOr(options);
  };

  // 1. The island with the koala preserve is due south of Pwana.
  one_of(Pwana, koala_preserve, {{A, C}, {B, D}});
  // 2. The island with the alabaster quarry is due west of Quero.
  one_of(alabaster, Quero, {{A, B}, {C, D}});
  // 3. The island with the resort hotel is due east of the durian fruit exporter.
  one_of(durian_fruit, resort_hotel, {{A, B}, {C, D}});
  // 4. Skern and the jai alai stadium island share a north-south bridge.
  one_of(Skern, jai_alai_stadium, {{A, C}, {C, A}, {B, D}, {D, B}});
  // 5. Rayou and the banana exporter share an east-west bridge.
  one_of(Rayou, bananas, {{A, B}, {B, A}, {C, D}, {D, C}});
  // 6. The ice skating rink and the jai alai stadium islands are not connected
  //    by a bridge, so they sit on a diagonal.
  one_of(ice_skating_rink, jai_alai_stadium, {{A, D}, {D, A}, {B, C}, {C, B}});

  auto leaves = [](const std::vector<IntVar>& v) {
    json a = json::array();
    for (const IntVar& x : v) a.push_back(x.index());
    return a;
  };
  outputs = {{"island", leaves(island)},
             {"export", leaves(exportv)},
             {"attraction", leaves(attraction)}};
}
