// Climbing stairs: climb a stair of n steps, taking between m1 and m2 steps
// at a time. steps[i] is the number of steps taken at move i; it is between
// m1 and m2, or 0 once the top of the stair is reached.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n").get<int>();
  int m1 = instance.at("m1").get<int>();
  int m2 = instance.at("m2").get<int>();

  // a move is taken (1) or not (0); a move of 0 steps is not taken
  // the smallest move that is taken is at least 1 step
  int lo = m1 > 1 ? m1 : 1;

  std::vector<dcp::Lin> steps;
  std::vector<dcp::Lin> taken;
  for (int i = 0; i < n; ++i) {
    steps.push_back(dcp::new_var(h, 0, m2));
    taken.push_back(dcp::new_var(h, 0, 1));
  }

  // a move takes between m1 and m2 steps when it is taken
  for (int i = 0; i < n; ++i) {
    // steps[i] >= lo when the move is taken, and 0 otherwise
    dcp::add_row(h, steps[i] - lo * taken[i], 0, kHighsInf);
    // steps[i] <= m2 when the move is taken, and 0 otherwise
    dcp::add_row(h, steps[i] - m2 * taken[i], -kHighsInf, 0);
  }

  // the moves after reaching the top are 0: once a move is not taken, later moves are not taken
  for (int i = 0; i + 1 < n; ++i) {
    dcp::add_row(h, taken[i] - taken[i + 1], 0, kHighsInf);
  }

  // the steps taken add up to the height of the stair
  dcp::Lin total;
  for (int i = 0; i < n; ++i) total = total + steps[i];
  dcp::add_row(h, total, n, n);

  out.add("steps", steps);
}
