// Travelling salesman problem: a shortest closed tour visits every city exactly once and returns to the origin.
// Distance between two cities is the Euclidean distance between their points, rounded to an integer.
#include "dcp.h"

#include <algorithm>
#include <cmath>
#include <limits>

// Held-Karp node penalties. Every city is entered once and left once, so with arc cost d[i][j] + pi[i] + pi[j]
// the tour cost grows by exactly 2 * sum(pi). The penalties come from subgradient ascent on the 1-tree bound
// and make the cheap arcs of the reduced cost matrix close to a tour, which tightens the objective bound.
static std::vector<int> HeldKarpPenalties(const std::vector<std::vector<int>>& d, int ub) {
  int n = static_cast<int>(d.size());
  std::vector<double> pi(n, 0.0), best_pi(n, 0.0);
  double best = -1e18, step_scale = 2.0;
  int stall = 0;
  for (int it = 0; it < 400 && n > 3; ++it) {
    auto r = [&](int i, int j) { return d[i][j] + pi[i] + pi[j]; };
    // minimum spanning tree on cities 1..n-1 (Prim), then the two cheapest edges at city 0
    std::vector<double> key(n, 1e18);
    std::vector<int> par(n, -1), deg(n, 0);
    std::vector<bool> in(n, false);
    double w = 0;
    key[1] = 0;
    for (int k = 1; k < n; ++k) {
      int u = -1;
      for (int v = 1; v < n; ++v) if (!in[v] && (u < 0 || key[v] < key[u])) u = v;
      in[u] = true;
      w += key[u];
      if (par[u] >= 0) { deg[u]++; deg[par[u]]++; }
      for (int v = 1; v < n; ++v) if (!in[v] && r(u, v) < key[v]) { key[v] = r(u, v); par[v] = u; }
    }
    int a = -1, b = -1;
    for (int v = 1; v < n; ++v) {
      if (a < 0 || r(0, v) < r(0, a)) { b = a; a = v; }
      else if (b < 0 || r(0, v) < r(0, b)) b = v;
    }
    w += r(0, a) + r(0, b);
    deg[0] = 2; deg[a]++; deg[b]++;
    double sumpi = 0, norm = 0;
    for (int i = 0; i < n; ++i) { sumpi += pi[i]; norm += (deg[i] - 2) * (deg[i] - 2); }
    double bound = w - 2 * sumpi;
    if (bound > best + 1e-9) { best = bound; best_pi = pi; stall = 0; }
    else if (++stall >= 20) { step_scale *= 0.5; stall = 0; }
    if (norm == 0) break;
    double t = step_scale * (ub - bound) / norm;
    for (int i = 0; i < n; ++i) pi[i] += t * (deg[i] - 2);
  }
  std::vector<int> out(n);
  for (int i = 0; i < n; ++i) out[i] = static_cast<int>(std::lround(best_pi[i]));
  return out;
}

void Build(const json& instance, json& outputs) {
  auto loc = instance.at("locations").get<std::vector<std::vector<int>>>();
  int n = static_cast<int>(loc.size());

  // dist[i][j] is the Euclidean distance between cities i and j, rounded to an integer
  std::vector<std::vector<int>> dist(n, std::vector<int>(n, 0));
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) {
      double dx = loc[i][0] - loc[j][0], dy = loc[i][1] - loc[j][1];
      dist[i][j] = static_cast<int>(std::lround(std::sqrt(dx * dx + dy * dy)));
    }

  // an upper bound for the penalty search: length of the tour 0, 1, ..., n-1
  int ub = 0;
  for (int i = 0; i < n; ++i) ub += dist[i][(i + 1) % n];
  std::vector<int> pi = HeldKarpPenalties(dist, ub);
  int pi_sum = 0;
  for (int i = 0; i < n; ++i) pi_sum += pi[i];
  // red[i][j] is the arc cost with penalties; tour length = sum of red over the tour arcs - 2 * pi_sum
  std::vector<std::vector<int>> red(n, std::vector<int>(n, 0));
  int rmin = std::numeric_limits<int>::max(), rmax = std::numeric_limits<int>::min();
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) {
      red[i][j] = dist[i][j] + pi[i] + pi[j];
      if (i != j) { rmin = std::min(rmin, red[i][j]); rmax = std::max(rmax, red[i][j]); }
    }

  // succ[i] is the city visited directly after city i; the successors form one tour through all cities
  vec<IntVar*> succ;
  createVars(succ, n, 0, n - 1);
  for (int i = 0; i < n; ++i) int_rel(succ[i], IRT_NE, i);
  circuit(succ);

  // pred[j] is the city visited directly before city j (inverse of succ)
  vec<IntVar*> pred;
  createVars(pred, n, 0, n - 1);
  inverse(succ, pred);

  // leg[i] is the penalised cost of the arc leaving city i
  vec<IntVar*> leg;
  vec<int> ones;
  for (int i = 0; i < n; ++i) {
    vec<int> row;
    int lo = std::numeric_limits<int>::max(), hi = std::numeric_limits<int>::min();
    for (int j = 0; j < n; ++j) {
      row.push(red[i][j]);
      if (j != i) { lo = std::min(lo, red[i][j]); hi = std::max(hi, red[i][j]); }
    }
    IntVar* li = newIntVar(lo, hi);
    array_int_element(succ[i], row, li);
    leg.push(li);
    ones.push(1);
  }
  IntVar* legsum = newIntVar(n * rmin, n * rmax);
  int_linear(ones, leg, IRT_EQ, legsum);

  // travel_distance is the total length of the tour: the penalised legs minus the penalties
  int total_max = 0;
  for (int i = 0; i < n; ++i) {
    int m = 0;
    for (int j = 0; j < n; ++j) if (j != i) m = std::max(m, dist[i][j]);
    total_max += m;
  }
  IntVar* total = newIntVar(0, total_max);
  {
    vec<int> c; vec<IntVar*> t;
    c.push(1); t.push(legsum); c.push(-1); t.push(total);
    int_linear(c, t, IRT_EQ, 2 * pi_sum);
  }

  // redundant: a city is left and entered by two different arcs; the cost of the pair (succ, pred) of every city
  // is the sum of the penalised costs of these two arcs, and every arc is counted twice (at its tail and its head)
  vec<IntVar*> pc;
  vec<int> ones2;
  for (int i = 0; i < n; ++i) {
    vec<vec<int>> tuples;
    int lo = std::numeric_limits<int>::max(), hi = std::numeric_limits<int>::min();
    for (int s = 0; s < n; ++s)
      for (int p = 0; p < n; ++p) {
        if (s == i || p == i || s == p) continue;
        int v = red[i][s] + red[p][i];
        tuples.push();
        tuples.last().push(s);
        tuples.last().push(p);
        tuples.last().push(v);
        lo = std::min(lo, v);
        hi = std::max(hi, v);
      }
    IntVar* c = newIntVar(lo, hi);
    vec<IntVar*> tv;
    tv.push(succ[i]); tv.push(pred[i]); tv.push(c);
    table(tv, tuples);
    pc.push(c);
    ones2.push(1);
  }
  {
    vec<IntVar*> terms; vec<int> coef;
    for (int i = 0; i < n; ++i) { terms.push(pc[i]); coef.push(1); }
    terms.push(legsum); coef.push(-2);
    int_linear(coef, terms, IRT_EQ, 0);
  }

  branch(leg, VAR_MIN_MIN, VAL_MIN);
  optimize(total, OPT_MIN);

  outputs = {{"travel_distance", dcp::out(total)}};
}
