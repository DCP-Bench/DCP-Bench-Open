#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Sports tournament scheduling (CSPLib 26): schedule n teams over n-1 weeks,
// each week split into n/2 periods with one match per period (a home team and
// an away team), so that every team plays once a week, every team plays at
// most twice in the same period over the tournament, and every team plays
// every other team. Teams are numbered 1..n.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n_teams = instance.at("n_teams").get<int>();
  const int n_weeks = n_teams - 1;
  const int n_periods = n_teams / 2;

  // home[w][p] / away[w][p]: the team playing at home / away in week w, period p.
  // is_home[w][p][t] / is_away[w][p][t] are their one-hot Boolean views
  // (team t + 1), used to count appearances and to state which pairs meet.
  std::vector<std::vector<IntVar>> home(n_weeks), away(n_weeks);
  std::vector<std::vector<std::vector<BoolVar>>> is_home(n_weeks), is_away(n_weeks);
  for (int w = 0; w < n_weeks; ++w) {
    is_home[w].resize(n_periods);
    is_away[w].resize(n_periods);
    for (int p = 0; p < n_periods; ++p) {
      const IntVar h = model.NewIntVar(Domain(1, n_teams));
      const IntVar a = model.NewIntVar(Domain(1, n_teams));
      home[w].push_back(h);
      away[w].push_back(a);
      LinearExpr h_value, a_value;
      for (int t = 0; t < n_teams; ++t) {
        is_home[w][p].push_back(model.NewBoolVar());
        is_away[w][p].push_back(model.NewBoolVar());
        h_value += (t + 1) * is_home[w][p][t];
        a_value += (t + 1) * is_away[w][p][t];
      }
      model.AddExactlyOne(is_home[w][p]);
      model.AddExactlyOne(is_away[w][p]);
      model.AddEquality(h, h_value);
      model.AddEquality(a, a_value);

      // A team cannot play itself.
      model.AddNotEqual(h, a);
    }
  }

  // Every team plays once a week: the home and away teams of a week are all different.
  for (int w = 0; w < n_weeks; ++w) {
    std::vector<IntVar> week(home[w]);
    week.insert(week.end(), away[w].begin(), away[w].end());
    model.AddAllDifferent(week);
  }

  // Every team plays every other team: for each pair t1 < t2 there is a slot
  // where t1 is home and t2 away, or the reverse. meets is true only if that
  // slot really has this match (one direction suffices for "at least one").
  for (int t1 = 0; t1 < n_teams; ++t1) {
    for (int t2 = t1 + 1; t2 < n_teams; ++t2) {
      std::vector<BoolVar> meetings;
      for (int w = 0; w < n_weeks; ++w)
        for (int p = 0; p < n_periods; ++p) {
          const BoolVar forward = model.NewBoolVar();  // t1 home, t2 away
          model.AddImplication(forward, is_home[w][p][t1]);
          model.AddImplication(forward, is_away[w][p][t2]);
          const BoolVar backward = model.NewBoolVar();  // t2 home, t1 away
          model.AddImplication(backward, is_home[w][p][t2]);
          model.AddImplication(backward, is_away[w][p][t1]);
          meetings.push_back(forward);
          meetings.push_back(backward);
        }
      model.AddBoolOr(meetings);
    }
  }

  // Every team plays at most twice in the same period. A team cannot be both
  // home and away in one slot, so "home or away" is counted as a sum.
  for (int t = 0; t < n_teams; ++t)
    for (int p = 0; p < n_periods; ++p) {
      LinearExpr appearances;
      for (int w = 0; w < n_weeks; ++w) appearances += is_home[w][p][t] + is_away[w][p][t];
      model.AddLessOrEqual(appearances, 2);
    }

  json h_out = json::array(), a_out = json::array();
  for (int w = 0; w < n_weeks; ++w) {
    json h_row = json::array(), a_row = json::array();
    for (int p = 0; p < n_periods; ++p) {
      h_row.push_back(home[w][p].index());
      a_row.push_back(away[w][p].index());
    }
    h_out.push_back(h_row);
    a_out.push_back(a_row);
  }
  outputs = {{"home", h_out}, {"away", a_out}};
}
