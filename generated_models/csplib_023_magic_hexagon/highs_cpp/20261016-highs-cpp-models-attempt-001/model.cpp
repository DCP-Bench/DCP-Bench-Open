// Magic hexagon (CSPLib 023): place the numbers 1..NUM_CELLS on the 19 cells A..S
// of a hexagon so that the sum of the numbers on each of the 15 lines is MAGIC_SUM.
// Output LD lists the values of A, B, ..., S in that order.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int n = instance.at("NUM_CELLS").get<int>();
  const int magic = instance.at("MAGIC_SUM").get<int>();
  const int cells = 19;  // the hexagon has 19 cells, A=0 ... S=18
  if (n != cells) throw std::runtime_error("the hexagon needs NUM_CELLS = 19");

  // y[i][v] = 1 when cell i takes the value v (v in 1..n).
  std::vector<std::vector<dcp::Lin>> y(cells, std::vector<dcp::Lin>(n + 1));
  std::vector<dcp::Lin> x(cells);
  for (int i = 0; i < cells; ++i) {
    for (int v = 1; v <= n; ++v) y[i][v] = dcp::new_var(h, 0, 1);
  }

  // every cell holds exactly one value
  for (int i = 0; i < cells; ++i) {
    // cell i is the value sum v * y[i][v]
    dcp::Lin value;
    dcp::Lin one_value;
    for (int v = 1; v <= n; ++v) {
      value = value + static_cast<double>(v) * y[i][v];
      one_value = one_value + y[i][v];
    }
    x[i] = value;
    dcp::add_row(h, one_value, 1, 1);
  }

  // every value is used by exactly one cell (all different, values 1..n)
  for (int v = 1; v <= n; ++v) {
    dcp::Lin users;
    for (int i = 0; i < cells; ++i) users = users + y[i][v];
    dcp::add_row(h, users, 1, 1);
  }

  // each of the 15 lines sums to the magic constant
  const std::vector<std::vector<int>> lines = {
      // horizontal rows
      {0, 1, 2},
      {3, 4, 5, 6},
      {7, 8, 9, 10, 11},
      {12, 13, 14, 15},
      {16, 17, 18},
      // one diagonal direction
      {7, 12, 16},
      {3, 8, 13, 17},
      {0, 4, 9, 14, 18},
      {1, 5, 10, 15},
      {2, 6, 11},
      // the other diagonal direction
      {0, 3, 7},
      {1, 4, 8, 12},
      {2, 5, 9, 13, 16},
      {6, 10, 14, 17},
      {11, 15, 18},
  };
  for (const auto& line : lines) {
    dcp::Lin sum;
    for (int i : line) sum = sum + x[i];
    dcp::add_row(h, sum, magic, magic);
  }

  out.add("LD", x);
}
