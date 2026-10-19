// csplib_026 sports tournament scheduling: n teams play in n-1 weeks. Each week is divided
// into n/2 periods, and each period holds one match, whose two slots are the home and the
// away team. Every team plays once a week, every team plays at most twice in the same
// period over the tournament, and every team plays every other team.
#include <algorithm>

#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n_teams").get<int>();
  int W = n - 1;  // weeks
  int P = n / 2;  // periods per week

  // play[w][p][t] = 1 when team t plays in period p of week w.
  // meet[w][p][i][j] (i < j) = 1 when teams i and j are the match of period p of week w.
  // home[w][p][t] and away[w][p][t] = 1 when team t is the home or the away team there.
  auto slot = [&](int w, int p, int t) { return (w * P + p) * n + t; };
  auto meetIdx = [&](int w, int p, int i, int j) { return slot(w, p, 0) * n + i * n + j; };

  std::vector<dcp::Lin> play, home, away, meet(static_cast<std::size_t>(W * P * n * n));
  for (int k = 0; k < W * P * n; ++k) {
    play.push_back(dcp::new_var(h, 0, 1));
    home.push_back(dcp::new_var(h, 0, 1));
    away.push_back(dcp::new_var(h, 0, 1));
  }
  for (int w = 0; w < W; ++w)
    for (int p = 0; p < P; ++p)
      for (int i = 0; i < n; ++i)
        for (int j = i + 1; j < n; ++j) meet[meetIdx(w, p, i, j)] = dcp::new_var(h, 0, 1);

  // Each period holds exactly one match.
  for (int w = 0; w < W; ++w)
    for (int p = 0; p < P; ++p) {
      dcp::Lin s;
      for (int i = 0; i < n; ++i)
        for (int j = i + 1; j < n; ++j) s = s + meet[meetIdx(w, p, i, j)];
      dcp::add_row(h, s, 1, 1);
    }

  // A team plays in a period exactly when it is one of the two teams of that period's match.
  for (int w = 0; w < W; ++w)
    for (int p = 0; p < P; ++p)
      for (int t = 0; t < n; ++t) {
        dcp::Lin s;
        for (int o = 0; o < n; ++o) {
          if (o == t) continue;
          int a = std::min(t, o), b = std::max(t, o);
          s = s + meet[meetIdx(w, p, a, b)];
        }
        dcp::add_row(h, s - play[slot(w, p, t)], 0, 0);
      }

  // Every team plays once a week.
  for (int w = 0; w < W; ++w)
    for (int t = 0; t < n; ++t) {
      dcp::Lin s;
      for (int p = 0; p < P; ++p) s = s + play[slot(w, p, t)];
      dcp::add_row(h, s, 1, 1);
    }

  // Every team plays every other team exactly once over the tournament.
  for (int i = 0; i < n; ++i)
    for (int j = i + 1; j < n; ++j) {
      dcp::Lin s;
      for (int w = 0; w < W; ++w)
        for (int p = 0; p < P; ++p) s = s + meet[meetIdx(w, p, i, j)];
      dcp::add_row(h, s, 1, 1);
    }

  // Every team plays at most twice in the same period over the tournament.
  for (int p = 0; p < P; ++p)
    for (int t = 0; t < n; ++t) {
      dcp::Lin s;
      for (int w = 0; w < W; ++w) s = s + play[slot(w, p, t)];
      dcp::add_row(h, s, -kHighsInf, 2);
    }

  // In each slot of a match, the first team plays at home and the second plays away:
  // each period has one home team and one away team, both from its match.
  for (int w = 0; w < W; ++w)
    for (int p = 0; p < P; ++p) {
      dcp::Lin sh, sa;
      for (int t = 0; t < n; ++t) {
        dcp::add_row(h, home[slot(w, p, t)] + away[slot(w, p, t)] - play[slot(w, p, t)], 0, 0);
        sh = sh + home[slot(w, p, t)];
        sa = sa + away[slot(w, p, t)];
      }
      dcp::add_row(h, sh, 1, 1);
      dcp::add_row(h, sa, 1, 1);
    }

  // The output lists the team numbers, 1 to n.
  std::vector<std::vector<dcp::Lin>> homeOut(W, std::vector<dcp::Lin>(P)), awayOut(W, std::vector<dcp::Lin>(P));
  for (int w = 0; w < W; ++w)
    for (int p = 0; p < P; ++p)
      for (int t = 0; t < n; ++t) {
        homeOut[w][p] = homeOut[w][p] + static_cast<double>(t + 1) * home[slot(w, p, t)];
        awayOut[w][p] = awayOut[w][p] + static_cast<double>(t + 1) * away[slot(w, p, t)];
      }
  out.add("home", homeOut);
  out.add("away", awayOut);
}
