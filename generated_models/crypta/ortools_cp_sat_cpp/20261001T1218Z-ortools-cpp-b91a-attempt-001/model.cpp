#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Cryptarithm: solve
//     BAIJJAJIIAHFCFEBBJEA
//   + DHFGABCDIDBIFFAGFEJE
//   = GJEGACDDHFAFJBFIHEEF
// where the letters stand for distinct digits and no number starts with 0.
// The addition is split into three column blocks of 7, 7 and 6 digits, with
// carries Sr1 and Sr2 between them.
// The problem has no instance data: the sum is part of the puzzle.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  std::vector<IntVar> LD;
  for (int i = 0; i < 10; ++i) LD.push_back(model.NewIntVar(Domain(0, 9)));
  const IntVar &A = LD[0], &B = LD[1], &C = LD[2], &D = LD[3], &E = LD[4], &F = LD[5],
               &G = LD[6], &H = LD[7], &I = LD[8], &J = LD[9];
  // Carries out of the lowest and the middle block.
  const IntVar Sr1 = model.NewIntVar(Domain(0, 1));
  const IntVar Sr2 = model.NewIntVar(Domain(0, 1));

  // All letters are distinct digits.
  model.AddAllDifferent(LD);

  // The leading letters B, D and G are not zero.
  model.AddGreaterOrEqual(B, 1);
  model.AddGreaterOrEqual(D, 1);
  model.AddGreaterOrEqual(G, 1);

  // Lowest seven columns: FEBBJEA + FAGFEJE = BFIHEEF, with the carry Sr1 going out.
  model.AddEquality(A + 10 * E + 100 * J + 1000 * B + 10000 * B + 100000 * E + 1000000 * F +
                        E + 10 * J + 100 * E + 1000 * F + 10000 * G + 100000 * A + 1000000 * F,
                    F + 10 * E + 100 * E + 1000 * H + 10000 * I + 100000 * F + 1000000 * B +
                        10000000 * Sr1);

  // Middle seven columns: JIIAHFC + CDIDBIF = DDHFAFJ, with the carry Sr1 coming in
  // and Sr2 going out.
  model.AddEquality(C + 10 * F + 100 * H + 1000 * A + 10000 * I + 100000 * I + 1000000 * J + F +
                        10 * I + 100 * B + 1000 * D + 10000 * I + 100000 * D + 1000000 * C + Sr1,
                    J + 10 * F + 100 * A + 1000 * F + 10000 * H + 100000 * D + 1000000 * D +
                        10000000 * Sr2);

  // Highest six columns: BAIJJA + DHFGAB = GJEGAC, with the carry Sr2 coming in and
  // no carry going out.
  model.AddEquality(A + 10 * J + 100 * J + 1000 * I + 10000 * A + 100000 * B + B + 10 * A +
                        100 * G + 1000 * F + 10000 * H + 100000 * D + Sr2,
                    C + 10 * A + 100 * G + 1000 * E + 10000 * J + 100000 * G);

  outputs = {{"A", A.index()}, {"B", B.index()}, {"C", C.index()}, {"D", D.index()},
             {"E", E.index()}, {"F", F.index()}, {"G", G.index()}, {"H", H.index()},
             {"I", I.index()}, {"J", J.index()}};
}
