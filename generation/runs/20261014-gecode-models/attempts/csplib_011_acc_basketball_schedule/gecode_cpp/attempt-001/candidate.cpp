#include "dcp.h"

// 1997/98 Atlantic Coast Conference basketball: a double round-robin of the
// 9 teams over 18 dates, subject to mirroring, pattern and opponent rules.
//
// Team indices (problem constants): 0 Clem, 1 Duke, 2 FSU, 3 GT, 4 UMD,
// 5 UNC, 6 NCSt, 7 UVA, 8 Wake. Date indices are 0-based: the statement's
// date k is index k-1. Odd statement dates are weekdays, even ones weekends,
// so weekend dates are the odd indices.
//
// opp[d][i]   : opponent of team i on date d; i itself on a bye (config).
// where[d][i] : 0 home, 1 bye, 2 away.
class ACCBasketball : public dcp::Space {
 protected:
  int T;              // teams, from the instance
  int D;              // dates, from the instance
  IntVarArray opp;    // opp[d * T + i]
  IntVarArray where;  // where[d * T + i]

 public:
  explicit ACCBasketball(const json& instance) {
    T = instance.at("n_teams").get<int>();
    D = instance.at("n_days").get<int>();
    if (T != 9 || D != 18) throw std::invalid_argument("the ACC schedule has 9 teams and 18 dates");

    opp = IntVarArray(*this, D * T, 0, T - 1);
    where = IntVarArray(*this, D * T, 0, 2);
    auto O = [&](int d, int i) { return opp[d * T + i]; };
    auto W = [&](int d, int i) { return where[d * T + i]; };

    // 1. Mirroring: the dates are grouped into pairs (r1, r2) and each team
    // plays the same opponent on both dates of a pair, so the second date
    // shares the first date's opponent variables.
    // Scheme {(1,8),(2,9),(3,12),(4,13),(5,14),(6,15),(7,16),(10,17),(11,18)}, 0-based.
    const int mirror[9][2] = {{0, 7}, {1, 8}, {2, 11}, {3, 12}, {4, 13},
                              {5, 14}, {6, 15}, {9, 16}, {10, 17}};
    for (const auto& pair : mirror)
      for (int i = 0; i < T; ++i) opp[pair[1] * T + i] = opp[pair[0] * T + i];
    // A mirrored pair holds the two meetings of each team with its opponent,
    // one home and one away, or a bye on both dates: the sides sum to 2.
    for (const auto& pair : mirror)
      for (int i = 0; i < T; ++i) rel(*this, W(pair[0], i) + W(pair[1], i) == 2);

    // a bye is the team playing itself, and a bye is where 1
    for (int d = 0; d < D; ++d)
      for (int i = 0; i < T; ++i) rel(*this, (W(d, i) == 1) == (O(d, i) == i));

    // a match is one game: i plays j on a date exactly when j plays i
    for (int d = 0; d < D; ++d) {
      IntVarArgs row;
      for (int i = 0; i < T; ++i) row << O(d, i);
      channel(*this, row, row, IPL_DOM);
    }

    // the two teams of a match take opposite sides: one home, one away
    for (int d = 0; d < D; ++d) {
      IntVarArgs sides;
      for (int i = 0; i < T; ++i) sides << W(d, i);
      for (int i = 0; i < T; ++i) {
        IntVar other(*this, 0, 2);
        element(*this, sides, O(d, i), other);
        rel(*this, W(d, i) + other == 2);
      }
    }

    // double round-robin: each team plays each other team once at home
    // (and so once away, by the opposite-sides rule)
    for (int i = 0; i < T; ++i)
      for (int j = 0; j < T; ++j) {
        if (i == j) continue;
        BoolVarArgs hosts;
        for (int d = 0; d < D; ++d) hosts << expr(*this, (O(d, i) == j) && (W(d, i) == 0));
        linear(*this, hosts, IRT_EQ, 1);
      }

    // each team has two byes (18 dates, 16 matches), and plays each other
    // team exactly twice
    for (int i = 0; i < T; ++i) {
      IntVarArgs column;
      for (int d = 0; d < D; ++d) column << O(d, i);
      count(*this, column, i, IRT_EQ, 2);
      for (int j = 0; j < T; ++j)
        if (j != i) count(*this, column, j, IRT_EQ, 2);
    }

    // 2. No two final aways: no team plays away on both of the last two dates.
    for (int i = 0; i < T; ++i) rel(*this, (W(D - 2, i) == 2) >> (W(D - 1, i) != 2));

    // 3. Home/away/bye patterns, over each team's column of dates.
    for (int i = 0; i < T; ++i) {
      IntVarArgs column;
      for (int d = 0; d < D; ++d) column << W(d, i);
      // no more than two away matches in a row
      sequence(*this, column, IntSet(2, 2), 3, 0, 2);
      // no more than two home matches in a row
      sequence(*this, column, IntSet(0, 0), 3, 0, 2);
      // no more than three away matches or byes in a row
      sequence(*this, column, IntSet(1, 2), 4, 0, 3);
      // no more than four home matches or byes in a row
      sequence(*this, column, IntSet(0, 1), 5, 0, 4);
    }

    // weekend dates are the odd indices
    // 4. Weekend pattern: over the weekends each team plays four at home,
    // four away and has one bye.
    for (int i = 0; i < T; ++i) {
      IntVarArgs weekends;
      for (int d = 1; d < D; d += 2) weekends << W(d, i);
      count(*this, weekends, 0, IRT_EQ, 4);
      count(*this, weekends, 2, IRT_EQ, 4);
      count(*this, weekends, 1, IRT_EQ, 1);
      // the weekdays then hold the other four home matches, four away and one bye
      IntVarArgs weekdays;
      for (int d = 0; d < D; d += 2) weekdays << W(d, i);
      count(*this, weekdays, 0, IRT_EQ, 4);
      count(*this, weekdays, 2, IRT_EQ, 4);
      count(*this, weekdays, 1, IRT_EQ, 1);
    }

    // 5. First weekends: each team has home matches or byes on at least two
    // of the first five weekends (dates 2, 4, 6, 8, 10 in the statement).
    for (int i = 0; i < T; ++i) {
      IntVarArgs firstWeekends;
      for (int d = 1; d <= 9; d += 2) firstWeekends << W(d, i);
      count(*this, firstWeekends, IntSet(0, 1), IRT_GQ, 2);
    }

    // 6. Rival matches: on the last date every team except FSU plays its
    // rival, unless it plays FSU or has a bye. Rivals: Duke-UNC, Clem-GT,
    // NCSt-Wake, UMD-UVA.
    const int FSU = 2;
    const int rival[9] = {3, 5, FSU, 0, 7, 1, 8, 4, 6};
    for (int i = 0; i < T; ++i) {
      if (i == FSU) continue;
      int r = rival[i];
      rel(*this, (O(D - 1, i) == r) || (O(D - 1, i) == FSU) || (O(D - 1, i) == i));
    }

    // 7. Constrained matches: in dates 11 to 18 (indices 10 to 17) Wake-UNC,
    // Wake-Duke, GT-UNC and GT-Duke each occur at least once.
    const int UNC = 5, DUKE = 1, GT = 3, WAKE = 8;
    const int constrained[4][2] = {{WAKE, UNC}, {WAKE, DUKE}, {GT, UNC}, {GT, DUKE}};
    for (const auto& pair : constrained) {
      IntVarArgs meetings;
      for (int d = 10; d < D; ++d) meetings << O(d, pair[0]);
      count(*this, meetings, pair[1], IRT_GQ, 1);
    }

    // 8. Opponent sequences.
    // No team plays away against UNC and Duke on two consecutive dates.
    TupleSet awayUncDuke(4);
    awayUncDuke.add(IntArgs({2, UNC, 2, DUKE})).add(IntArgs({2, DUKE, 2, UNC}));
    awayUncDuke.finalize();
    for (int i = 0; i < T; ++i)
      for (int d = 0; d + 1 < D; ++d) {
        IntVarArgs pair;
        pair << W(d, i) << O(d, i) << W(d + 1, i) << O(d + 1, i);
        extensional(*this, pair, awayUncDuke, false);
      }
    // No team plays against UNC, Duke and Wake on three consecutive dates
    // (in any order, home or away).
    TupleSet uncDukeWake(3);
    const int trio[3] = {UNC, DUKE, WAKE};
    for (int a = 0; a < 3; ++a)
      for (int b = 0; b < 3; ++b)
        for (int c = 0; c < 3; ++c)
          if (a != b && b != c && a != c) uncDukeWake.add(IntArgs({trio[a], trio[b], trio[c]}));
    uncDukeWake.finalize();
    for (int i = 0; i < T; ++i)
      for (int d = 0; d + 2 < D; ++d) {
        IntVarArgs triple;
        triple << O(d, i) << O(d + 1, i) << O(d + 2, i);
        extensional(*this, triple, uncDukeWake, false);
      }

    // 9. Other constraints (fixed facts of the statement, 0-based dates).
    // UNC plays its rival Duke in the last date and in date 11.
    rel(*this, O(D - 1, UNC), IRT_EQ, DUKE);
    rel(*this, O(10, UNC), IRT_EQ, DUKE);
    // UNC plays Clem in the second date.
    rel(*this, O(1, UNC), IRT_EQ, 0);
    // Duke has a bye in date 16.
    rel(*this, W(15, DUKE), IRT_EQ, 1);
    // Wake does not play home in date 17.
    rel(*this, W(16, WAKE), IRT_NQ, 0);
    // Wake has a bye in the first date.
    rel(*this, W(0, WAKE), IRT_EQ, 1);
    // Clem, Duke, UMD and Wake do not play away in the last date.
    for (int i : {0, DUKE, 4, WAKE}) rel(*this, W(D - 1, i), IRT_NQ, 2);
    // Clem, FSU, GT and Wake do not play away in the first date.
    for (int i : {0, FSU, GT, WAKE}) rel(*this, W(0, i), IRT_NQ, 2);
    // Neither FSU nor NCSt have a bye in the last date.
    for (int i : {FSU, 6}) rel(*this, W(D - 1, i), IRT_NQ, 1);
    // UNC does not have a bye in the first date.
    rel(*this, W(0, UNC), IRT_NQ, 1);

    // Search: decide the match sides first, then the opponents.
    // Opponents of the first date of each mirror pair; the rest are shared.
    IntVarArgs firstOfPair;
    for (const auto& pair : mirror)
      for (int i = 0; i < T; ++i) firstOfPair << opp[pair[0] * T + i];
    branch(*this, firstOfPair, INT_VAR_AFC_SIZE_MAX(0.99), INT_VAL_MIN());
    branch(*this, where, INT_VAR_AFC_SIZE_MAX(0.99), INT_VAL_MIN());
    restarts(100);

    // config[d][i] and where[d][i], one row per date
    output("config", Matrix<IntVarArray>(opp, T, D));
    output("where", Matrix<IntVarArray>(where, T, D));
  }

  ACCBasketball(ACCBasketball& s) : dcp::Space(s), T(s.T), D(s.D) {
    opp.update(*this, s.opp);
    where.update(*this, s.where);
  }
  Gecode::Space* copy() override { return new ACCBasketball(*this); }
};

DCP_MODEL(ACCBasketball)
