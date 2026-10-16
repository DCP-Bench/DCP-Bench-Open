#include "dcp.h"

#include <algorithm>
#include <numeric>

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int n = instance.at("n_boats").get<int>();
  const int periods = instance.at("n_periods").get<int>();
  const std::vector<int> cap = instance.at("capacity").get<std::vector<int>>();
  const std::vector<int> crew = instance.at("crew_size").get<std::vector<int>>();

  // Big-M from the data: no boat can ever carry more than all crews together plus its capacity.
  const double big = static_cast<double>(std::accumulate(crew.begin(), crew.end(), 0)) +
                     static_cast<double>(*std::max_element(cap.begin(), cap.end()));

  // is_host[b] = 1 when boat b is a host.
  std::vector<dcp::Lin> is_host;
  for (int b = 0; b < n; ++b) is_host.push_back(dcp::new_var(h, 0, 1));

  // visit[p][g][v] = 1 when, in period p, guest boat g visits host boat v (v != g).
  std::vector<std::vector<std::vector<dcp::Lin>>> visit(
      periods, std::vector<std::vector<dcp::Lin>>(n, std::vector<dcp::Lin>(n)));
  for (int p = 0; p < periods; ++p)
    for (int g = 0; g < n; ++g)
      for (int v = 0; v < n; ++v)
        if (v != g) visit[p][g][v] = dcp::new_var(h, 0, 1);

  // each guest boat visits exactly one host in each period; a host boat visits no other boat
  for (int p = 0; p < periods; ++p)
    for (int g = 0; g < n; ++g) {
      dcp::Lin e = is_host[g];
      for (int v = 0; v < n; ++v)
        if (v != g) e = e + visit[p][g][v];
      dcp::add_row(h, e, 1, 1);
    }

  // guest boats only visit boats that are hosts
  for (int p = 0; p < periods; ++p)
    for (int g = 0; g < n; ++g)
      for (int v = 0; v < n; ++v)
        if (v != g) dcp::add_row(h, visit[p][g][v] - is_host[v], -kHighsInf, 0);

  // the people aboard a host boat (its crew plus the guest crews) do not exceed its capacity
  for (int p = 0; p < periods; ++p)
    for (int v = 0; v < n; ++v) {
      dcp::Lin e = big * is_host[v];
      for (int g = 0; g < n; ++g)
        if (g != v) e = e + static_cast<double>(crew[g]) * visit[p][g][v];
      dcp::add_row(h, e, -kHighsInf, static_cast<double>(cap[v] - crew[v]) + big);
    }

  // a guest boat visits each host boat at most once over all periods
  for (int g = 0; g < n; ++g)
    for (int v = 0; v < n; ++v)
      if (v != g) {
        dcp::Lin e;
        for (int p = 0; p < periods; ++p) e = e + visit[p][g][v];
        dcp::add_row(h, e, -kHighsInf, 1);
      }

  // two guest crews meet at most once: they are aboard the same host in at most one period
  for (int g1 = 0; g1 < n; ++g1)
    for (int g2 = g1 + 1; g2 < n; ++g2) {
      dcp::Lin meet;
      for (int p = 0; p < periods; ++p)
        for (int v = 0; v < n; ++v) {
          if (v == g1 || v == g2) continue;
          // together_pv = 1 exactly when both guest crews visit host v in period p
          dcp::Lin together = dcp::new_var(h, 0, 1, false);
          dcp::add_row(h, together - visit[p][g1][v], -kHighsInf, 0);
          dcp::add_row(h, together - visit[p][g2][v], -kHighsInf, 0);
          dcp::add_row(h, together - visit[p][g1][v] - visit[p][g2][v], -1, kHighsInf);
          meet = meet + together;
        }
      dcp::add_row(h, meet, -kHighsInf, 1);
    }

  // minimise the number of host boats
  dcp::Lin hosts;
  for (int b = 0; b < n; ++b) hosts = hosts + is_host[b];
  out.minimize(hosts);

  // outputs: is_host per boat, and visits[p][b] = the host boat that boat b is at in period p
  // (a host boat is at itself)
  out.add("is_host", is_host);
  std::vector<std::vector<dcp::Lin>> visits(periods, std::vector<dcp::Lin>(n));
  for (int p = 0; p < periods; ++p)
    for (int b = 0; b < n; ++b) {
      dcp::Lin e = static_cast<double>(b) * is_host[b];
      for (int v = 0; v < n; ++v)
        if (v != b) e = e + static_cast<double>(v) * visit[p][b][v];
      visits[p][b] = e;
    }
  out.add("visits", visits);
}
