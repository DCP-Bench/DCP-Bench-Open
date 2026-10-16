// Progressive party: choose host boats and, in each period, send every guest crew to a host
// so that capacities hold, no guest revisits a host and no two guest crews meet twice;
// minimize the number of hosts.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int B = instance.at("n_boats");
  int T = instance.at("n_periods");
  std::vector<int> capacity = instance.at("capacity").get<std::vector<int>>();
  std::vector<int> crew = instance.at("crew_size").get<std::vector<int>>();

  // is_host[b] = 1 if boat b is a host boat (host_lit[b] is the same as a Boolean)
  vec<IntVar*> is_host;
  vec<BoolView> host_lit;
  for (int b = 0; b < B; ++b) {
    IntVar* h;
    createVar(h, 0, 1, true);
    BoolView l = newBoolVar();
    bool2int(l, h);
    is_host.push(h);
    host_lit.push(l);
  }

  // visits[p][b] = boat visited by boat b in period p; the crew of a host boat remains on
  // board, so a host boat visits itself
  vec<vec<IntVar*>> visits;
  createVars(visits, T, B, 0, B - 1, true);

  // a boat is a host exactly when it stays on its own boat (a guest never visits itself,
  // since only host boats can be visited)
  for (int p = 0; p < T; ++p)
    for (int b = 0; b < B; ++b) int_rel_reif(visits[p][b], IRT_EQ, b, host_lit[b]);

  // the crews of guest boats visit host boats
  IntVar* one = getConstant(1);
  for (int p = 0; p < T; ++p)
    for (int b = 0; b < B; ++b) array_var_int_element_bound(visits[p][b], is_host, one);

  // at[p][b][h] = 1 if in period p boat b is aboard boat h
  std::vector<std::vector<std::vector<IntVar*>>> at(
      T, std::vector<std::vector<IntVar*>>(B, std::vector<IntVar*>(B)));
  for (int p = 0; p < T; ++p)
    for (int b = 0; b < B; ++b)
      for (int h = 0; h < B; ++h) {
        BoolView l = newBoolVar();
        int_rel_reif(visits[p][b], IRT_EQ, h, l);
        createVar(at[p][b][h], 0, 1, true);
        bool2int(l, at[p][b][h]);
      }

  // the total number of people aboard a boat, host crew and guest crews, must not exceed
  // its capacity, in every period
  for (int p = 0; p < T; ++p)
    for (int h = 0; h < B; ++h) {
      vec<int> co;
      vec<IntVar*> vs;
      for (int b = 0; b < B; ++b) { co.push(crew[b]); vs.push(at[p][b][h]); }
      int_linear(co, vs, IRT_LE, capacity[h]);
    }

  // a guest boat cannot revisit a host
  for (int b = 0; b < B; ++b)
    for (int h = 0; h < B; ++h) {
      if (b == h) continue;
      vec<IntVar*> vs;
      for (int p = 0; p < T; ++p) vs.push(at[p][b][h]);
      int_linear(vs, IRT_LE, 1);
    }

  // guest crews cannot meet more than once: two boats are on the same host in at most one period
  for (int b1 = 0; b1 < B; ++b1)
    for (int b2 = b1 + 1; b2 < B; ++b2) {
      vec<IntVar*> meets;
      for (int p = 0; p < T; ++p) {
        BoolView l = newBoolVar();
        int_rel_reif(visits[p][b1], IRT_EQ, visits[p][b2], l);
        IntVar* m;
        createVar(m, 0, 1, true);
        bool2int(l, m);
        meets.push(m);
      }
      int_linear(meets, IRT_LE, 1);
    }

  // minimize the number of host boats
  IntVar* hosts = newIntVar(0, B);
  int_linear(is_host, IRT_EQ, hosts);
  branch(is_host, VAR_INORDER, VAL_MIN);
  vec<IntVar*> flat;
  flatten(visits, flat);
  branch(flat, VAR_INORDER, VAL_MIN);
  optimize(hosts, OPT_MIN);

  json host_out = json::array();
  for (int b = 0; b < B; ++b) host_out.push_back(dcp::out(is_host[b]));
  json rows = json::array();
  for (int p = 0; p < T; ++p) {
    json row = json::array();
    for (int b = 0; b < B; ++b) row.push_back(dcp::out(visits[p][b]));
    rows.push_back(row);
  }
  outputs = {{"is_host", host_out}, {"visits", rows}};
}
