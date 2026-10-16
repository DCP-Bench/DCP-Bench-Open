// Cutting stock problem: raw rolls of one width are cut into pieces of several widths.
// Each cutting pattern says how many pieces of each width one roll gives. Choose how many
// rolls to cut with each pattern so that, for each width, the pieces cut meet the orders,
// and minimise the total number of raw rolls cut.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  // Instance data: the orders per width, the number of patterns, and the count of each
  // width that one roll of each pattern yields (num_rolls_width[pattern][width]).
  const json& orders = instance.at("orders");
  const json& rolls_width = instance.at("num_rolls_width");
  int num_patterns = instance.at("num_patterns");
  int num_widths = orders.size();

  // Bound on the rolls cut with one pattern: the total of all orders. Any more rolls of a
  // pattern than that can be dropped and every width still gets at least its orders.
  double total_orders = 0;
  for (int w = 0; w < num_widths; ++w) total_orders += orders[w].get<double>();

  // patterns_used[p]: number of rolls cut with pattern p (integer, 0 .. total orders).
  std::vector<dcp::Lin> patterns_used;
  for (int p = 0; p < num_patterns; ++p) patterns_used.push_back(dcp::new_var(h, 0, total_orders));

  // For each width, the pieces of that width cut from all rolls meet its orders.
  for (int w = 0; w < num_widths; ++w) {
    // the pieces of this width cut from all the patterns meet the orders of this width
    dcp::Lin pieces;
    for (int p = 0; p < num_patterns; ++p)
      pieces = pieces + rolls_width[p][w].get<double>() * patterns_used[p];
    dcp::add_row(h, pieces, orders[w].get<double>(), kHighsInf);
  }

  // the total number of raw rolls cut is the sum over all patterns
  dcp::Lin min_rolls_cut;
  for (int p = 0; p < num_patterns; ++p) min_rolls_cut = min_rolls_cut + patterns_used[p];

  out.add("patterns_used", patterns_used);
  out.add("min_rolls_cut", min_rolls_cut);
  out.minimize(min_rolls_cut);
}
