// Kidney exchange: people on a waiting list donate kidneys to each other. Person i can donate to the people in
// compatible[i]. Anyone who gives a kidney must receive one, and nobody receives more than one kidney.
// Maximise the number of people who receive a kidney.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("num_people");
  auto compatible = instance.at("compatible").get<std::vector<std::vector<int>>>();

  // allowed[i][j] is true when person i can donate to person j (1-based ids in the instance)
  std::vector<std::vector<char>> allowed(n, std::vector<char>(n, 0));
  for (int i = 0; i < n; ++i)
    for (int j : compatible[i])
      if (j >= 1 && j <= n && j - 1 != i) allowed[i][j - 1] = 1;

  // to[i] is the person who receives the kidney of person i; to[i] = i means person i does not donate.
  // The values form a permutation: nobody receives more than one kidney, and whoever gives a kidney
  // (to[i] != i) also receives one (the person who gives to i is not i itself).
  vec<IntVar*> to;
  createVars(to, n, 0, n - 1);
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j)
      if (j != i && !allowed[i][j]) int_rel(to[i], IRT_NE, j);
  all_different(to, CL_DOM);

  // gift01[i*n+j] is 1 when person i donates to person j (row-major)
  vec<IntVar*> gift01;
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) {
      IntVar* g = newIntVar(0, 1);
      if (i != j && allowed[i][j]) {
        BoolView b = newBoolVar();
        int_rel_reif(to[i], IRT_EQ, j, b);
        bool2int(b, g);
      } else {
        int_rel(g, IRT_EQ, 0);
      }
      gift01.push(g);
    }

  // maximize the number of people that receive a new kidney. Everybody who gives receives, so these are the people
  // with to[i] != i; keep[i] is 1 when person i neither gives nor receives
  vec<IntVar*> keep;
  for (int i = 0; i < n; ++i) {
    BoolView b = newBoolVar();
    int_rel_reif(to[i], IRT_EQ, i, b);
    IntVar* k = newIntVar(0, 1);
    bool2int(b, k);
    keep.push(k);
  }
  IntVar* received = newIntVar(0, n);
  keep.push(received);
  int_linear(keep, IRT_EQ, n);

  vec<IntVar*> obj;
  obj.push(received);
  branch(obj, VAR_INORDER, VAL_MAX);
  branch(to, VAR_SIZE_MIN, VAL_MIN);
  optimize(received, OPT_MAX);

  // transplants[i][j] is 1 when person i donates to person j
  json rows = json::array();
  for (int i = 0; i < n; ++i) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(dcp::out(gift01[i * n + j]));
    rows.push_back(row);
  }
  outputs = {{"transplants", rows}};
}
