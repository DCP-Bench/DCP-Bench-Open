// Sports tournament scheduling: n teams (n even) play a round robin over n-1 weeks; each week the teams are paired into n/2 periods, one home and one away team per period; every team plays every other team once and meets in the same period at most twice over the tournament.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n_teams");
  int W = n - 1;  // weeks
  int P = n / 2;  // periods per week

  // teams are numbered 0..n-1 inside the model; the output adds 1

  // opp[w][t] = the opponent of team t in week w
  vec<vec<IntVar*>> opp;
  createVars(opp, W, n, 0, n - 1);
  // per[w][t] = the period in which team t plays in week w
  vec<vec<IntVar*>> per;
  createVars(per, W, n, 0, P - 1);
  // hi[w][t] = 1 if team t plays at home in week w
  vec<vec<IntVar*>> hi;
  createVars(hi, W, n, 0, 1, true);

  // every week, the teams are paired up: nobody plays themselves, and if t plays u then u plays t
  for (int w = 0; w < W; ++w) {
    for (int t = 0; t < n; ++t) int_rel(opp[w][t], IRT_NE, t);
    vec<IntVar*> a, b;
    for (int t = 0; t < n; ++t) {
      a.push(opp[w][t]);
      b.push(opp[w][t]);
    }
    inverse(a, b);
  }

  // every team plays every other team exactly once: the n-1 weeks give n-1 different opponents of each team
  for (int t = 0; t < n; ++t) {
    vec<IntVar*> col;
    for (int w = 0; w < W; ++w) col.push(opp[w][t]);
    all_different(col);
  }

  // the two teams of a match share the period of that match
  for (int w = 0; w < W; ++w) {
    for (int t = 0; t < n; ++t) {
      array_var_int_element_bound(opp[w][t], per[w], per[w][t]);
    }
  }

  // eq[((w*n)+t)*P+p] = 1 if team t plays in period p of week w
  vec<BoolView> eq;
  createVars(eq, W * n * P);
  for (int w = 0; w < W; ++w)
    for (int t = 0; t < n; ++t)
      for (int p = 0; p < P; ++p) int_rel_reif(per[w][t], IRT_EQ, p, eq[((w * n) + t) * P + p]);

  // each period of each week holds exactly one match, that is two teams
  for (int w = 0; w < W; ++w) {
    for (int p = 0; p < P; ++p) {
      vec<BoolView> in_period;
      for (int t = 0; t < n; ++t) in_period.push(eq[((w * n) + t) * P + p]);
      bool_linear(in_period, IRT_EQ, getConstant(2));
    }
  }

  // no team plays in the same period more than twice over the whole tournament
  for (int t = 0; t < n; ++t) {
    for (int p = 0; p < P; ++p) {
      vec<BoolView> same;
      for (int w = 0; w < W; ++w) same.push(eq[((w * n) + t) * P + p]);
      bool_linear(same, IRT_LE, getConstant(2));
    }
  }

  // in each match one team plays at home and the other away
  vec<BoolView> hb;  // hb[w*n+t] = 1 if team t plays at home in week w (same as hi as a Boolean)
  for (int w = 0; w < W; ++w) {
    for (int t = 0; t < n; ++t) {
      BoolView h = newBoolVar();
      bool2int(h, hi[w][t]);
      hb.push(h);
    }
  }
  for (int w = 0; w < W; ++w) {
    for (int t = 0; t < n; ++t) {
      IntVar* other_home = newIntVar(0, 1);
      array_var_int_element_bound(opp[w][t], hi[w], other_home);
      vec<IntVar*> both;
      both.push(hi[w][t]);
      both.push(other_home);
      vec<int> ones;
      ones.push(1);
      ones.push(1);
      int_linear(ones, both, IRT_EQ, 1);
    }
  }

  // symmetry breaking: the teams can be renumbered, and periods and home/away can be swapped within week 0.
  // Week 0 pairs teams (0,1), (2,3), ... in periods 0, 1, ..., with the even team at home.
  for (int t = 0; t < n; ++t) {
    int_rel(opp[0][t], IRT_EQ, t ^ 1);
    int_rel(per[0][t], IRT_EQ, t / 2);
    int_rel(hi[0][t], IRT_EQ, (t % 2 == 0) ? 1 : 0);
  }

  // home[w][p] / away[w][p] (1-based): the team of match p of week w at home / away
  json H = json::array(), A = json::array();
  for (int w = 0; w < W; ++w) {
    json hr = json::array(), ar = json::array();
    for (int p = 0; p < P; ++p) {
      vec<IntVar*> hsel, asel;
      vec<int> hc, ac;
      for (int t = 0; t < n; ++t) {
        // is team t the home team of match p in week w
        BoolView hb_tp = newBoolVar();
        vec<BoolView> hand;
        hand.push(eq[((w * n) + t) * P + p]);
        hand.push(hb[w * n + t]);
        array_bool_and(hand, hb_tp);
        IntVar* hbi = newIntVar(0, 1);
        bool2int(hb_tp, hbi);
        hsel.push(hbi);
        hc.push(t + 1);

        // is team t the away team of match p in week w
        BoolView ab_tp = newBoolVar();
        BoolView not_home = ~hb[w * n + t];
        vec<BoolView> aand;
        aand.push(eq[((w * n) + t) * P + p]);
        aand.push(not_home);
        array_bool_and(aand, ab_tp);
        IntVar* abi = newIntVar(0, 1);
        bool2int(ab_tp, abi);
        asel.push(abi);
        ac.push(t + 1);
      }
      IntVar* home_team = newIntVar(1, n);
      int_linear(hc, hsel, IRT_EQ, home_team);
      IntVar* away_team = newIntVar(1, n);
      int_linear(ac, asel, IRT_EQ, away_team);
      hr.push_back(dcp::out(home_team));
      ar.push_back(dcp::out(away_team));
    }
    H.push_back(hr);
    A.push_back(ar);
  }

  // branch on the opponents week by week, then the periods and home slots
  vec<IntVar*> decision;
  for (int w = 0; w < W; ++w)
    for (int t = 0; t < n; ++t) decision.push(opp[w][t]);
  for (int w = 0; w < W; ++w)
    for (int t = 0; t < n; ++t) decision.push(per[w][t]);
  branch(decision, VAR_INORDER, VAL_MIN);

  outputs = {{"home", H}, {"away", A}};
}
