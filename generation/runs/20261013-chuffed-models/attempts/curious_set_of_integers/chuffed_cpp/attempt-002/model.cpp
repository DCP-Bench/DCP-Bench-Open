// Curious set of integers: find a number >= 0 that can be added to the set {1, 3, 8, 120} so that the
// product of any two integers of the set is still one less than a perfect square.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int max_val = instance.at("max_val");
  // the numbers already in the set (given in the problem statement, not an instance field)
  const int kSet[4] = {1, 3, 8, 120};

  // the number to add
  IntVar* number = newIntVar(0, max_val);

  // the product of the new number with each number of the set is one less than a perfect square:
  // number * k + 1 = root^2
  for (int k : kSet) {
    // the root is at most sqrt(max_val * k + 1)
    int bound = 1;
    while (bound * bound < max_val * k + 1) ++bound;
    IntVar* root = newIntVar(0, bound);
    IntVar* square = newIntVar(0, bound * bound);
    int_times(root, root, square);
    // k * number - square = -1
    vec<int> coef;
    vec<IntVar*> terms;
    coef.push(k);
    terms.push(number);
    coef.push(-1);
    terms.push(square);
    int_linear(coef, terms, IRT_EQ, -1);
  }
  vec<IntVar*> decisions;
  decisions.push(number);
  branch(decisions, VAR_INORDER, VAL_MIN);
  outputs = {{"number", dcp::out(number)}};
}
