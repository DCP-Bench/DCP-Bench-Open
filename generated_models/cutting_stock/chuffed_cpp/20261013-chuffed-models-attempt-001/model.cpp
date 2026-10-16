// Cutting stock: cut raw rolls of a fixed width into pieces of the ordered widths, using a set of
// cutting patterns, so that the total number of raw rolls cut is minimal.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> widths = instance.at("widths").get<std::vector<int>>();
  std::vector<int> orders = instance.at("orders").get<std::vector<int>>();
  std::vector<std::vector<int>> pattern = instance.at("num_rolls_width").get<std::vector<std::vector<int>>>();
  int num_patterns = instance.at("num_patterns");
  int num_widths = static_cast<int>(widths.size());

  // total of all orders: an upper bound on how many times any pattern can be used
  int total_orders = 0;
  for (int o : orders) total_orders += o;

  // used[p] is how many raw rolls are cut with pattern p
  vec<IntVar*> used;
  createVars(used, num_patterns, 0, total_orders);

  // pieces of width w produced by all patterns together must meet the order for width w
  for (int w = 0; w < num_widths; ++w) {
    // the number of pieces of width w that pattern p gives is pattern[p][w]
    vec<int> per_roll;
    vec<IntVar*> rolls_used;
    for (int p = 0; p < num_patterns; ++p) {
      per_roll.push(pattern[p][w]);
      rolls_used.push(used[p]);
    }
    // the pieces of width w cut from all rolls must be at least the ordered number of pieces
    int_linear(per_roll, rolls_used, IRT_GE, orders[w]);
  }

  // the total number of raw rolls cut is the sum over the patterns, and this is what is minimized
  vec<int> ones;
  for (int p = 0; p < num_patterns; ++p) ones.push(1);
  IntVar* min_rolls_cut = newIntVar(0, total_orders);
  int_linear(ones, used, IRT_EQ, min_rolls_cut);

  // decide the pattern counts first
  branch(used, VAR_INORDER, VAL_MIN);
  optimize(min_rolls_cut, OPT_MIN);

  json uses = json::array();
  for (int p = 0; p < num_patterns; ++p) uses.push_back(dcp::out(used[p]));
  outputs = {{"min_rolls_cut", dcp::out(min_rolls_cut)}, {"patterns_used", uses}};
}
