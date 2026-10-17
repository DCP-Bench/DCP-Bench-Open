// CSPlib 011: 1997/98 ACC basketball schedule (satisfaction). Nine teams play a double round-robin
// over 18 dates (odd dates weekday, even dates weekend), subject to the mirroring,
// home/away/bye pattern, weekend, first-weekend, final-date, rival, constrained-match,
// opponent-sequence and other constraints of the problem description.
// Output: config[d][i] = opponent of team i on date d (its own index for a bye);
// where[d][i] = 0 home, 1 bye, 2 away.
#include <algorithm>
#include <array>
#include <stdexcept>

#include "dcp.h"

namespace {

using dcp::Lin;

// Team indices, in the order the description lists them.
constexpr int kClem = 0, kDuke = 1, kFSU = 2, kGT = 3, kUMD = 4, kUNC = 5, kNCSt = 6, kUVA = 7, kWake = 8;

// The rival of each team that has one (FSU has none).
constexpr int kRival[9] = {kGT, kUNC, -1, kClem, kUVA, kDuke, kWake, kUMD, kNCSt};

void le(Highs& h, const Lin& e, double k) { dcp::add_row(h, e, -kHighsInf, k); }
void ge(Highs& h, const Lin& e, double k) { dcp::add_row(h, e, k, kHighsInf); }
void eq(Highs& h, const Lin& e, double k) { dcp::add_row(h, e, k, k); }

struct Schedule {
  int T;
  int D;
  // g[d][i][j] = 1 when team i hosts team j on date d. The diagonal stays the zero expression.
  std::vector<std::vector<std::vector<Lin>>> g;

