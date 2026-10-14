// Best host: seat six guests around a table so that nobody sits next to a guest they do not get along with.
// Reading: the objective is satisfaction, so every pair of neighbours must be an allowed pair (zero conflicts).
// The table is circular (Figure 1), so the last seat is next to the first.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // The guest list and who sits next to whom is fixed by the problem statement.
  // 0 Andrew, 1 Betty, 2 Cara, 3 Dave, 4 Erica, 5 Frank
  const int guests = 6;
  // Andrew only sits next to Dave and Frank; Betty next to Cara and Erica; Cara next to Betty and Frank;
  // Dave next to Andrew and Erica; Erica next to Betty and Dave; Frank next to Andrew and Cara.
  const int allowed[6][2] = {{3, 5}, {2, 4}, {1, 5}, {0, 4}, {1, 3}, {0, 2}};

  // x[s] is the guest seated at seat s (seats are in order around the table)
  vec<IntVar*> x;
  createVars(x, guests, 0, guests - 1, true);

  // every guest has exactly one seat
  all_different(x);

  // two guests seated next to each other must be a pair that gets along
  vec<vec<int>> pairs;
  for (int g = 0; g < guests; ++g)
    for (int k = 0; k < 2; ++k) {
      pairs.push();
      pairs.last().push(g);
      pairs.last().push(allowed[g][k]);
    }
  for (int s = 0; s < guests; ++s) {
    vec<IntVar*> neighbours;
    neighbours.push(x[s]);
    neighbours.push(x[(s + 1) % guests]);
    table(neighbours, pairs);
  }

  branch(x, VAR_INORDER, VAL_MIN);
  json arr = json::array();
  for (int s = 0; s < guests; ++s) arr.push_back(dcp::out(x[s]));
  outputs = {{"x", arr}};
}
