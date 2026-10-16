// csplib_018 water bucket: three buckets with capacities, start with all water in the
// first bucket. Pour water between buckets until the first two buckets hold the goal
// amounts, minimising the number of transfers. Output the transfer count and the
// sequence of states, padded with the padding value after the goal state.
#include <algorithm>
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  std::vector<int> cap = instance.at("capacities").get<std::vector<int>>();
  std::vector<int> init = instance.at("initial_state").get<std::vector<int>>();
  std::vector<int> goal = instance.at("goal_state").get<std::vector<int>>();
  int steps = instance.at("MAX_STEPS").get<int>();
  int pad = instance.at("PADDING_VALUE").get<int>();
  int nb = static_cast<int>(cap.size());
  int T = steps - 1;  // last state index; transfers go from state t to state t+1

  int maxcap = 0;
  for (int c : cap) maxcap = std::max(maxcap, c);
  double M = maxcap;             // big-M for pour and goal rows, from the capacities
  double M2 = maxcap - pad + 1;  // big-M for the output rows, from the capacities and padding

  // a[t] = 1 when state t is a real state of the path, 0 when it is padding.
  // The real states come first, so a is non-increasing and a[0] = 1.
  std::vector<dcp::Lin> a(steps);
  for (int t = 0; t < steps; ++t) a[t] = dcp::new_var(h, t == 0 ? 1 : 0, 1);
  // // the real states come first and the padding follows them
  for (int t = 0; t < T; ++t) dcp::add_row(h, a[t + 1] - a[t], -kHighsInf, 0);

  // v[t][k] = water in bucket k at state t, between 0 and its capacity.
  // State 0 is the initial state.
  std::vector<std::vector<dcp::Lin>> v(steps, std::vector<dcp::Lin>(nb));
  for (int t = 0; t < steps; ++t)
    for (int k = 0; k < nb; ++k)
      v[t][k] = (t == 0) ? dcp::new_var(h, init[k], init[k])
                         : dcp::new_var(h, 0, cap[k]);

  // p[t][i][j] = 1 when step t pours from bucket i to bucket j; q[t][i][j] = amount poured;
  // e[t][i][j] = 1 when the pour empties bucket i, 0 when it fills bucket j.
  std::vector<std::vector<std::vector<dcp::Lin>>> p(T, std::vector<std::vector<dcp::Lin>>(nb, std::vector<dcp::Lin>(nb)));
  auto q = p;
  auto e = p;
  for (int t = 0; t < T; ++t)
    for (int i = 0; i < nb; ++i)
      for (int j = 0; j < nb; ++j)
        if (i != j) {
          p[t][i][j] = dcp::new_var(h, 0, 1);
          q[t][i][j] = dcp::new_var(h, 0, maxcap);
          e[t][i][j] = dcp::new_var(h, 0, 1);
        }

  for (int t = 0; t < T; ++t) {
    // // a real transition moves water exactly once, and a padded step moves nothing
    dcp::Lin count;
    for (int i = 0; i < nb; ++i)
      for (int j = 0; j < nb; ++j)
        if (i != j) count = count + p[t][i][j];
    dcp::add_row(h, count - a[t + 1], 0, 0);

    for (int i = 0; i < nb; ++i)
      for (int j = 0; j < nb; ++j) {
        if (i == j) continue;
        const dcp::Lin& P = p[t][i][j];
        const dcp::Lin& Q = q[t][i][j];
        const dcp::Lin& E = e[t][i][j];
        // // no amount is poured when the pour is not chosen
        dcp::add_row(h, Q - M * P, -kHighsInf, 0);
        // // the amount poured cannot exceed what bucket i holds or what bucket j has room for
        dcp::add_row(h, Q - v[t][i] + M * P, -kHighsInf, M);
        dcp::add_row(h, Q + v[t][j] + M * P, -kHighsInf, cap[j] + M);
        // // a pour that empties bucket i pours exactly what bucket i holds
        dcp::add_row(h, Q - v[t][i] - M * E - M * P, -2 * M, kHighsInf);
        dcp::add_row(h, Q - v[t][i] + M * E + M * P, -kHighsInf, 2 * M);
        // // a pour that fills bucket j pours exactly its free room
        dcp::add_row(h, Q + v[t][j] + M * E - M * P, cap[j] - M, kHighsInf);
        dcp::add_row(h, Q + v[t][j] - M * E + M * P, -kHighsInf, cap[j] + M);
      }

    // // water is conserved: each bucket gains what flows in and loses what flows out
    for (int k = 0; k < nb; ++k) {
      dcp::Lin expr = v[t + 1][k] - v[t][k];
      for (int i = 0; i < nb; ++i)
        if (i != k) expr = expr - q[t][i][k];
      for (int j = 0; j < nb; ++j)
        if (j != k) expr = expr + q[t][k][j];
      dcp::add_row(h, expr, 0, 0);
    }
  }

  // // the last real state holds the goal amounts in every bucket
  for (int t = 0; t < steps; ++t) {
    dcp::Lin last = (t < T) ? (M * a[t] - M * a[t + 1]) : (M * a[t]);
    for (int k = 0; k < nb; ++k) {
      dcp::add_row(h, v[t][k] - goal[k] + last, -kHighsInf, M);
      dcp::add_row(h, goal[k] - v[t][k] + last, -kHighsInf, M);
    }
  }

  // // the output sequence copies each real state and shows the padding value after the goal
  std::vector<std::vector<dcp::Lin>> seq(steps, std::vector<dcp::Lin>(nb));
  for (int t = 0; t < steps; ++t)
    for (int k = 0; k < nb; ++k) {
      seq[t][k] = dcp::new_var(h, pad < 0 ? pad : 0, cap[k]);
      dcp::add_row(h, seq[t][k] - v[t][k] + M2 * a[t], -kHighsInf, M2);
      dcp::add_row(h, seq[t][k] - v[t][k] - M2 * a[t], -M2, kHighsInf);
      dcp::add_row(h, seq[t][k] - (cap[k] - pad) * a[t], -kHighsInf, pad);
    }

  // // the cost is the number of transfers, one for each real state after the initial one
  dcp::Lin cost;
  for (int t = 1; t < steps; ++t) cost = cost + a[t];
  out.minimize(cost);
  out.add("cost", cost);
  out.add("sequence", seq);
}
