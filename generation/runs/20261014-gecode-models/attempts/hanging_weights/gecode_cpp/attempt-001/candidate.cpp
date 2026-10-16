#include "dcp.h"

// Hanging weights: assign each weight A-M an integer value in 1..13 so that every
// bar of the hanging system balances (weights on either side of a pivot, weighted
// by distance from the pivot, are equal). A bar hanging beneath another contributes
// its total weight as one weight.
// Distances are in units of three characters of the diagram. Output letters a..m
// stand for weights A..M.
class HangingWeights : public dcp::Space {
 protected:
  IntVarArray w;  // w[0..12] = weights A..M

 public:
  explicit HangingWeights(const json& instance) {
    (void)instance;  // the puzzle has no instance data
    w = IntVarArray(*this, 13, 1, 13);
    IntVar A = w[0], B = w[1], C = w[2], D = w[3], E = w[4], F = w[5], G = w[6],
           H = w[7], I = w[8], J = w[9], K = w[10], L = w[11], M = w[12];

    // bottom right bar: C hangs 5 units from its pivot, D hangs 1 unit
    rel(*this, 5 * C == D);

    // the bar above it: G hangs 3 units from its pivot, the C+D bar hangs 2 units
    rel(*this, 3 * G == 2 * C + 2 * D);

    // bottom left bar: A hangs 4 units from its pivot, B hangs 1 unit
    rel(*this, 4 * A == B);

    // bar holding E and F: E hangs 3 units from its pivot, F hangs 2 units
    rel(*this, 3 * E == 2 * F);

    // bar holding H and I, with the E-F bar hanging 2 units from the pivot:
    // H and I hang 3 units from the pivot on either side
    rel(*this, 3 * H == 3 * I + 2 * E + 2 * F);

    // bar holding L and M, with the H-I-E-F subtree hanging 1 unit to the left:
    // L hangs 1 unit to the right, M hangs 4 units to the right
    rel(*this, H + I + E + F == L + 4 * M);

    // top bar: the L-M subtree hangs 4 units left of the pivot, the J-K-A-B-G-C-D
    // subtree hangs 3 units right of it
    rel(*this, 4 * (L + M + H + I + E + F) == 3 * (A + B + J + K + G + C + D));

    // bar holding J and K, with the A-B bar 3 units left of its pivot and the G bar
    // 2 units right: J hangs 2 units left, K hangs 1 unit right
    rel(*this, 3 * (A + B) + 2 * J == K + 2 * (G + C + D));

    branch(*this, w, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("a", A);
    output("b", B);
    output("c", C);
    output("d", D);
    output("e", E);
    output("f", F);
    output("g", G);
    output("h", H);
    output("i", I);
    output("j", J);
    output("k", K);
    output("l", L);
    output("m", M);
  }

  HangingWeights(HangingWeights& s) : dcp::Space(s) { w.update(*this, s.w); }
  Gecode::Space* copy() override { return new HangingWeights(*this); }
};

DCP_MODEL(HangingWeights)
