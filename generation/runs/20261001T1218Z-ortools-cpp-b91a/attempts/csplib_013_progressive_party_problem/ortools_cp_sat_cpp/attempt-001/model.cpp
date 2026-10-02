#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Progressive party: pick as few host boats as possible and timetable which
// boat each crew visits in every period, within the boats' capacities.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n_boats = instance.at("n_boats").get<int>();
  const int n_periods = instance.at("n_periods").get<int>();
  const std::vector<int64_t> capacity =
      instance.at("capacity").get<std::vector<int64_t>>();
  const std::vector<int64_t> crew_size =
      instance.at("crew_size").get<std::vector<int64_t>>();

  // is_host[b]: boat b is a host boat.
  // visits[p][c]: the boat that the crew of boat c is on during period p
  // (its own boat when it stays as host).
  // goes[p][c][b]: crew c is on boat b during period p.  It is the 0/1 form of
  // visits[p][c] (exactly one boat per crew and period), so the capacity and
  // meeting rules below stay linear.
  std::vector<BoolVar> is_host;
  for (int b = 0; b < n_boats; ++b) is_host.push_back(model.NewBoolVar());

  std::vector<std::vector<IntVar>> visits(n_periods);
  std::vector<std::vector<std::vector<BoolVar>>> goes(n_periods);
  for (int p = 0; p < n_periods; ++p) {
    goes[p].resize(n_boats);
    for (int c = 0; c < n_boats; ++c) {
      visits[p].push_back(model.NewIntVar(Domain(0, n_boats - 1)));
      LinearExpr one_boat;
      LinearExpr boat_index;
      for (int b = 0; b < n_boats; ++b) {
        goes[p][c].push_back(model.NewBoolVar());
        one_boat += goes[p][c][b];
        boat_index += b * goes[p][c][b];
      }
      model.AddEquality(one_boat, 1);
      model.AddEquality(visits[p][c], boat_index);
    }
  }

  // Crews of host boats stay on their own boat in every period.
  for (int b = 0; b < n_boats; ++b) {
    for (int p = 0; p < n_periods; ++p) {
      model.AddImplication(is_host[b], goes[p][b][b]);
    }
  }

  // The crews aboard a boat in a period can never exceed its capacity.
  for (int p = 0; p < n_periods; ++p) {
    for (int b = 0; b < n_boats; ++b) {
      LinearExpr people_aboard;
      for (int c = 0; c < n_boats; ++c) {
        people_aboard += crew_size[c] * goes[p][c][b];
      }
      model.AddLessOrEqual(people_aboard, capacity[b]);
    }
  }

  // A guest boat cannot visit the same boat twice: for a non-host boat b,
  // the values of visits[.][b] are all different, i.e. every boat is visited
  // at most once over the periods.  (CP-SAT has no enforced AllDifferent, so
  // this is stated as one "at most once" count per visited boat.)
  for (int b = 0; b < n_boats; ++b) {
    for (int target = 0; target < n_boats; ++target) {
      LinearExpr times_visited;
      for (int p = 0; p < n_periods; ++p) times_visited += goes[p][b][target];
      model.AddLessOrEqual(times_visited, 1).OnlyEnforceIf(is_host[b].Not());
    }
  }

  // Non-host boats cannot be visited: if any crew is on boat b, b is a host.
  for (int p = 0; p < n_periods; ++p) {
    for (int c = 0; c < n_boats; ++c) {
      for (int b = 0; b < n_boats; ++b) {
        model.AddImplication(goes[p][c][b], is_host[b]);
      }
    }
  }

  // Two crews cannot meet more than once: they meet in period p when they are
  // on the same boat.  Both directions of the reification are posted so that
  // meet is pinned to "visits are equal".
  for (int c1 = 0; c1 < n_boats; ++c1) {
    for (int c2 = c1 + 1; c2 < n_boats; ++c2) {
      LinearExpr meetings;
      for (int p = 0; p < n_periods; ++p) {
        BoolVar meet = model.NewBoolVar();
        model.AddEquality(visits[p][c1], visits[p][c2]).OnlyEnforceIf(meet);
        model.AddNotEqual(visits[p][c1], visits[p][c2])
            .OnlyEnforceIf(meet.Not());
        meetings += meet;
      }
      model.AddLessOrEqual(meetings, 1);
    }
  }

  // Minimise the number of host boats.
  LinearExpr hosts;
  for (int b = 0; b < n_boats; ++b) hosts += is_host[b];
  model.Minimize(hosts);

  json host_out = json::array();
  for (const BoolVar& b : is_host) host_out.push_back(b.index());
  json visits_out = json::array();
  for (int p = 0; p < n_periods; ++p) {
    json row = json::array();
    for (int c = 0; c < n_boats; ++c) row.push_back(visits[p][c].index());
    visits_out.push_back(row);
  }
  outputs = {{"is_host", host_out}, {"visits", visits_out}};
}
