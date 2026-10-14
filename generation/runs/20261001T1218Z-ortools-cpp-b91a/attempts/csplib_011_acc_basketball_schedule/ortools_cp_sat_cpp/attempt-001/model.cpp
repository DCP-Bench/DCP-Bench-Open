#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// ACC basketball scheduling (CSPLib 11): a double round-robin timetable for
// the nine teams of the 1997/98 Atlantic Coast Conference over 18 dates (odd
// dates are weekday fixtures, even dates weekend fixtures), subject to the
// mirroring scheme, home/away/bye pattern rules, weekend rules, rival matches,
// constrained matches, opponent sequence rules and a set of fixed fixtures.
// Days are 0-based below: "date 11" is day 10.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n_teams = instance.at("n_teams").get<int>();
  const int n_days = instance.at("n_days").get<int>();

  // Team names, rivals and the mirroring scheme belong to the problem
  // statement (nine named teams, 18 dates), not to the instance data.
  enum { CLEM, DUKE, FSU, GT, UMD, UNC, NCSt, UVA, WAKE };
  const std::vector<int> rivals = {GT, UNC, FSU, CLEM, UVA, DUKE, WAKE, UMD, NCSt};
  // scheme[d]: the day mirrored with day d (Nemhauser and Trick's pairs
  // (1,8), (2,9), (3,12), (4,13), (5,14), (6,15), (7,16), (10,17), (11,18)).
  const std::vector<int> scheme = {7, 8, 11, 12, 13, 14, 15, 0, 1, 16, 17, 2, 3, 4, 5, 6, 9, 10};

  // home[d][i][j] (i != j): on day d team i plays team j at home, so j is away.
  // play[d][i][j]: teams i and j meet on day d, whoever is at home.
  // is_home / is_away / is_bye[d][i]: what team i does on day d.
  std::vector<std::vector<std::vector<BoolVar>>> home(n_days), play(n_days);
  std::vector<std::vector<BoolVar>> is_home(n_days), is_away(n_days), is_bye(n_days);
  for (int d = 0; d < n_days; ++d) {
    home[d].assign(n_teams, std::vector<BoolVar>(n_teams));
    play[d].assign(n_teams, std::vector<BoolVar>(n_teams));
    for (int i = 0; i < n_teams; ++i)
      for (int j = 0; j < n_teams; ++j)
        if (i != j) home[d][i][j] = model.NewBoolVar();
    for (int i = 0; i < n_teams; ++i)
      for (int j = i + 1; j < n_teams; ++j) {
        const BoolVar meet = model.NewBoolVar();
        model.AddEquality(meet, home[d][i][j] + home[d][j][i]);
        play[d][i][j] = meet;
        play[d][j][i] = meet;
      }
    for (int i = 0; i < n_teams; ++i) {
      is_home[d].push_back(model.NewBoolVar());
      is_away[d].push_back(model.NewBoolVar());
      is_bye[d].push_back(model.NewBoolVar());
      LinearExpr hosts, visits;
      for (int j = 0; j < n_teams; ++j) {
        if (i == j) continue;
        hosts += home[d][i][j];
        visits += home[d][j][i];
      }
      model.AddEquality(is_home[d][i], hosts);
      model.AddEquality(is_away[d][i], visits);
      // A team has one opponent on a day, or a bye: when team i plays team j,
      // team j plays team i, one of them at home and the other away.
      model.AddEquality(is_home[d][i] + is_away[d][i] + is_bye[d][i], 1);
    }
  }

  // config[d][i]: the opponent of team i on day d, or i itself on a bye.
  // where[d][i]: 0 when team i plays at home, 1 on a bye, 2 when away.
  std::vector<std::vector<IntVar>> config(n_days), where(n_days);
  for (int d = 0; d < n_days; ++d) {
    for (int i = 0; i < n_teams; ++i) {
      LinearExpr opponent = i * is_bye[d][i];
      for (int j = 0; j < n_teams; ++j)
        if (j != i) opponent += j * play[d][i][j];
      const IntVar c = model.NewIntVar(Domain(0, n_teams - 1));
      model.AddEquality(c, opponent);
      config[d].push_back(c);
      const IntVar w = model.NewIntVar(Domain(0, 2));
      model.AddEquality(w, is_bye[d][i] + 2 * is_away[d][i]);
      where[d].push_back(w);
    }
    // A team cannot have different opponents on the same day.
    model.AddAllDifferent(config[d]);
  }

  // Double round-robin: each team plays every other team once at home.
  for (int i = 0; i < n_teams; ++i)
    for (int j = 0; j < n_teams; ++j) {
      if (i == j) continue;
      LinearExpr hosted;
      for (int d = 0; d < n_days; ++d) hosted += home[d][i][j];
      model.AddEquality(hosted, 1);
    }

  // 1. Mirroring: on mirrored days a team meets the same opponent with home
  //    and away swapped (byes stay byes).
  for (int d = 0; d < n_days; ++d)
    for (int i = 0; i < n_teams; ++i)
      for (int j = 0; j < n_teams; ++j)
        if (i != j) model.AddEquality(home[d][i][j], home[scheme[d]][j][i]);

  // 2. No team plays away on both last dates.
  for (int t = 0; t < n_teams; ++t)
    model.AddLessOrEqual(is_away[n_days - 2][t] + is_away[n_days - 1][t], 1);

  // 3. Home/away/bye patterns, over every window of consecutive days.
  for (int t = 0; t < n_teams; ++t) {
    for (int d = 0; d + 3 <= n_days; ++d) {
      // No more than two home matches in a row, and no more than two away.
      model.AddLessOrEqual(is_home[d][t] + is_home[d + 1][t] + is_home[d + 2][t], 2);
      model.AddLessOrEqual(is_away[d][t] + is_away[d + 1][t] + is_away[d + 2][t], 2);
    }
    for (int d = 0; d + 4 <= n_days; ++d) {
      // No more than three away matches or byes in a row.
      LinearExpr away_or_bye;
      for (int k = d; k < d + 4; ++k) away_or_bye += is_away[k][t] + is_bye[k][t];
      model.AddLessOrEqual(away_or_bye, 3);
    }
    for (int d = 0; d + 5 <= n_days; ++d) {
      // No more than four home matches or byes in a row.
      LinearExpr home_or_bye;
      for (int k = d; k < d + 5; ++k) home_or_bye += is_home[k][t] + is_bye[k][t];
      model.AddLessOrEqual(home_or_bye, 4);
    }
  }

  // Weekends are the even dates, i.e. the odd 0-based days.
  std::vector<int> weekends;
  for (int d = 1; d < n_days; d += 2) weekends.push_back(d);

  for (int t = 0; t < n_teams; ++t) {
    // 4. Of the weekends, each team plays four at home, four away, and has one bye.
    LinearExpr w_home, w_away, w_bye;
    for (int d : weekends) {
      w_home += is_home[d][t];
      w_away += is_away[d][t];
      w_bye += is_bye[d][t];
    }
    model.AddEquality(w_home, 4);
    model.AddEquality(w_away, 4);
    model.AddEquality(w_bye, 1);

    // 5. Each team plays at home or has a bye on at least two of the first five weekends.
    LinearExpr first;
    for (int k = 0; k < 5; ++k) first += is_home[weekends[k]][t] + is_bye[weekends[k]][t];
    model.AddGreaterOrEqual(first, 2);
  }

  // 6. On the last date every team except FSU plays its rival, unless it
  //    plays FSU or has a bye.
  const int last = n_days - 1;
  for (int t = 0; t < n_teams; ++t) {
    if (t == FSU) continue;
    model.AddBoolOr({play[last][t][rivals[t]], play[last][t][FSU], is_bye[last][t]});
  }

  // 7. Wake-UNC, Wake-Duke, GT-UNC and GT-Duke each meet at least once in dates 11 to 18.
  for (const auto& [a, b] : std::vector<std::pair<int, int>>{
           {WAKE, UNC}, {WAKE, DUKE}, {GT, UNC}, {GT, DUKE}}) {
    std::vector<BoolVar> meetings;
    for (int d = 10; d < n_days; ++d) meetings.push_back(play[d][a][b]);
    model.AddBoolOr(meetings);
  }

  // 8. Opponent sequences.
  const int trio[3] = {UNC, DUKE, WAKE};
  for (int t = 0; t < n_teams; ++t) {
    if (t != DUKE && t != UNC) {
      // No team plays away against UNC and then away against Duke on the
      // next date, or the other way round (away at X means X is at home).
      for (int d = 0; d + 1 < n_days; ++d) {
        model.AddBoolOr({home[d][UNC][t].Not(), home[d + 1][DUKE][t].Not()});
        model.AddBoolOr({home[d][DUKE][t].Not(), home[d + 1][UNC][t].Not()});
      }
    }
    if (t != UNC && t != DUKE && t != WAKE) {
      // No team plays UNC, Duke and Wake on three consecutive dates, in any order.
      for (int d = 0; d + 2 < n_days; ++d)
        for (int a = 0; a < 3; ++a)
          for (int b = 0; b < 3; ++b) {
            if (b == a) continue;
            const int c = 3 - a - b;
            model.AddBoolOr({play[d][t][trio[a]].Not(), play[d + 1][t][trio[b]].Not(),
                             play[d + 2][t][trio[c]].Not()});
          }
    }
  }

  // 9. Other constraints.
  // UNC plays its rival Duke on the last date and on date 11.
  model.AddEquality(play[10][UNC][DUKE], 1);
  model.AddEquality(play[last][UNC][DUKE], 1);
  // UNC plays Clem on the second date.
  model.AddEquality(play[1][UNC][CLEM], 1);
  // Duke has a bye on date 16.
  model.AddEquality(is_bye[15][DUKE], 1);
  // Wake does not play at home on date 17.
  model.AddEquality(is_home[16][WAKE], 0);
  // Wake has a bye on the first date.
  model.AddEquality(is_bye[0][WAKE], 1);
  // Clem, Duke, UMD and Wake do not play away on the last date.
  for (int t : {CLEM, DUKE, UMD, WAKE}) model.AddEquality(is_away[last][t], 0);
  // Clem, FSU, GT and Wake do not play away on the first date.
  for (int t : {CLEM, FSU, GT, WAKE}) model.AddEquality(is_away[0][t], 0);
  // Neither FSU nor NCSt has a bye on the last date.
  for (int t : {FSU, NCSt}) model.AddEquality(is_bye[last][t], 0);
  // UNC does not have a bye on the first date.
  model.AddEquality(is_bye[0][UNC], 0);

  json c_out = json::array(), w_out = json::array();
  for (int d = 0; d < n_days; ++d) {
    json c_row = json::array(), w_row = json::array();
    for (int i = 0; i < n_teams; ++i) {
      c_row.push_back(config[d][i].index());
      w_row.push_back(where[d][i].index());
    }
    c_out.push_back(c_row);
    w_out.push_back(w_row);
  }
  outputs = {{"config", c_out}, {"where", w_out}};
}
