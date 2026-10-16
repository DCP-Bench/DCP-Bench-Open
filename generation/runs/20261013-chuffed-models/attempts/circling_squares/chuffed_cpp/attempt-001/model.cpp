// Circling the squares: ten different numbers on a circle such that the sum of the squares of any
// two adjacent numbers equals the sum of the squares of the two numbers diametrically opposite.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // circle positions in order: A B C D E F G H I K (position i is opposite position i+5)
  const char* names[10] = {"A", "B", "C", "D", "E", "F", "G", "H", "I", "K"};

  // no number needs more than two figures, and fractions are not allowed
  vec<IntVar*> x;
  createVars(x, 10, 1, 99);

  // the four numbers given as examples stay as they are: A=16, B=2, F=8, G=14
  int_rel(x[0], IRT_EQ, 16);
  int_rel(x[1], IRT_EQ, 2);
  int_rel(x[5], IRT_EQ, 8);
  int_rel(x[6], IRT_EQ, 14);

  // a different number in each of the ten squares
  all_different(x);

  // the square of each number
  vec<IntVar*> sq;
  for (int i = 0; i < 10; ++i) {
    IntVar* s = newIntVar(1, 99 * 99);
    int_times(x[i], x[i], s);
    sq.push(s);
  }

  // the sum of the squares of any two adjacent numbers equals the sum of the squares of the two
  // numbers diametrically opposite to them
  for (int i = 0; i < 10; ++i) {
    vec<int> coef;
    vec<IntVar*> terms;
    coef.push(1);  terms.push(sq[i]);
    coef.push(1);  terms.push(sq[(i + 1) % 10]);
    coef.push(-1); terms.push(sq[(i + 5) % 10]);
    coef.push(-1); terms.push(sq[(i + 6) % 10]);
    int_linear(coef, terms, IRT_EQ, 0);
  }

  branch(x, VAR_INORDER, VAL_MIN);
  outputs = json::object();
  for (int i = 0; i < 10; ++i) outputs[names[i]] = dcp::out(x[i]);
}
