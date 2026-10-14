// Map colouring: colour the six countries Belgium, Denmark, France, Germany, Netherlands and
// Luxembourg (nodes 1 to 6 in the graph) so that neighbouring countries get different colours,
// using as few colours as possible. Colours are the integers 1 to 6.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<std::vector<int>> edges = instance.at("graph").get<std::vector<std::vector<int>>>();

  // colors[k] is the colour of country k+1 (six countries, the problem's own count)
  vec<IntVar*> colors;
  createVars(colors, 6, 1, 6);

  // neighbouring countries (each edge of the graph, numbered from 1) have different colours
  for (size_t e = 0; e < edges.size(); ++e) {
    int_rel(colors[edges[e][0] - 1], IRT_NE, colors[edges[e][1] - 1]);
  }

  // the number of colours used is the largest colour, which is minimised
  IntVar* used = newIntVar(1, 6);
  maximum(colors, used);

  // the colours are the decision variables
  branch(colors, VAR_INORDER, VAL_MIN);

  // minimise the number of colours used
  optimize(used, OPT_MIN);

  json out_colors = json::array();
  for (int k = 0; k < 6; ++k) out_colors.push_back(dcp::out(colors[k]));
  outputs = {{"colors", out_colors}};
}
