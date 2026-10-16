// Bus driver scheduling: select a set of shifts so that every piece of work is covered by exactly one
// selected shift, minimizing the number of selected shifts.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int num_work = instance.at("num_work");
  int num_shifts = instance.at("num_shifts");
  // shifts[j] lists the pieces of work (0-based) that shift j covers; the lists have different lengths
  std::vector<std::vector<int>> shifts = instance.at("shifts").get<std::vector<std::vector<int>>>();

  // x[j] = 1 if shift j is selected
  vec<IntVar*> x;
  createVars(x, num_shifts, 0, 1, true);

  // every piece of work is covered by exactly one selected shift
  for (int w = 0; w < num_work; ++w) {
    vec<IntVar*> covering;
    for (int j = 0; j < num_shifts; ++j) {
      for (int piece : shifts[j]) {
        if (piece == w) {
          covering.push(x[j]);
          break;
        }
      }
    }
    int_linear(covering, IRT_EQ, 1);
  }

  // the cost is the number of selected shifts (all shifts cost the same)
  IntVar* cost = newIntVar(0, num_shifts);
  int_linear(x, IRT_EQ, cost);
  optimize(cost, OPT_MIN);

  branch(x, VAR_INORDER, VAL_MIN);

  json flags = json::array();
  for (int j = 0; j < num_shifts; ++j) flags.push_back(dcp::out(x[j]));
  outputs = {{"x", flags}};
}
