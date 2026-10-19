// Three coins on a table, initially tails, heads, tails (1 = tails, 0 = heads).
// Make all coins face the same way in exactly num_moves moves, where each move
// flips one coin. Output steps[t][i]: the state of coin i after t moves
// (True = tails), so steps[0] is the initial state and steps[num_moves] is all equal.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const std::vector<int> init = instance.at("init").get<std::vector<int>>();
  const int moves = instance.at("num_moves").get<int>();
  const int n = static_cast<int>(init.size());

  // state[t][i]: coin i is tails after t moves (t = 0 is the initial state)
  std::vector<std::vector<dcp::Lin>> state(moves + 1, std::vector<dcp::Lin>(n));
  // flip[t][i]: coin i is flipped by move t (t from 1)
  std::vector<std::vector<dcp::Lin>> flip(moves + 1, std::vector<dcp::Lin>(n));

  // the initial state is the given one
  // initial state: coin i starts as init[i]
  for (int i = 0; i < n; i++) {
    state[0][i] = dcp::new_var(h, init[i], init[i]);
  }

  for (int t = 1; t <= moves; t++) {
    for (int i = 0; i < n; i++) {
      state[t][i] = dcp::new_var(h, 0, 1);
      flip[t][i] = dcp::new_var(h, 0, 1);
    }

    // each move flips exactly one coin
    // exactly one coin is flipped by move t
    dcp::Lin flips = flip[t][0];
    for (int i = 1; i < n; i++) flips = flips + flip[t][i];
    dcp::add_row(h, flips, 1, 1);

    // a coin flips its state: the new state is the old state XOR the flip,
    // written as a + c + f = 2k with k binary, so the sum is 0 or 2
    // the sum of old state, new state and flip is even
    for (int i = 0; i < n; i++) {
      dcp::Lin k = dcp::new_var(h, 0, 1);
      dcp::Lin parity = state[t - 1][i] + state[t][i] + flip[t][i] - 2.0 * k;
      dcp::add_row(h, parity, 0, 0);
    }
  }

  // all coins face the same way after the last move
  // the final coins all show the same face
  for (int i = 1; i < n; i++) {
    dcp::add_row(h, state[moves][i] - state[moves][0], 0, 0);
  }

  out.add("steps", state);
}
