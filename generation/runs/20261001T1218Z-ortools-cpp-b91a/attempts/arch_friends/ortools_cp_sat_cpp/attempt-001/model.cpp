#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Arch friends logic puzzle: Harriet bought four pairs of shoes at four
// different stores, one per stop. Find the stop (1..4) at which each pair was
// bought and the stop at which each store was visited.
// The problem has no instance data: shoes, stores and clues are part of the puzzle.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int n = 4;

  // shoes[k]: stop at which shoe k was bought (ecru espadrilles, fuchsia
  // flats, purple pumps, suede sandals). store[k]: stop at which store k was
  // visited (Foot Farm, Heels in a Handcart, The Shoe Palace, Tootsies).
  std::vector<IntVar> shoes, store;
  for (int k = 0; k < n; ++k) {
    shoes.push_back(model.NewIntVar(Domain(1, n)));
    store.push_back(model.NewIntVar(Domain(1, n)));
  }
  const IntVar &ecruespadrilles = shoes[0], &fuchsiaflats = shoes[1], &purplepumps = shoes[2],
               &suedesandals = shoes[3];
  const IntVar &footfarm = store[0], &heelsinahandcart = store[1], &theshoepalace = store[2],
               &tootsies = store[3];

  // One pair of shoes and one store per stop.
  model.AddAllDifferent(shoes);
  model.AddAllDifferent(store);

  // 1. Harriet bought fuchsia flats at Heels in a Handcart.
  model.AddEquality(fuchsiaflats, heelsinahandcart);
  // 2. The store she visited just after buying her purple pumps was not Tootsies.
  model.AddNotEqual(purplepumps + 1, tootsies);
  // 3. The Foot Farm was Harriet's second stop.
  model.AddEquality(footfarm, 2);
  // 4. Two stops after leaving The Shoe Palace, Harriet bought her suede sandals.
  model.AddEquality(theshoepalace + 2, suedesandals);

  outputs = {{"ecruespadrilles", ecruespadrilles.index()},
             {"fuchsiaflats", fuchsiaflats.index()},
             {"purplepumps", purplepumps.index()},
             {"suedesandals", suedesandals.index()},
             {"footfarm", footfarm.index()},
             {"heelsinahandcart", heelsinahandcart.index()},
             {"theshoepalace", theshoepalace.index()},
             {"tootsies", tootsies.index()}};
}
