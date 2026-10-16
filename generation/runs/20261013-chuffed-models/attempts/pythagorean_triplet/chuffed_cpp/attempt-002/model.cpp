// Pythagorean triplet: find natural numbers a < b < c with a^2 + b^2 = c^2 and a + b + c = 1000.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // the perimeter of the triangle, from the problem statement
  const int SUM = 1000;

  // a, b, c are the three sides, each at most the perimeter
  IntVar* a = newIntVar(1, SUM);
  IntVar* b = newIntVar(1, SUM);
  IntVar* c = newIntVar(1, SUM);

  // the three numbers are in increasing order (a < b < c)
  int_rel(a, IRT_LT, b);
  int_rel(b, IRT_LT, c);

  // a + b + c = 1000
  vec<IntVar*> sides;
  sides.push(a);
  sides.push(b);
  sides.push(c);
  vec<int> ones;
  ones.push(1);
  ones.push(1);
  ones.push(1);
  int_linear(ones, sides, IRT_EQ, SUM);

  // the squares of the sides
  IntVar* a2 = newIntVar(1, SUM * SUM);
  IntVar* b2 = newIntVar(1, SUM * SUM);
  IntVar* c2 = newIntVar(1, SUM * SUM);
  int_times(a, a, a2);
  int_times(b, b, b2);
  int_times(c, c, c2);

  // a^2 + b^2 = c^2
  vec<IntVar*> squares;
  squares.push(a2);
  squares.push(b2);
  vec<int> ones2;
  ones2.push(1);
  ones2.push(1);
  int_linear(ones2, squares, IRT_EQ, c2);

  branch(sides, VAR_INORDER, VAL_MIN);

  outputs = {{"a", dcp::out(a)}, {"b", dcp::out(b)}, {"c", dcp::out(c)}};
}
