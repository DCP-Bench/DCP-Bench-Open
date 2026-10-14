// Bank card PIN: find the 4-digit PIN abcd with distinct digits, where cd = 3 * ab and da = 2 * bc.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // a, b, c, d are the digits of the PIN
  IntVar* a = newIntVar(0, 9);
  IntVar* b = newIntVar(0, 9);
  IntVar* c = newIntVar(0, 9);
  IntVar* d = newIntVar(0, 9);

  // no two digits are the same
  vec<IntVar*> digits;
  digits.push(a);
  digits.push(b);
  digits.push(c);
  digits.push(d);
  all_different(digits);

  // the two-digit number cd is 3 times the two-digit number ab: 10c + d = 3 * (10a + b)
  vec<int> k1;
  k1.push(10);
  k1.push(1);
  k1.push(-30);
  k1.push(-3);
  vec<IntVar*> v1;
  v1.push(c);
  v1.push(d);
  v1.push(a);
  v1.push(b);
  int_linear(k1, v1, IRT_EQ, 0);

  // the two-digit number da is 2 times the two-digit number bc: 10d + a = 2 * (10b + c)
  vec<int> k2;
  k2.push(10);
  k2.push(1);
  k2.push(-20);
  k2.push(-2);
  vec<IntVar*> v2;
  v2.push(d);
  v2.push(a);
  v2.push(b);
  v2.push(c);
  int_linear(k2, v2, IRT_EQ, 0);

  // branch on the digits in PIN order
  vec<IntVar*> pin;
  pin.push(a);
  pin.push(b);
  pin.push(c);
  pin.push(d);
  branch(pin, VAR_INORDER, VAL_MIN);

  outputs = {{"a", dcp::out(a)}, {"b", dcp::out(b)}, {"c", dcp::out(c)}, {"d", dcp::out(d)}};
}
