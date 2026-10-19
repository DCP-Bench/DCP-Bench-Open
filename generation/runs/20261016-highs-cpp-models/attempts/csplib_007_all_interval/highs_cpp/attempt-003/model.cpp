// csplib_007_all_interval: find a series x of the pitch-classes 0..n-1, each occurring exactly once,
// whose neighbouring intervals |x[i+1] - x[i]| cover each of the values 1..n-1 exactly once.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n").get<int>();

  // the pitch-class at each position of the series, 0..n-1
  std::vector<dcp::Lin> x;
  for (int i = 0; i < n; i++) x.push_back(dcp::new_var(h, 0, n - 1));

  // the interval between neighbouring positions i and i+1, 1..n-1
  std::vector<dcp::Lin> diffs;
  for (int i = 0; i < n - 1; i++) diffs.push_back(dcp::new_var(h, 1, n - 1));

  // y[i][v] = 1 when position i holds pitch-class v
  std::vector<std::vector<dcp::Lin>> y(n, std::vector<dcp::Lin>(n));
  for (int i = 0; i < n; i++)
    for (int v = 0; v < n; v++) y[i][v] = dcp::new_var(h, 0, 1);

  // each position holds exactly one pitch-class
  for (int i = 0; i < n; i++) {
    dcp::Lin s = 0.0;
    for (int v = 0; v < n; v++) s = s + y[i][v];
    dcp::add_row(h, s, 1, 1);
  }

  // each pitch-class occurs in exactly one position
  for (int v = 0; v < n; v++) {
    dcp::Lin s = 0.0;
    for (int i = 0; i < n; i++) s = s + y[i][v];
    dcp::add_row(h, s, 1, 1);
  }

  // the pitch-class of each position is the value chosen by its indicators
  for (int i = 0; i < n; i++) {
    dcp::Lin s = 0.0;
    for (int v = 0; v < n; v++) s = s + (double)v * y[i][v];
    dcp::add_row(h, x[i] - s, 0, 0);
  }

  // for each neighbouring pair, up[i][k] = 1 when x[i+1] - x[i] = +k and down[i][k] = 1 when it is -k
  // (k = 1..n-1); exactly one of these holds, so no big-M is needed
  std::vector<std::vector<dcp::Lin>> up(n - 1, std::vector<dcp::Lin>(n));
  std::vector<std::vector<dcp::Lin>> down(n - 1, std::vector<dcp::Lin>(n));
  for (int i = 0; i < n - 1; i++)
    for (int k = 1; k < n; k++) {
      up[i][k] = dcp::new_var(h, 0, 1);
      down[i][k] = dcp::new_var(h, 0, 1);
    }

  for (int i = 0; i < n - 1; i++) {
    // each neighbouring pair has exactly one signed difference
    dcp::Lin s = 0.0;
    for (int k = 1; k < n; k++) s = s + up[i][k] + down[i][k];
    dcp::add_row(h, s, 1, 1);

    // the difference x[i+1] - x[i] is the signed size chosen for this pair
    dcp::Lin signed_diff = 0.0;
    for (int k = 1; k < n; k++) signed_diff = signed_diff + (double)k * up[i][k] - (double)k * down[i][k];
    dcp::add_row(h, x[i + 1] - x[i] - signed_diff, 0, 0);

    // diffs[i] is the absolute value of that difference
    dcp::Lin size = 0.0;
    for (int k = 1; k < n; k++) size = size + (double)k * (up[i][k] + down[i][k]);
    dcp::add_row(h, diffs[i] - size, 0, 0);
  }

  // the intervals cover each of 1..n-1 exactly once: each size k is used by exactly one pair
  for (int k = 1; k < n; k++) {
    dcp::Lin s = 0.0;
    for (int i = 0; i < n - 1; i++) s = s + up[i][k] + down[i][k];
    dcp::add_row(h, s, 1, 1);
  }

  // adjacency view: adj[i][a][b] = 1 when position i holds pitch-class a and position i+1 holds b
  // (a != b). The product is linearised exactly by the three rows after its declaration.
  std::vector<std::vector<std::vector<dcp::Lin>>> adj(
      n - 1, std::vector<std::vector<dcp::Lin>>(n, std::vector<dcp::Lin>(n)));
  for (int i = 0; i < n - 1; i++)
    for (int a = 0; a < n; a++)
      for (int b = 0; b < n; b++) {
        if (a == b) continue;
        adj[i][a][b] = dcp::new_var(h, 0, 1);
        // adj implies position i holds a
        dcp::add_row(h, adj[i][a][b] - y[i][a], -kHighsInf, 0);
        // adj implies position i+1 holds b
        dcp::add_row(h, adj[i][a][b] - y[i + 1][b], -kHighsInf, 0);
        // both hold implies adj
        dcp::add_row(h, adj[i][a][b] - y[i][a] - y[i + 1][b], -1, kHighsInf);
      }

  // each position pair has exactly one ordered pair of pitch-classes
  for (int i = 0; i < n - 1; i++) {
    dcp::Lin s = 0.0;
    for (int a = 0; a < n; a++)
      for (int b = 0; b < n; b++)
        if (a != b) s = s + adj[i][a][b];
    dcp::add_row(h, s, 1, 1);
  }

  // each pitch-class has one or two neighbours in the series: one at an end, two in the middle
  for (int a = 0; a < n; a++) {
    dcp::Lin s = 0.0;
    for (int i = 0; i < n - 1; i++)
      for (int b = 0; b < n; b++) {
        if (a == b) continue;
        s = s + adj[i][a][b] + adj[i][b][a];
      }
    dcp::add_row(h, s, 1, 2);
  }

  out.add("x", x);
  out.add("diffs", diffs);
}