  // Teams i and j play each other on date d, at home either way.
  Lin pl(int d, int i, int j) const { return g[d][i][j] + g[d][j][i]; }
  // Team i plays a match on date d (against anyone).
  Lin play(int d, int i) const {
    Lin e;
    for (int j = 0; j < T; ++j)
      if (j != i) e = e + pl(d, i, j);
    return e;
  }
  // Team i has a bye on date d.
  Lin bye(int d, int i) const { return Lin(1.0) - play(d, i); }
  // Team i hosts on date d.
  Lin home(int d, int i) const {
    Lin e;
    for (int j = 0; j < T; ++j)
      if (j != i) e = e + g[d][i][j];
    return e;
  }
  // Team i plays away on date d.
  Lin away(int d, int i) const {
    Lin e;
    for (int j = 0; j < T; ++j)
      if (j != i) e = e + g[d][j][i];
    return e;
  }
};

}  // namespace

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  Schedule s;
  s.T = instance.at("n_teams").get<int>();
  s.D = instance.at("n_days").get<int>();
  if (s.T != 9 || s.D != 18) throw std::runtime_error("the ACC schedule is fixed at 9 teams and 18 dates");
  const int T = s.T;
  const int D = s.D;

  // One binary per ordered pair of teams and date.
  s.g.assign(D, std::vector<std::vector<Lin>>(T, std::vector<Lin>(T)));
  for (int d = 0; d < D; ++d)
    for (int i = 0; i < T; ++i)
      for (int j = 0; j < T; ++j)
        if (i != j) s.g[d][i][j] = dcp::new_var(h, 0, 1);

  // ---- Double round-robin: each team plays each other once at home and once away ----
  // // each team hosts each other team exactly once
  for (int i = 0; i < T; ++i)
    for (int j = 0; j < T; ++j)
      if (i != j) {
        Lin e;
        for (int d = 0; d < D; ++d) e = e + s.g[d][i][j];
        eq(h, e, 1);
      }

  // ---- A team plays at most one match on each date ----
  // // no team plays more than one match on a date
  for (int d = 0; d < D; ++d)
    for (int i = 0; i < T; ++i) le(h, s.play(d, i), 1);

  // ---- Mirroring: each team meets the same opponent on dates r1 and r2 ----
  // // the dates are paired (r1, r2), with 1-based dates (1,8) (2,9) (3,12) (4,13) (5,14)
  // // (6,15) (7,16) (10,17) (11,18); each team plays the same team in both dates of a pair
  const std::array<std::array<int, 2>, 9> mirror = {{{0, 7}, {1, 8}, {2, 11}, {3, 12}, {4, 13},
                                                    {5, 14}, {6, 15}, {9, 16}, {10, 17}}};
  for (const auto& pr : mirror)
    for (int i = 0; i < T; ++i)
      for (int j = 0; j < T; ++j)
        if (i != j) eq(h, s.pl(pr[0], i, j) - s.pl(pr[1], i, j), 0);

  // ---- No two final aways: no team plays away on both last dates ----
  // // no team plays away on both of the last two dates
  for (int i = 0; i < T; ++i) le(h, s.away(D - 2, i) + s.away(D - 1, i), 1);

  // ---- Home/away/bye patterns over consecutive dates ----
  for (int i = 0; i < T; ++i)
    for (int d = 0; d + 2 < D; ++d) {
      // // no more than two away matches in a row
      Lin aw;
      for (int k = 0; k < 3; ++k) aw = aw + s.away(d + k, i);
      le(h, aw, 2);
      // // no more than two home matches in a row
      Lin hm;
      for (int k = 0; k < 3; ++k) hm = hm + s.home(d + k, i);
      le(h, hm, 2);
    }
  for (int i = 0; i < T; ++i)
    for (int d = 0; d + 3 < D; ++d) {
      // // no more than three away matches or byes in a row (any four dates hold a home match)
      Lin nothome;
      for (int k = 0; k < 4; ++k) nothome = nothome + (Lin(1.0) - s.home(d + k, i));
      le(h, nothome, 3);
    }
  for (int i = 0; i < T; ++i)
    for (int d = 0; d + 4 < D; ++d) {
      // // no more than four home matches or byes in a row (any five dates hold an away match)
      Lin notaway;
      for (int k = 0; k < 5; ++k) notaway = notaway + (Lin(1.0) - s.away(d + k, i));
      le(h, notaway, 4);
    }

  // ---- Weekend pattern: over the weekends, four home, four away and one bye ----
  // // weekends are the even dates (1-based), which are the odd indices here
  for (int i = 0; i < T; ++i) {
    Lin hm, aw, by;
    for (int d = 1; d < D; d += 2) {
      hm = hm + s.home(d, i);
      aw = aw + s.away(d, i);
      by = by + s.bye(d, i);
    }
    // // each team plays four matches at home on the weekends
    eq(h, hm, 4);
    // // each team plays four matches away on the weekends
    eq(h, aw, 4);
    // // each team has one bye on the weekends
    eq(h, by, 1);
  }

  // ---- Redundant totals over the season: 16 matches per team, eight home, eight away, two byes ----
  // // each team has eight home matches, eight away matches and two byes over the 18 dates
  for (int i = 0; i < T; ++i) {
    Lin hm, aw, by;
    for (int d = 0; d < D; ++d) {
      hm = hm + s.home(d, i);
      aw = aw + s.away(d, i);
      by = by + s.bye(d, i);
    }
    eq(h, hm, 8);
    eq(h, aw, 8);
    eq(h, by, 2);
  }

  // ---- First weekends: home matches or byes on at least two of the first five weekends ----
  // // each team has home matches or byes at least on two of the first five weekends (dates 2 to 10)
  for (int i = 0; i < T; ++i) {
    Lin e;
    for (int d = 1; d <= 9; d += 2) e = e + s.home(d, i) + s.bye(d, i);
    ge(h, e, 2);
  }

  // ---- Rival matches on the last date ----
  // // on the last date every team except FSU plays its rival, unless it plays FSU or has a bye
  for (int i = 0; i < T; ++i) {
    if (kRival[i] < 0) continue;
    for (int j = 0; j < T; ++j)
      if (j != i && j != kRival[i] && j != kFSU) eq(h, s.pl(D - 1, i, j), 0);
  }

  // ---- Constrained matches in dates 11 to 18 ----
  // // Wake-UNC, Wake-Duke, GT-UNC and GT-Duke each occur at least once in dates 11 to 18
  const std::array<std::array<int, 2>, 4> required = {{{kWake, kUNC}, {kWake, kDuke}, {kGT, kUNC}, {kGT, kDuke}}};
  for (const auto& pr : required) {
    Lin e;
    for (int d = 10; d < D; ++d) e = e + s.pl(d, pr[0], pr[1]);
    ge(h, e, 1);
  }

  // ---- Opponent sequence constraints ----
  for (int i = 0; i < T; ++i)
    for (int d = 0; d + 1 < D; ++d) {
      // // no team plays in two consecutive dates away against UNC and Duke
      le(h, s.g[d][kUNC][i] + s.g[d + 1][kDuke][i], 1);
      le(h, s.g[d][kDuke][i] + s.g[d + 1][kUNC][i], 1);
    }
  std::array<int, 3> trio = {kUNC, kDuke, kWake};
  for (int i = 0; i < T; ++i)
    for (int d = 0; d + 2 < D; ++d) {
      // // no team plays in three consecutive dates against UNC, Duke and Wake, in any order
      do {
        le(h, s.pl(d, i, trio[0]) + s.pl(d + 1, i, trio[1]) + s.pl(d + 2, i, trio[2]), 2);
      } while (std::next_permutation(trio.begin(), trio.end()));
    }

  // ---- Other constraints ----
  // // UNC plays its rival Duke in the last date, and in date 11
  eq(h, s.pl(D - 1, kUNC, kDuke), 1);
  eq(h, s.pl(10, kUNC, kDuke), 1);
  // // UNC plays Clem in the second date
  eq(h, s.pl(1, kUNC, kClem), 1);
  // // Duke has a bye in date 16
  eq(h, s.bye(15, kDuke), 1);
  // // Wake does not play home in date 17
  eq(h, s.home(16, kWake), 0);
  // // Wake has a bye in the first date
  eq(h, s.bye(0, kWake), 1);
  // // Clem, Duke, UMD and Wake do not play away in the last date
  for (int i : {kClem, kDuke, kUMD, kWake}) eq(h, s.away(D - 1, i), 0);
  // // Clem, FSU, GT and Wake do not play away in the first date
  for (int i : {kClem, kFSU, kGT, kWake}) eq(h, s.away(0, i), 0);
  // // neither FSU nor NCSt has a bye in the last date
  for (int i : {kFSU, kNCSt}) eq(h, s.bye(D - 1, i), 0);
  // // UNC does not have a bye in the first date
  eq(h, s.bye(0, kUNC), 0);

  // ---- Outputs ----
  std::vector<std::vector<Lin>> config(D, std::vector<Lin>(T));
  std::vector<std::vector<Lin>> where(D, std::vector<Lin>(T));
  for (int d = 0; d < D; ++d)
    for (int i = 0; i < T; ++i) {
      // // the opponent of team i on date d, or i itself for a bye
      Lin opp = static_cast<double>(i) * s.bye(d, i);
      for (int j = 0; j < T; ++j)
        if (j != i) opp = opp + static_cast<double>(j) * s.pl(d, i, j);
      config[d][i] = opp;
      // // 0 at home, 1 for a bye, 2 away
      where[d][i] = 2.0 * s.away(d, i) + s.bye(d, i);
    }
  out.add("config", config);
  out.add("where", where);
}
