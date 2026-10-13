// Even Fibonacci sum: the sum of the even-valued terms of the sequence 1, 2, 3, 5, 8, ... that do not
// exceed four million.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // the bound on the terms, from the problem statement
  const int LIMIT = 4000000;

  // the terms that do not exceed the limit: 1, 2, 3, 5, ... up to 3524578, which is the 32nd term
  const int TERMS = 32;

  // f[k] is the (k+1)-th term of the sequence; f[0] = 1 and f[1] = 2
  vec<IntVar*> f;
  createVars(f, TERMS, 1, LIMIT);
  int_rel(f[0], IRT_EQ, 1);
  int_rel(f[1], IRT_EQ, 2);

  // each term from the third on is the sum of the two terms before it
  for (int k = 2; k < TERMS; ++k) {
    vec<IntVar*> xs;
    xs.push(f[k - 1]);
    xs.push(f[k - 2]);
    xs.push(f[k]);
    vec<int> cs;
    cs.push(1);
    cs.push(1);
    cs.push(-1);
    int_linear(cs, xs, IRT_EQ, 0);
  }

  // the terms are determined by the first two, so the search only needs to see them
  vec<IntVar*> seeds;
  seeds.push(f[0]);
  seeds.push(f[1]);
  branch(seeds, VAR_INORDER, VAL_MIN);

  // even_part[k] is f[k] when that term is even and 0 otherwise
  vec<IntVar*> even_part;
  for (int k = 0; k < TERMS; ++k) {
    // f[k] = 2 * half + rem with rem in 0..1; the term is even exactly when rem = 0
    IntVar* half = newIntVar(0, LIMIT / 2);
    IntVar* rem = newIntVar(0, 1);
    vec<int> coef;
    coef.push(2);
    coef.push(1);
    vec<IntVar*> parts;
    parts.push(half);
    parts.push(rem);
    int_linear(coef, parts, IRT_EQ, f[k]);

    // is_even is true exactly when rem = 0
    BoolView is_even = newBoolVar();
    int_rel_reif(rem, IRT_EQ, 0, is_even);
    IntVar* is_even_int = newIntVar(0, 1);
    bool2int(is_even, is_even_int);

    // the term itself when even, 0 otherwise
    IntVar* part = newIntVar(0, LIMIT);
    int_times(f[k], is_even_int, part);
    even_part.push(part);
  }

  // res is the sum of the even terms that do not exceed the limit
  IntVar* res = newIntVar(0, 3 * LIMIT);
  vec<int> ones;
  for (int k = 0; k < TERMS; ++k) ones.push(1);
  int_linear(ones, even_part, IRT_EQ, res);

  outputs = {{"res", dcp::out(res)}};
}
