#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");
  IntVar* x = newIntVar(0, n);
  IntVar* y = newIntVar(0, n);
  vec<IntVar*> terms;
  terms.push(x);
  terms.push(y);
  if (instance.at("optimize").get<bool>()) {
    IntVar* total = newIntVar(0, 2 * n);
    int_linear(terms, IRT_EQ, total);
    int_rel(total, IRT_GE, n);
    optimize(total, OPT_MIN);
  } else {
    int_linear(terms, IRT_EQ, n);
  }
  outputs = {{"x", dcp::out(x)}, {"y", dcp::out(y)}};
}
