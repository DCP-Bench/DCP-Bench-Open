// SEND + MORE = MONEY: assign a different digit to each letter so that the sum holds and the leading letters are not zero.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // the puzzle has no instance data; the digits of each letter are 0 to 9

  // one digit variable per letter, in the order s, e, n, d, m, o, r, y
  IntVar* s = newIntVar(0, 9);
  IntVar* e = newIntVar(0, 9);
  IntVar* n = newIntVar(0, 9);
  IntVar* d = newIntVar(0, 9);
  IntVar* m = newIntVar(0, 9);
  IntVar* o = newIntVar(0, 9);
  IntVar* r = newIntVar(0, 9);
  IntVar* y = newIntVar(0, 9);

  vec<IntVar*> letters;
  letters.push(s); letters.push(e); letters.push(n); letters.push(d);
  letters.push(m); letters.push(o); letters.push(r); letters.push(y);

  // each letter stands for a different digit
  all_different(letters);

  // the first letter of SEND and of MORE cannot be zero
  int_rel(s, IRT_NE, 0);
  int_rel(m, IRT_NE, 0);

  // SEND + MORE = MONEY, written as a column sum: 1000s + 100e + 10n + d + 1000m + 100o + 10r + e = 10000m + 1000o + 100n + 10e + y
  // collected on one side this is 1000s + 91e - 90n + d - 9000m - 900o + 10r - y = 0
  vec<int> coef;
  coef.push(1000); coef.push(91); coef.push(-90); coef.push(1);
  coef.push(-9000); coef.push(-900); coef.push(10); coef.push(-1);
  vec<IntVar*> terms;
  terms.push(s); terms.push(e); terms.push(n); terms.push(d);
  terms.push(m); terms.push(o); terms.push(r); terms.push(y);
  int_linear(coef, terms, IRT_EQ, 0);

  // search on the letters in the order they are written
  branch(letters, VAR_INORDER, VAL_MIN);

  outputs = {
    {"s", dcp::out(s)}, {"e", dcp::out(e)}, {"n", dcp::out(n)}, {"d", dcp::out(d)},
    {"m", dcp::out(m)}, {"o", dcp::out(o)}, {"r", dcp::out(r)}, {"y", dcp::out(y)}
  };
}
