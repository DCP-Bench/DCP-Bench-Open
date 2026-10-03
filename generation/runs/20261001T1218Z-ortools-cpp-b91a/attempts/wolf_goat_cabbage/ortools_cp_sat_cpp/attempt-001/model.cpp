#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Wolf, goat and cabbage: a farmer must ferry a wolf, a goat and a cabbage
// across a river in a boat that holds at most one item besides him, without
// ever leaving the wolf alone with the goat or the goat alone with the cabbage.
// Each position is 0 on the starting shore and 1 on the destination shore.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int stage = instance.at("stage").get<int>();

  std::vector<BoolVar> wolf, goat, cabbage, boat;
  for (int i = 0; i < stage; ++i) {
    wolf.push_back(model.NewBoolVar());
    goat.push_back(model.NewBoolVar());
    cabbage.push_back(model.NewBoolVar());
    boat.push_back(model.NewBoolVar());
  }

  // Initial situation: everything on the starting shore.
  model.AddEquality(boat[0], 0);
  model.AddEquality(wolf[0], 0);
  model.AddEquality(goat[0], 0);
  model.AddEquality(cabbage[0], 0);

  // The boat changes shore at every stage.
  for (int i = 1; i < stage; ++i) model.AddNotEqual(boat[i], boat[i - 1]);

  // Final situation: everything on the destination shore.
  model.AddEquality(boat[stage - 1], 1);
  model.AddEquality(wolf[stage - 1], 1);
  model.AddEquality(goat[stage - 1], 1);
  model.AddEquality(cabbage[stage - 1], 1);

  for (int i = 0; i < stage; ++i) {
    // The wolf and the goat cannot be left alone: they are on different
    // shores, or the boat (with the farmer) is on the wolf's shore.
    const BoolVar wg_apart = model.NewBoolVar();
    const BoolVar wg_watched = model.NewBoolVar();
    model.AddNotEqual(goat[i], wolf[i]).OnlyEnforceIf(wg_apart);
    model.AddEquality(boat[i], wolf[i]).OnlyEnforceIf(wg_watched);
    model.AddBoolOr({wg_apart, wg_watched});

    // The goat and the cabbage cannot be left alone: they are on different
    // shores, or the boat is on the goat's shore.
    const BoolVar gc_apart = model.NewBoolVar();
    const BoolVar gc_watched = model.NewBoolVar();
    model.AddNotEqual(goat[i], cabbage[i]).OnlyEnforceIf(gc_apart);
    model.AddEquality(boat[i], goat[i]).OnlyEnforceIf(gc_watched);
    model.AddBoolOr({gc_apart, gc_watched});
  }

  // Only one of the wolf, goat and cabbage changes shore per stage.
  // moved is true exactly when the item's position differs between stages
  // (|a - b| for two 0/1 values), reified in both directions.
  auto moved = [&](const BoolVar& a, const BoolVar& b) {
    const BoolVar m = model.NewBoolVar();
    model.AddNotEqual(a, b).OnlyEnforceIf(m);
    model.AddEquality(a, b).OnlyEnforceIf(m.Not());
    return m;
  };
  for (int i = 0; i + 1 < stage; ++i) {
    model.AddLessOrEqual(moved(wolf[i], wolf[i + 1]) + moved(goat[i], goat[i + 1]) +
                             moved(cabbage[i], cabbage[i + 1]),
                         1);
  }

  auto indices = [](const std::vector<BoolVar>& vars) {
    json a = json::array();
    for (const BoolVar& v : vars) a.push_back(v.index());
    return a;
  };
  outputs = {{"wolf_pos", indices(wolf)},
             {"goat_pos", indices(goat)},
             {"cabbage_pos", indices(cabbage)},
             {"boat_pos", indices(boat)}};
}
