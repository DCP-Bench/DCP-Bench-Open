// Farmer and cows: cows numbered 1..num_cows, cow i gives i units of milk. The farmer has
// num_sons sons and gives each son a fixed number of cows (cows_per_son). Every son must
// get the same total milk. Output cow_assignments[i] is the son (0-based) that cow i+1 goes to.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("num_cows").get<int>();
  int s = instance.at("num_sons").get<int>();
  std::vector<int> per_son = instance.at("cows_per_son").get<std::vector<int>>();

  // x[i][j] is 1 when cow i goes to son j
  std::vector<std::vector<dcp::Lin>> x(n, std::vector<dcp::Lin>(s));
  for (int i = 0; i < n; i++)
    for (int j = 0; j < s; j++)
      x[i][j] = dcp::new_var(h, 0, 1);

  // each cow goes to exactly one son
  for (int i = 0; i < n; i++) {
    dcp::Lin e;
    for (int j = 0; j < s; j++) e = e + x[i][j];
    dcp::add_row(h, e, 1, 1);
  }

  // each son gets the number of cows given in the distribution
  for (int j = 0; j < s; j++) {
    dcp::Lin e;
    for (int i = 0; i < n; i++) e = e + x[i][j];
    dcp::add_row(h, e, per_son[j], per_son[j]);
  }

  // every son gets the same total milk as son 0
  for (int j = 1; j < s; j++) {
    dcp::Lin e;
    for (int i = 0; i < n; i++)
      e = e + (double(i + 1)) * x[i][j] - (double(i + 1)) * x[i][0];
    dcp::add_row(h, e, 0, 0);
  }

  // the son of each cow is the sum of j * x[i][j], which is j for the one son the cow goes to
  std::vector<dcp::Lin> assignment(n);
  for (int i = 0; i < n; i++)
    for (int j = 0; j < s; j++)
      assignment[i] = assignment[i] + (double(j)) * x[i][j];
  out.add("cow_assignments", assignment);
}
