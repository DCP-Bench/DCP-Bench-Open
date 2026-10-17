// Template design (CSPLib 002): a colour printing firm prints cartons from aluminium
// templates. Each template has n_slots positions, and each position carries one design
// variation. Decide how many distinct templates to make (n_templates), which variations
// and how many copies of each go on each template, and how many sheets to print from
// each template, so that every variation meets its demand, minimising the total number
// of printed sheets.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int T = instance.at("n_templates").get<int>();
  int V = instance.at("n_var").get<int>();
  int S = instance.at("n_slots").get<int>();
  std::vector<int> demand = instance.at("demand").get<std::vector<int>>();

  // Sheets printed from one template never need to exceed the largest demand: a template
  // with more sheets than that over-supplies every variation it carries. Production is
  // written in binary: bit j has weight 2^j.
  long long total = 0, dmax = 0;
  for (int d : demand) { total += d; if (d > dmax) dmax = d; }
  int J = 0;
  while ((1LL << J) - 1 < dmax) ++J;

  // Copies of variation v on template t, each between 0 and n_slots.
  std::vector<std::vector<dcp::Lin>> layout(T, std::vector<dcp::Lin>(V));
  for (int t = 0; t < T; ++t)
    for (int v = 0; v < V; ++v) layout[t][v] = dcp::new_var(h, 0, S);

  // Sheets printed from template t, as binary bits.
  std::vector<std::vector<dcp::Lin>> bit(T, std::vector<dcp::Lin>(J));
  std::vector<dcp::Lin> production(T);
  for (int t = 0; t < T; ++t) {
    for (int j = 0; j < J; ++j) bit[t][j] = dcp::new_var(h, 0, 1);
    dcp::Lin p;
    for (int j = 0; j < J; ++j) p = p + (double)(1LL << j) * bit[t][j];
    production[t] = p;
    dcp::add_row(h, p, -kHighsInf, (double)dmax);
  }

  // Template t holds at most n_slots designs, one per position.
  for (int t = 0; t < T; ++t) {
    dcp::Lin used;
    for (int v = 0; v < V; ++v) used = used + layout[t][v];
    dcp::add_row(h, used, -kHighsInf, S);
  }

  // u[t][v][j] = layout[t][v] * bit[t][j], linearised with the bounds of layout (0..S).
  std::vector<std::vector<std::vector<dcp::Lin>>> u(
      T, std::vector<std::vector<dcp::Lin>>(V, std::vector<dcp::Lin>(J)));
  for (int t = 0; t < T; ++t)
    for (int v = 0; v < V; ++v)
      for (int j = 0; j < J; ++j) {
        u[t][v][j] = dcp::new_var(h, 0, S);
        // u <= S * bit
        dcp::add_row(h, u[t][v][j] - (double)S * bit[t][j], -kHighsInf, 0);
        // u <= layout
        dcp::add_row(h, u[t][v][j] - layout[t][v], -kHighsInf, 0);
        // u >= layout - S * (1 - bit)
        dcp::add_row(h, u[t][v][j] - layout[t][v] - (double)S * bit[t][j], -S, kHighsInf);
      }

  // The items printed from template t, over all variations, fill at most n_slots positions
  // for each sheet: the sum over variations of layout * production is at most n_slots * production.
  std::vector<dcp::Lin> printed_var(V);
  for (int v = 0; v < V; ++v)
    for (int t = 0; t < T; ++t)
      for (int j = 0; j < J; ++j) printed_var[v] = printed_var[v] + (double)(1LL << j) * u[t][v][j];
  for (int t = 0; t < T; ++t) {
    dcp::Lin items;
    for (int v = 0; v < V; ++v)
      for (int j = 0; j < J; ++j) items = items + (double)(1LL << j) * u[t][v][j];
    dcp::add_row(h, items - (double)S * production[t], -kHighsInf, 0);
  }

  // Every variation is printed at least as many items as its demand.
  for (int v = 0; v < V; ++v) dcp::add_row(h, printed_var[v], demand[v], kHighsInf);

  // Templates are interchangeable: list them by decreasing number of sheets.
  for (int t = 0; t + 1 < T; ++t) dcp::add_row(h, production[t] - production[t + 1], 0, kHighsInf);

  dcp::Lin sheets;
  for (int t = 0; t < T; ++t) sheets = sheets + production[t];
  out.minimize(sheets);

  out.add("layout", layout);
  out.add("production", production);
}
