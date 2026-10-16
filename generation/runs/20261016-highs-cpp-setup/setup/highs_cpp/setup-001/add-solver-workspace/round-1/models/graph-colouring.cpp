// Graph colouring with the minimum number of colours.
// x[i][c] binary: node i has colour c. used[c] binary: colour c appears. Minimise sum used[c].
#include <algorithm>
#include <cstdio>
#include <fstream>
#include <vector>

#include <nlohmann/json.hpp>

#include "Highs.h"

static HighsInt newBin(Highs& h) {
  HighsInt k = h.getNumCol();
  h.addVar(0, 1);
  h.changeColIntegrality(k, HighsVarType::kInteger);
  return k;
}

int main(int argc, char** argv) {
  if (argc < 2) return 1;
  std::ifstream file(argv[1]);
  nlohmann::json data = nlohmann::json::parse(file);
  const int n = data.at("n_nodes").get<int>();
  std::vector<std::vector<int>> edges = data.at("edges").get<std::vector<std::vector<int>>>();

  // Greedy colouring uses at most maxdeg + 1 colours, so no optimum needs more.
  std::vector<int> deg(n, 0);
  for (const auto& e : edges) { deg[e[0]]++; deg[e[1]]++; }
  int maxdeg = n > 0 ? *std::max_element(deg.begin(), deg.end()) : 0;
  const int K = std::max(1, std::min(n, maxdeg + 1));

  Highs h;
  h.setOptionValue("output_flag", false);
  h.setOptionValue("threads", HighsInt{1});
  h.setOptionValue("mip_rel_gap", 0.0);
  h.setOptionValue("mip_abs_gap", 0.0);
  h.changeObjectiveSense(ObjSense::kMinimize);

  // Columns: x[i][c] = i * K + c, then used[c] = n * K + c.
  for (int i = 0; i < n * K; ++i) newBin(h);
  for (int c = 0; c < K; ++c) {
    HighsInt u = newBin(h);
    h.changeColCost(u, 1);
  }

  // Every node gets exactly one colour.
  for (int i = 0; i < n; ++i) {
    std::vector<HighsInt> cols;
    std::vector<double> ones;
    for (int c = 0; c < K; ++c) { cols.push_back(i * K + c); ones.push_back(1); }
    h.addRow(1, 1, K, cols.data(), ones.data());
  }

  // Endpoints of an edge differ.
  for (const auto& e : edges) {
    for (int c = 0; c < K; ++c) {
      HighsInt cols[2] = {e[0] * K + c, e[1] * K + c};
      double vals[2] = {1, 1};
      h.addRow(-kHighsInf, 1, 2, cols, vals);
    }
  }

  // A colour used by a node counts as used.
  for (int i = 0; i < n; ++i) {
    for (int c = 0; c < K; ++c) {
      HighsInt cols[2] = {i * K + c, n * K + c};
      double vals[2] = {1, -1};
      h.addRow(-kHighsInf, 0, 2, cols, vals);
    }
  }

  h.run();
  if (h.getModelStatus() != HighsModelStatus::kOptimal) {
    std::fprintf(stderr, "not solved: %s\n", h.modelStatusToString(h.getModelStatus()).c_str());
    return 1;
  }

  const std::vector<double>& val = h.getSolution().col_value;
  std::printf("{\"colour\": [");
  for (int i = 0; i < n; ++i) {
    int colour = 0;
    for (int c = 0; c < K; ++c) {
      if (val[i * K + c] > 0.5) { colour = c; break; }
    }
    std::printf("%s%d", i ? ", " : "", colour);
  }
  std::printf("]}\n");
  return 0;
}
