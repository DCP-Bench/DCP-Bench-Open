// Five statements: each statement says "exactly k of these statements are false" for k = 1..5; find which are true.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // statement[k] is true (1) when exactly k+1 of the five statements are false
  vec<BoolView> statement;
  createVars(statement, 5);

  // the number of false statements; the five statements are either true or false, so it is 5 minus the number of true ones
  IntVar* falses = newIntVar(0, 5);

  // the number of true statements plus the number of false statements is 5
  vec<IntVar*> counts;
  vec<int> ones;
  for (int k = 0; k < 5; ++k) {
    IntVar* t = newIntVar(0, 1);
    bool2int(statement[k], t);
    counts.push(t);
    ones.push(1);
  }
  counts.push(falses);
  ones.push(1);
  int_linear(ones, counts, IRT_EQ, 5);

  // statement k+1 holds exactly when the number of false statements is k+1
  for (int k = 0; k < 5; ++k) {
    int_rel_reif(falses, IRT_EQ, k + 1, statement[k]);
  }

  // the answer is the 0/1 value of each statement, exported in the order of the statements
  branch(counts, VAR_INORDER, VAL_MIN);
  json st = json::array();
  for (int k = 0; k < 5; ++k) {
    IntVar* t = counts[k];
    st.push_back(dcp::out(t));
  }
  outputs = {{"statements", st}};
}
