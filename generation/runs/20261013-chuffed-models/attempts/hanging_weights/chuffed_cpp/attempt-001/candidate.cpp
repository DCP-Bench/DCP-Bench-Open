// Hanging weights: weights a..m (each an integer 1..13) hang from a system of bars and
// must balance as drawn. The weights on either side of a given pivot point must be equal,
// when weighted by the distance from the pivot, and a bar hanging beneath another
// contributes its total weight as though it were a single weight.
// Reading the diagram: each bar hangs from the pivot under the '|' above it. Pivots and
// weight positions sit on the '+' columns, and arms are measured in units of 3 characters.
// Where the drawn '|' is one column off a '+', the pivot is the '+' it lands on.
#include "dcp.h"

// posts sum_i c[i] * x[i] == 0
static void torque_eq(const std::vector<int>& c, const std::vector<IntVar*>& x) {
  vec<int> cv;
  vec<IntVar*> xv;
  for (int v : c) cv.push(v);
  for (IntVar* v : x) xv.push(v);
  int_linear(cv, xv, IRT_EQ, 0);
}

void Build(const json& instance, json& outputs) {
  IntVar* a = newIntVar(1, 13);
  IntVar* b = newIntVar(1, 13);
  IntVar* c = newIntVar(1, 13);
  IntVar* d = newIntVar(1, 13);
  IntVar* e = newIntVar(1, 13);
  IntVar* f = newIntVar(1, 13);
  IntVar* g = newIntVar(1, 13);
  IntVar* h = newIntVar(1, 13);
  IntVar* i = newIntVar(1, 13);
  IntVar* j = newIntVar(1, 13);
  IntVar* k = newIntVar(1, 13);
  IntVar* l = newIntVar(1, 13);
  IntVar* m = newIntVar(1, 13);

  // total weight carried by each bar (its own weights plus the bars hanging beneath it)
  IntVar* wAB = newIntVar(2, 26);  // bar with A and B
  torque_eq({1, 1, -1}, {a, b, wAB});
  IntVar* wR = newIntVar(2, 26);   // bottom right bar with C and D
  torque_eq({1, 1, -1}, {c, d, wR});
  IntVar* wG = newIntVar(3, 52);   // bar with G and the bottom right bar
  torque_eq({1, 1, -1}, {g, wR, wG});
  IntVar* wEF = newIntVar(2, 26);  // bar with E and F
  torque_eq({1, 1, -1}, {e, f, wEF});
  IntVar* wH = newIntVar(3, 52);   // bar with H and I, carrying the E-F bar
  torque_eq({1, 1, 1, -1}, {h, wEF, i, wH});
  IntVar* wP = newIntVar(3, 78);   // bar with L and M, carrying the H bar
  torque_eq({1, 1, 1, -1}, {wH, l, m, wP});
  IntVar* wQ = newIntVar(3, 130);  // bar with J and K, carrying the A-B bar and the G bar
  torque_eq({1, 1, 1, 1, -1}, {j, k, wAB, wG, wQ});

  // (1) bottom right bar, pivot at column 44: C at 29 has arm 5, D at 47 has arm 1
  torque_eq({5, -1}, {c, d});
  // bar with G, pivot at column 38: G at 29 has arm 3, the bottom right bar at 44 has arm 2
  torque_eq({3, -2}, {g, wR});
  // bar with A and B, pivot at column 23: A at 11 has arm 4, B at 26 has arm 1
  torque_eq({4, -1}, {a, b});
  // bar with E and F, pivot at column 14: E at 5 has arm 3, F at 20 has arm 2
  torque_eq({3, -2}, {e, f});
  // bar with H and I, pivot at column 9: H at 0 has arm 3, the E-F bar at 15 has arm 2, I at 18 has arm 3
  torque_eq({3, -2, -3}, {h, wEF, i});
  // bar with L and M, pivot at column 11: the H bar at 8 has arm 1, L at 14 has arm 1, M at 23 has arm 4
  torque_eq({1, -1, -4}, {wH, l, m});
  // bar with J and K, pivot at column 33: the A-B bar at 24 has arm 3, J at 27 has arm 2,
  // K at 36 has arm 1, the G bar at 39 has arm 2
  torque_eq({3, 2, -1, -2}, {wAB, j, k, wG});
  // top bar, pivot at column 23 from the ceiling: the L-M bar at 11 has arm 4, the J-K bar at 32 has arm 3
  torque_eq({4, -3}, {wP, wQ});

  // branch on the weights a..m
  vec<IntVar*> all;
  all.push(a); all.push(b); all.push(c); all.push(d); all.push(e); all.push(f); all.push(g);
  all.push(h); all.push(i); all.push(j); all.push(k); all.push(l); all.push(m);
  branch(all, VAR_INORDER, VAL_MIN);

  outputs = {{"a", dcp::out(a)}, {"b", dcp::out(b)}, {"c", dcp::out(c)}, {"d", dcp::out(d)},
             {"e", dcp::out(e)}, {"f", dcp::out(f)}, {"g", dcp::out(g)}, {"h", dcp::out(h)},
             {"i", dcp::out(i)}, {"j", dcp::out(j)}, {"k", dcp::out(k)}, {"l", dcp::out(l)},
             {"m", dcp::out(m)}};
}
