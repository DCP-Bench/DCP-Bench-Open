#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Circling the squares (Dudeney): place ten different numbers A..K around a
// circle so that, for any two adjacent numbers, the sum of their squares
// equals the sum of the squares of the two numbers diametrically opposite.
// A = 16, B = 2, F = 8 and G = 14 are given by the puzzle.
// The problem has no instance data: the givens and the 1..99 range ("no
// number need contain more than two figures") are part of the puzzle.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int n = 10;
  std::vector<IntVar> x, sq;
  for (int i = 0; i < n; ++i) {
    x.push_back(model.NewIntVar(Domain(1, 99)));
    // sq[i] is x[i] squared.
    sq.push_back(model.NewIntVar(Domain(1, 99 * 99)));
    model.AddMultiplicationEquality(sq[i], {x[i], x[i]});
  }
  enum { A, B, C, D, E, F, G, H, I, K };

  // All numbers are different.
  model.AddAllDifferent(x);

  // The four numbers given in the puzzle.
  model.AddEquality(x[A], 16);
  model.AddEquality(x[B], 2);
  model.AddEquality(x[F], 8);
  model.AddEquality(x[G], 14);

  // Adjacent pair (p, q) and opposite pair (r, s) have equal sums of squares.
  auto same_squares = [&](int p, int q, int r, int s) {
    model.AddEquality(sq[p] + sq[q], sq[r] + sq[s]);
  };
  same_squares(A, B, F, G);
  same_squares(B, C, G, H);
  same_squares(C, D, H, I);
  same_squares(D, E, I, K);
  same_squares(E, F, K, A);

  outputs = {{"A", x[A].index()}, {"B", x[B].index()}, {"C", x[C].index()}, {"D", x[D].index()},
             {"E", x[E].index()}, {"F", x[F].index()}, {"G", x[G].index()}, {"H", x[H].index()},
             {"I", x[I].index()}, {"K", x[K].index()}};
}
