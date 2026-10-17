// Graph colouring of six countries (Belgium, Denmark, France, Germany, Netherlands,
// Luxembourg). Two neighbouring countries cannot have the same colour. Colours are
// integers starting from 1. Minimise the number of colours used.
// The instance gives the neighbour pairs as 1-based country numbers in "graph".
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int countries = 6;
  const int colours = countries;  // at most one colour per country

  // y[i][k] = 1 when country i has colour k+1
  std::vector<std::vector<dcp::Lin>> y(countries, std::vector<dcp::Lin>(colours));
  for (int i = 0; i < countries; ++i)
    for (int k = 0; k < colours; ++k) y[i][k] = dcp::new_var(h, 0, 1);

  // each country has exactly one colour
  for (int i = 0; i < countries; ++i) {
    dcp::Lin one_colour = 0;
    for (int k = 0; k < colours; ++k) one_colour = one_colour + y[i][k];
    dcp::add_row(h, one_colour, 1, 1);
  }

  // colour of country i, numbered from 1
  std::vector<dcp::Lin> colour(countries);
  for (int i = 0; i < countries; ++i) {
    dcp::Lin c = 0;
    for (int k = 0; k < colours; ++k) c = c + (k + 1) * y[i][k];
    colour[i] = c;
  }

  // the objective variable is at least every colour in use
  dcp::Lin used = dcp::new_var(h, 1, colours);
  for (int i = 0; i < countries; ++i) dcp::add_row(h, used - colour[i], 0, kHighsInf);

  // neighbouring countries have different colours: they never share a colour k
  const auto& graph = instance.at("graph");
  for (const auto& edge : graph) {
    int a = edge[0].get<int>() - 1;  // 1-based in the data
    int b = edge[1].get<int>() - 1;
    // a and b are different countries: for each colour, not both take it
    for (int k = 0; k < colours; ++k) dcp::add_row(h, y[a][k] + y[b][k], -kHighsInf, 1);
  }

  out.minimize(used);

  std::vector<dcp::Lin> result(colour.begin(), colour.end());
  out.add("colors", result);
}
