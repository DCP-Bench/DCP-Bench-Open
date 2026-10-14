#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// General store cryptarithm: each letter is a different digit, and the sixteen
// words CHESS, CASH, BOWWOW, CHOPS, ALSOPS, PALEALE, COOL, BASS, HOPS, ALES,
// HOES, APPLES, COWS, CHEESE, CHSOAP and SHEEP add up to ALLWOOL.
// The problem has no instance data: the words are the puzzle.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  std::vector<IntVar> x;
  for (int i = 0; i < 10; ++i) x.push_back(model.NewIntVar(Domain(0, 9)));
  const IntVar &C = x[0], &H = x[1], &E = x[2], &S = x[3], &A = x[4], &B = x[5], &O = x[6],
               &W = x[7], &P = x[8], &L = x[9];

  // Each different letter stands for a different digit.
  model.AddAllDifferent(x);

  // The value of a word read as a decimal number, most significant letter first.
  auto word = [](const std::vector<IntVar>& letters) {
    LinearExpr value;
    for (const IntVar& letter : letters) value = 10 * value + letter;
    return value;
  };

  // The words above the line add to ALLWOOL.
  LinearExpr sum;
  sum += word({C, H, E, S, S});
  sum += word({C, A, S, H});
  sum += word({B, O, W, W, O, W});
  sum += word({C, H, O, P, S});
  sum += word({A, L, S, O, P, S});
  sum += word({P, A, L, E, A, L, E});
  sum += word({C, O, O, L});
  sum += word({B, A, S, S});
  sum += word({H, O, P, S});
  sum += word({A, L, E, S});
  sum += word({H, O, E, S});
  sum += word({A, P, P, L, E, S});
  sum += word({C, O, W, S});
  sum += word({C, H, E, E, S, E});
  sum += word({C, H, S, O, A, P});
  sum += word({S, H, E, E, P});
  model.AddEquality(sum, word({A, L, L, W, O, O, L}));

  outputs = {{"C", C.index()}, {"H", H.index()}, {"E", E.index()}, {"S", S.index()},
             {"A", A.index()}, {"B", B.index()}, {"O", O.index()}, {"W", W.index()},
             {"P", P.index()}, {"L", L.index()}};
}
