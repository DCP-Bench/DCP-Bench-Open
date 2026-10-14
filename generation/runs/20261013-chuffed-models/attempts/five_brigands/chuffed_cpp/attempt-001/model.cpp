// Five brigands: find whole doubloon counts A, B, C, D, E for Alfonso, Benito, Carlos,
// Diego and Esteban, each at least 1, that fit the two statements of the puzzle.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // A, B, C, D, E are the doubloons of Alfonso, Benito, Carlos, Diego and Esteban;
  // no brigand had less than one doubloon, and the upper bound follows from the total
  IntVar* A = newIntVar(1, 200);
  IntVar* B = newIntVar(1, 200);
  IntVar* C = newIntVar(1, 200);
  IntVar* D = newIntVar(1, 200);
  IntVar* E = newIntVar(1, 200);

  vec<IntVar*> v;
  v.push(A); v.push(B); v.push(C); v.push(D); v.push(E);

  // together they had exactly 200 doubloons
  vec<int> ones;
  ones.push(1); ones.push(1); ones.push(1); ones.push(1); ones.push(1);
  int_linear(ones, v, IRT_EQ, 200);

  // with Alfonso's twelve times, Benito's three times, Carlos's same, Diego's half and
  // Esteban's one-third, the total is still 200: 12A + 3B + C + D/2 + E/3 = 200.
  // Multiplied by 6 to keep the coefficients integer: 72A + 18B + 6C + 3D + 2E = 1200
  vec<int> scaled;
  scaled.push(72); scaled.push(18); scaled.push(6); scaled.push(3); scaled.push(2);
  int_linear(scaled, v, IRT_EQ, 1200);

  // branch on the holdings in order, smallest value first
  branch(v, VAR_INORDER, VAL_MIN);

  outputs = {{"A", dcp::out(A)}, {"B", dcp::out(B)}, {"C", dcp::out(C)},
             {"D", dcp::out(D)}, {"E", dcp::out(E)}};
}
