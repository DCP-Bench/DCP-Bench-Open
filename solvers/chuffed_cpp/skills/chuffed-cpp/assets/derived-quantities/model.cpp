// Three numbers 0..n and quantities derived from them: absolute difference, extremes, a
// count, a reified comparison, a weighted sum, a 2-D table lookup and a lexicographic order.
// Every intermediate is its own IntVar posted with a constraint: Chuffed has no expressions.
// Usage: model [n]   (default 4)
#include <chuffed/branching/branching.h>
#include <chuffed/core/engine.h>
#include <chuffed/core/options.h>
#include <chuffed/globals/globals.h>
#include <chuffed/primitives/primitives.h>
#include <chuffed/support/vec.h>
#include <chuffed/vars/int-var.h>
#include <chuffed/vars/modelling.h>

#include <cstdlib>
#include <iostream>
#include <ostream>

class Derived : public Problem {
 public:
  vec<IntVar*> x;
  IntVar *ad, *hi, *lo3, *cnt, *lti, *wsum, *val;

  explicit Derived(int n) {
    createVars(x, 3, 0, n, true);

    // ad is the absolute difference between the first two numbers
    IntVar* diff = newIntVar(-n, n);
    int_minus(x[0], x[1], diff);
    ad = newIntVar(0, n);
    int_abs(diff, ad);

    // hi is the largest and lo the smallest of the three numbers
    hi = newIntVar(0, n);
    maximum(x, hi);
    IntVar* lo = newIntVar(0, n);
    int_min(x[0], x[1], lo);   // pairwise
    lo3 = newIntVar(0, n);
    int_min(lo, x[2], lo3);

    // cnt is how many of the numbers equal 2
    vec<IntVar*> ind;
    for (int i = 0; i < 3; ++i) {
      BoolView b = newBoolVar();
      int_rel_reif(x[i], IRT_EQ, 2, b);
      IntVar* bi = newIntVar(0, 1);
      bool2int(b, bi);
      ind.push(bi);
    }
    cnt = newIntVar(0, 3);
    int_linear(ind, IRT_EQ, cnt);

    // lt is 1 exactly when the first number is smaller than the second
    BoolView lt = newBoolVar();
    int_rel_reif(x[0], IRT_LT, x[1], lt);
    lti = newIntVar(0, 1);
    bool2int(lt, lti);

    // if the first number is smaller than the second, the third is at least 3
    int_rel_half_reif(x[2], IRT_GE, 3, lt);

    // the weighted sum x0 + 2*x1 + 3*x2 may not exceed 14, and wsum records it
    vec<int> coef; coef.push(1); coef.push(2); coef.push(3);
    int_linear(coef, x, IRT_LE, 14);
    wsum = newIntVar(0, 6 * n);
    int_linear(coef, x, IRT_EQ, wsum);

    // val is the entry of a 3 x 3 table at row x0, column x1 (flattened row-major)
    int T[3][3] = {{5, 1, 4}, {2, 7, 0}, {3, 6, 8}};
    vec<int> flat;
    for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) flat.push(T[i][j]);
    IntVar* r = newIntVar(0, 2);
    IntVar* c = newIntVar(0, 2);
    int_rel(r, IRT_EQ, x[0], 0);  // r == x0 (so x0 <= 2)
    IntVar* idx = newIntVar(0, 8);
    vec<int> w3; w3.push(3); w3.push(1);
    vec<IntVar*> rc; rc.push(r); rc.push(c);
    int_linear(w3, rc, IRT_EQ, idx);
    val = newIntVar(0, 8);
    array_int_element(idx, flat, val);
    int_rel(c, IRT_EQ, x[1], 0);

    // (x0, x1) must not come after (x2, x1) in lexicographic order
    vec<IntVar*> la, lb; la.push(x[0]); la.push(x[1]); lb.push(x[2]); lb.push(x[1]);
    lex(la, lb, false);

    branch(x, VAR_INORDER, VAL_MIN);
    output_vars(x);  // solutions differ in x; needed to enumerate several
  }

  void print(std::ostream& os) override {
    os << "x = " << x[0]->getVal() << ' ' << x[1]->getVal() << ' ' << x[2]->getVal()
       << ", ad = " << ad->getVal() << ", hi = " << hi->getVal() << ", lo = " << lo3->getVal()
       << ", cnt = " << cnt->getVal() << ", lt = " << lti->getVal()
       << ", wsum = " << wsum->getVal() << ", val = " << val->getVal() << "\n";
  }
};

int main(int argc, char** argv) {
  int n = argc > 1 ? std::atoi(argv[1]) : 4;
  so.print_sol = true;
  so.nof_solutions = 3;  // the first three solutions (default 1, 0 = all)
  engine.solve(new Derived(n));
  std::cout << "solutions " << engine.solutions << std::endl;
  return 0;
}
