// Sports tournament scheduling: n teams play a round robin over n-1 weeks, each week split into n/2 periods with a home and an away team.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n_teams");
  int W = n - 1;  // number of weeks
  int P = n / 2;  // periods per week, each with two slots (home and away)

  // home[w][p] and away[w][p] are the teams (numbered 1..n) in the home and away slot of week w, period p
  vec<vec<IntVar*>> home, away;
  createVars(home, W, P, 1, n);
  createVars(away, W, P, 1, n);

  // hb[(w*P+p)*n+t] = 1 if team t+1 plays at home in week w, period p; aw is the same for the away slot
  vec<BoolView> hb, aw;
  createVars(hb, W * P * n);
  createVars(aw, W * P * n);
  for (int w = 0; w < W; ++w) {
    for (int p = 0; p < P; ++p) {
      for (int t = 0; t < n; ++t) {
        int idx = (w * P + p) * n + t;
        int_rel_reif(home[w][p], IRT_EQ, t + 1, hb[idx]);
        int_rel_reif(away[w][p], IRT_EQ, t + 1, aw[idx]);
      }
    }
  }

  // every team plays once a week: the 2 * (n/2) = n slots of each week hold all the teams, each exactly once
  for (int w = 0; w < W; ++w) {
    vec<IntVar*> week;
    for (int p = 0; p < P; ++p) {
      week.push(home[w][p]);
      week.push(away[w][p]);
    }
    all_different(week);
  }

  // symmetry breaking: teams can be renumbered freely, so week 1 can be fixed to the pairs
  // (1 v P+1), (2 v P+2), ... with team i+1 at home in period i (renumbering the teams keeps every class represented)
  for (int p = 0; p < P; ++p) {
    int_rel(home[0][p], IRT_EQ, p + 1);
    int_rel(away[0][p], IRT_EQ, P + p + 1);
  }

  // every team plays at most twice in the same period over the whole tournament
  for (int p = 0; p < P; ++p) {
    for (int t = 0; t < n; ++t) {
      vec<BoolView> plays;
      for (int w = 0; w < W; ++w) {
        int idx = (w * P + p) * n + t;
        plays.push(hb[idx]);
        plays.push(aw[idx]);
      }
      bool_linear(plays, IRT_LE, getConstant(2));
    }
  }

  // every team plays every other team: each unordered pair meets at least once in some week and period,
  // in either order. There are n(n-1)/2 matches for n(n-1)/2 pairs, so every pair meets exactly once.
  for (int i = 0; i < n; ++i) {
    for (int j = i + 1; j < n; ++j) {
      vec<BoolView> meet;
      for (int w = 0; w < W; ++w) {
        for (int p = 0; p < P; ++p) {
          // m1: team i at home against team j away; m2: team j at home against team i away
          BoolView m1 = newBoolVar();
          vec<BoolView> and1;
          and1.push(hb[(w * P + p) * n + i]);
          and1.push(aw[(w * P + p) * n + j]);
          array_bool_and(and1, m1);
          meet.push(m1);

          BoolView m2 = newBoolVar();
          vec<BoolView> and2;
          and2.push(hb[(w * P + p) * n + j]);
          and2.push(aw[(w * P + p) * n + i]);
          array_bool_and(and2, m2);
          meet.push(m2);
        }
      }
      bool_clause(meet);
    }
  }

  // branch on the slots week by week
  vec<IntVar*> slots;
  for (int w = 0; w < W; ++w) {
    for (int p = 0; p < P; ++p) {
      slots.push(home[w][p]);
      slots.push(away[w][p]);
    }
  }
  branch(slots, VAR_INORDER, VAL_MIN);

  json H = json::array(), A = json::array();
  for (int w = 0; w < W; ++w) {
    json hr = json::array(), ar = json::array();
    for (int p = 0; p < P; ++p) {
      hr.push_back(dcp::out(home[w][p]));
      ar.push_back(dcp::out(away[w][p]));
    }
    H.push_back(hr);
    A.push_back(ar);
  }
  outputs = {{"home", H}, {"away", A}};
}
