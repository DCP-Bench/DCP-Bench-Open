// Finding celebrities: a celebrity is known by everybody else at the party and knows only other celebrities.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // graph[i][j] = 1 if person i knows person j (the diagonal is not used)
  std::vector<std::vector<int>> graph = instance.at("graph").get<std::vector<std::vector<int>>>();
  int n = static_cast<int>(graph.size());

  // c[i] = 1 if person i is a celebrity
  vec<IntVar*> c;
  createVars(c, n, 0, 1, true);

  // at least one celebrity is present at the party
  int_linear(c, IRT_GE, 1);

  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < n; ++j) {
      if (i == j) continue;
      // a celebrity is known by everybody: if person j does not know person i, then i is not a celebrity
      if (graph[j][i] == 0) int_rel(c[i], IRT_EQ, 0);
      // a celebrity knows only celebrities: if i knows j and i is a celebrity, then j is a celebrity
      if (graph[i][j] == 1) int_rel(c[i], IRT_LE, c[j], 0);
    }
  }

  branch(c, VAR_INORDER, VAL_MIN);

  json flags = json::array();
  for (int i = 0; i < n; ++i) flags.push_back(dcp::out(c[i]));
  outputs = {{"celebrities", flags}};
}
