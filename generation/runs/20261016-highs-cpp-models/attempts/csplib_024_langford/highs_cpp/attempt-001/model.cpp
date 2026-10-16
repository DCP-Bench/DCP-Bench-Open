// csplib_024_langford: Langford's problem. Two copies of each number 1..k are
// arranged in one sequence of 2k positions so that the two 1's are one number
// apart, the two 2's are two numbers apart, ..., and the two k's are k numbers
// apart. Output sol lists the sequence of 2k numbers.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int k = instance.at("k").get<int>();
  int N = 2 * k;

  // Placement of number i: start[i][p] = 1 means the first copy of i is at
  // position p (0-based) and the second copy is at position p + i + 1.
  // The second copy must stay inside the sequence, so p runs over 0..N-2-i.
  std::vector<std::vector<dcp::Lin>> start(k + 1);
  for (int i = 1; i <= k; i++) {
    for (int p = 0; p + i + 1 <= N - 1; p++) {
      start[i].push_back(dcp::new_var(h, 0, 1));
    }
  }

  // each number is placed exactly once: exactly one start position is chosen
  for (int i = 1; i <= k; i++) {
    dcp::Lin placed;
    for (const auto& b : start[i]) placed = placed + b;
    dcp::add_row(h, placed, 1, 1);
  }

  // every position of the sequence holds exactly one copy of some number:
  // a position q is taken by the first copy of i when start[i][q] = 1, and by
  // the second copy of i when start[i][q - i - 1] = 1
  std::vector<dcp::Lin> sol(N);
  for (int q = 0; q < N; q++) {
    dcp::Lin taken;
    for (int i = 1; i <= k; i++) {
      if (q < (int)start[i].size()) {
        taken = taken + start[i][q];
        sol[q] = sol[q] + static_cast<double>(i) * start[i][q];
      }
      int p = q - i - 1;
      if (p >= 0 && p < (int)start[i].size()) {
        taken = taken + start[i][p];
        sol[q] = sol[q] + static_cast<double>(i) * start[i][p];
      }
    }
    dcp::add_row(h, taken, 1, 1);
  }

  // the reported sequence: the number occupying each position
  out.add("sol", sol);
}
