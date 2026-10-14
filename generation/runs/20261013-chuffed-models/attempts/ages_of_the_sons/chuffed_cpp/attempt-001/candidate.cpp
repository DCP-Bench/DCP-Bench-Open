// Ages of the sons: three ages with product 36, an ambiguous sum, and a unique oldest son.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // The old man's number from the statement: the product of the ages is 36.
  const int product = 36;

  // Sums that the mathematician cannot resolve: a sum shared by at least two
  // different age triples with product 36. Triples are listed as multisets (a >= b >= c).
  std::vector<int> triples_per_sum(3 * product + 1, 0);
  for (int a = 1; a <= product; ++a)
    for (int b = 1; b <= a; ++b)
      for (int c = 1; c <= b; ++c)
        if (a * b * c == product) triples_per_sum[a + b + c]++;

  // A1, A2, A3 are the ages of the sons, starting from the oldest
  vec<IntVar*> ages;
  createVars(ages, 3, 1, product);
  IntVar* A1 = ages[0];
  IntVar* A2 = ages[1];
  IntVar* A3 = ages[2];

  // ages are listed from the oldest to the youngest
  int_rel(A1, IRT_GE, A2);
  int_rel(A2, IRT_GE, A3);

  // the product of their ages is 36
  IntVar* p12 = newIntVar(1, product);
  int_times(A1, A2, p12);
  IntVar* p123 = newIntVar(1, product);
  int_times(p12, A3, p123);
  int_rel(p123, IRT_EQ, product);

  // the sum of their ages is the number of windows; the mathematician still needs
  // more information, so that sum is shared by several possible triples
  IntVar* windows;
  createVar(windows, 3, 3 * product, true);
  int_linear(ages, IRT_EQ, windows);
  for (int s = 3; s <= 3 * product; ++s)
    if (triples_per_sum[s] < 2) int_rel(windows, IRT_NE, s);

  // the oldest son has blue eyes, so there is a single oldest son
  int_rel(A1, IRT_GT, A2);

  branch(ages, VAR_INORDER, VAL_MIN);
  outputs = {{"A1", dcp::out(A1)}, {"A2", dcp::out(A2)}, {"A3", dcp::out(A3)}};
}
