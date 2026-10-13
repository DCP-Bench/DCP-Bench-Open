// ACC basketball timetabling: a double round robin of 9 teams over 18 dates with home, away and bye patterns and the extra rules of the 1997/98 Atlantic Coast Conference schedule.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int N = instance.at("n_teams");  // 9 teams
  int D = instance.at("n_days");   // 18 dates; odd dates (1-based) are weekdays, even dates weekends

  // teams are numbered 0..8 in the order of the problem statement
  const int CLEM = 0, DUKE = 1, FSU = 2, GT = 3, UMD = 4, UNC = 5, NCST = 6, UVA = 7, WAKE = 8;

  // opp[d][t] = the team that team t plays on date d (its own number when it has a bye)
  vec<vec<IntVar*>> opp;
  createVars(opp, D, N, 0, N - 1);
  // where[d][t] = 0 home, 1 bye, 2 away
  vec<vec<IntVar*>> where;
  createVars(where, D, N, 0, 2);

  // E[(d*N+t)*N+u] = 1 if team t plays team u on date d
  vec<BoolView> E;
  createVars(E, D * N * N);
  // Hb, Ab, Bb: Boolean views of team t being at home, away, or having a bye on date d (index d*N+t)
  vec<BoolView> Hb, Ab, Bb;
  createVars(Hb, D * N);
  createVars(Ab, D * N);
  createVars(Bb, D * N);

  for (int d = 0; d < D; ++d) {
    for (int t = 0; t < N; ++t) {
      int_rel_reif(where[d][t], IRT_EQ, 0, Hb[d * N + t]);
      int_rel_reif(where[d][t], IRT_EQ, 2, Ab[d * N + t]);
      int_rel_reif(where[d][t], IRT_EQ, 1, Bb[d * N + t]);
      for (int u = 0; u < N; ++u) {
        int_rel_reif(opp[d][t], IRT_EQ, u, E[(d * N + t) * N + u]);
      }
    }
  }

  // a team has a bye exactly when it is paired with itself
  for (int d = 0; d < D; ++d) {
    for (int t = 0; t < N; ++t) {
      int_rel_reif(opp[d][t], IRT_EQ, t, Bb[d * N + t]);
    }
  }

  // the pairings of each date are symmetric: if t plays u then u plays t
  for (int d = 0; d < D; ++d) {
    vec<IntVar*> a, b;
    for (int t = 0; t < N; ++t) {
      a.push(opp[d][t]);
      b.push(opp[d][t]);
    }
    inverse(a, b);
  }

  // one team of every match is at home and the other is away: the two sides of a match have home/away that differ, and the sum of their codes is 2 (home 0 + away 2, or bye 1 + bye 1)
  for (int d = 0; d < D; ++d) {
    for (int t = 0; t < N; ++t) {
      IntVar* other = newIntVar(0, 2);
      array_var_int_element_bound(opp[d][t], where[d], other);
      vec<IntVar*> pair;
      pair.push(where[d][t]);
      pair.push(other);
      vec<int> ones;
      ones.push(1);
      ones.push(1);
      int_linear(ones, pair, IRT_EQ, 2);
    }
  }

  // every team plays every other team twice in the tournament, once at home and once away
  for (int t = 0; t < N; ++t) {
    for (int u = 0; u < N; ++u) {
      if (u == t) continue;
      vec<BoolView> games;
      vec<BoolView> homes;
      for (int d = 0; d < D; ++d) {
        games.push(E[(d * N + t) * N + u]);
        BoolView hm = newBoolVar();
        vec<BoolView> at_home;
        at_home.push(E[(d * N + t) * N + u]);
        at_home.push(Hb[d * N + t]);
        array_bool_and(at_home, hm);
        homes.push(hm);
      }
      bool_linear(games, IRT_EQ, getConstant(2));
      bool_linear(homes, IRT_EQ, getConstant(1));
    }
  }

  // mirroring: the dates are grouped into pairs (r1, r2) (1-based: (1,8), (2,9), (3,12), (4,13), (5,14), (6,15), (7,16), (10,17), (11,18)), and each team plays the same opponent on both dates of a pair
  int mirror[9][2] = {{0, 7}, {1, 8}, {2, 11}, {3, 12}, {4, 13}, {5, 14}, {6, 15}, {9, 16}, {10, 17}};
  for (int m = 0; m < 9; ++m) {
    for (int t = 0; t < N; ++t) {
      int_rel(opp[mirror[m][0]][t], IRT_EQ, opp[mirror[m][1]][t]);
    }
  }

  // no two final aways: no team can play away on both of the last two dates
  for (int t = 0; t < N; ++t) {
    vec<BoolView> none;
    vec<BoolView> both_away;
    both_away.push(Ab[(D - 2) * N + t]);
    both_away.push(Ab[(D - 1) * N + t]);
    bool_clause(none, both_away);
  }

  // home, away and bye runs: no more than two away in a row, no more than two home in a row,
  // no more than three away or byes in a row, and no more than four home or byes in a row
  for (int t = 0; t < N; ++t) {
    for (int d = 0; d + 2 < D; ++d) {
      vec<BoolView> three_away, three_home;
      for (int k = 0; k < 3; ++k) {
        three_away.push(Ab[(d + k) * N + t]);
        three_home.push(Hb[(d + k) * N + t]);
      }
      vec<BoolView> none;
      bool_clause(none, three_away);
      bool_clause(none, three_home);
    }
    for (int d = 0; d + 3 < D; ++d) {
      // at least one home match in every four dates
      vec<BoolView> four_slots;
      for (int k = 0; k < 4; ++k) four_slots.push(Hb[(d + k) * N + t]);
      bool_clause(four_slots);
    }
    for (int d = 0; d + 4 < D; ++d) {
      // at least one away match in every five dates
      vec<BoolView> five_slots;
      for (int k = 0; k < 5; ++k) five_slots.push(Ab[(d + k) * N + t]);
      bool_clause(five_slots);
    }
  }

  // weekend pattern: the weekends are the even dates (1-based), i.e. 0-based indices 1, 3, ..., 17;
  // each team plays four home, four away and one bye across the nine weekends
  for (int t = 0; t < N; ++t) {
    vec<BoolView> wh, wa, wb;
    for (int d = 1; d < D; d += 2) {
      wh.push(Hb[d * N + t]);
      wa.push(Ab[d * N + t]);
      wb.push(Bb[d * N + t]);
    }
    bool_linear(wh, IRT_EQ, getConstant(4));
    bool_linear(wa, IRT_EQ, getConstant(4));
    bool_linear(wb, IRT_EQ, getConstant(1));
  }

  // first weekends: each team has home matches or byes on at least two of the first five weekends
  for (int t = 0; t < N; ++t) {
    vec<BoolView> early;
    for (int d = 1; d <= 9; d += 2) {
      early.push(Hb[d * N + t]);
      early.push(Bb[d * N + t]);
    }
    bool_linear(early, IRT_GE, getConstant(2));
  }

  // rival matches on the last date: every team except FSU plays its rival, unless it plays FSU or has a bye
  // rival pairs: Duke-UNC, Clem-GT, NCSt-Wake, UMD-UVA
  int rival[9];
  rival[CLEM] = GT;
  rival[DUKE] = UNC;
  rival[FSU] = -1;
  rival[GT] = CLEM;
  rival[UMD] = UVA;
  rival[UNC] = DUKE;
  rival[NCST] = WAKE;
  rival[UVA] = UMD;
  rival[WAKE] = NCST;
  for (int t = 0; t < N; ++t) {
    if (rival[t] < 0) continue;
    vec<BoolView> ok;
    ok.push(E[((D - 1) * N + t) * N + rival[t]]);
    ok.push(E[((D - 1) * N + t) * N + FSU]);
    ok.push(Bb[(D - 1) * N + t]);
    bool_clause(ok);
  }

  // constrained matches: Wake-UNC, Wake-Duke, GT-UNC and GT-Duke must each occur at least once in dates 11 to 18
  int pairs[4][2] = {{WAKE, UNC}, {WAKE, DUKE}, {GT, UNC}, {GT, DUKE}};
  for (int p = 0; p < 4; ++p) {
    vec<BoolView> meet;
    for (int d = 10; d < D; ++d) meet.push(E[(d * N + pairs[p][0]) * N + pairs[p][1]]);
    bool_clause(meet);
  }

  // opponent sequences: no team plays away against UNC and Duke on two consecutive dates,
  // and no team plays against UNC, Duke and Wake on three consecutive dates
  for (int t = 0; t < N; ++t) {
    for (int d = 0; d + 1 < D; ++d) {
      // away_vs[d][u] is a BoolView: t plays away against u on date d
      BoolView unc_d = newBoolVar(), duke_d = newBoolVar(), unc_e = newBoolVar(), duke_e = newBoolVar();
      if (t != UNC && t != DUKE) {
        vec<BoolView> x1, x2, x3, x4;
        x1.push(E[(d * N + t) * N + UNC]);
        x1.push(Ab[d * N + t]);
        array_bool_and(x1, unc_d);
        x2.push(E[(d * N + t) * N + DUKE]);
        x2.push(Ab[d * N + t]);
        array_bool_and(x2, duke_d);
        x3.push(E[((d + 1) * N + t) * N + UNC]);
        x3.push(Ab[(d + 1) * N + t]);
        array_bool_and(x3, unc_e);
        x4.push(E[((d + 1) * N + t) * N + DUKE]);
        x4.push(Ab[(d + 1) * N + t]);
        array_bool_and(x4, duke_e);
        vec<BoolView> none;
        vec<BoolView> c1, c2;
        c1.push(unc_d);
        c1.push(duke_e);
        bool_clause(none, c1);
        vec<BoolView> c2b;
        c2b.push(duke_d);
        c2b.push(unc_e);
        bool_clause(none, c2b);
      }
    }
    for (int d = 0; d + 2 < D; ++d) {
      // the three opponents UNC, Duke and Wake in some order on three consecutive dates
      if (t == UNC || t == DUKE || t == WAKE) continue;
      int trio[3] = {UNC, DUKE, WAKE};
      int perm[6][3] = {{0, 1, 2}, {0, 2, 1}, {1, 0, 2}, {1, 2, 0}, {2, 0, 1}, {2, 1, 0}};
      for (int q = 0; q < 6; ++q) {
        vec<BoolView> none, not_all;
        for (int k = 0; k < 3; ++k) not_all.push(E[((d + k) * N + t) * N + trio[perm[q][k]]]);
        bool_clause(none, not_all);
      }
    }
  }

  // other constraints from the problem statement (dates are 0-based below)
  int_rel(opp[17][UNC], IRT_EQ, DUKE);   // UNC plays Duke in the last date
  int_rel(opp[10][UNC], IRT_EQ, DUKE);   // and in date 11
  int_rel(opp[1][UNC], IRT_EQ, CLEM);    // UNC plays Clem in the second date
  int_rel(where[15][DUKE], IRT_EQ, 1);   // Duke has a bye in date 16
  int_rel(where[16][WAKE], IRT_NE, 0);   // Wake does not play home in date 17
  int_rel(where[0][WAKE], IRT_EQ, 1);    // Wake has a bye in the first date
  int_rel(where[17][CLEM], IRT_NE, 2);   // Clem, Duke, UMD and Wake do not play away in the last date
  int_rel(where[17][DUKE], IRT_NE, 2);
  int_rel(where[17][UMD], IRT_NE, 2);
  int_rel(where[17][WAKE], IRT_NE, 2);
  int_rel(where[0][CLEM], IRT_NE, 2);    // Clem, FSU, GT and Wake do not play away in the first date
  int_rel(where[0][FSU], IRT_NE, 2);
  int_rel(where[0][GT], IRT_NE, 2);
  int_rel(where[0][WAKE], IRT_NE, 2);
  int_rel(where[17][FSU], IRT_NE, 1);    // neither FSU nor NCSt has a bye in the last date
  int_rel(where[17][NCST], IRT_NE, 1);
  int_rel(where[0][UNC], IRT_NE, 1);     // UNC does not have a bye in the first date

  // branch on the opponents date by date, then the home/away/bye codes
  vec<IntVar*> decision;
  for (int d = 0; d < D; ++d)
    for (int t = 0; t < N; ++t) decision.push(opp[d][t]);
  vec<IntVar*> homeaway;
  for (int d = 0; d < D; ++d)
    for (int t = 0; t < N; ++t) homeaway.push(where[d][t]);
  branch(homeaway, VAR_SIZE_MIN, VAL_MIN);
  branch(decision, VAR_SIZE_MIN, VAL_MIN);

  json config = json::array(), place = json::array();
  for (int d = 0; d < D; ++d) {
    json cr = json::array(), wr = json::array();
    for (int t = 0; t < N; ++t) {
      cr.push_back(dcp::out(opp[d][t]));
      wr.push_back(dcp::out(where[d][t]));
    }
    config.push_back(cr);
    place.push_back(wr);
  }
  outputs = {{"config", config}, {"where", place}};
}
