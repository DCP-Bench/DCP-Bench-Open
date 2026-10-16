// Finding celebrities at a party. Given a list of people at a party and for each person the
// list of people they know at the party, find the celebrities. A celebrity is a person that
// everybody at the party knows but that only knows other celebrities. At least one celebrity
// is present at the party. Output celebrities[i] is 1 when person i is a celebrity, 0 otherwise.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const json& graph = instance.at("graph");  // graph[i][j] = 1 when person i knows person j
  int n = graph.size();

  // one binary column per person: 1 when the person is a celebrity
  std::vector<dcp::Lin> celebrity;
  for (int i = 0; i < n; ++i) celebrity.push_back(dcp::new_var(h, 0, 1));

  // everybody at the party knows a celebrity: a person who is not known by some other person
  // at the party cannot be a celebrity
  for (int j = 0; j < n; ++j) {
    bool known_by_all = true;
    for (int i = 0; i < n; ++i)
      if (i != j && graph[i][j].get<int>() == 0) known_by_all = false;
    if (!known_by_all) dcp::add_row(h, celebrity[j], -kHighsInf, 0);
  }

  // a celebrity only knows other celebrities: when person i knows person j, celebrity i
  // implies celebrity j
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j)
      if (i != j && graph[i][j].get<int>() == 1)
        dcp::add_row(h, celebrity[j] - celebrity[i], 0, kHighsInf);

  // at least one celebrity is present at the party
  dcp::Lin count;
  for (int i = 0; i < n; ++i) count = count + celebrity[i];
  dcp::add_row(h, count, 1, kHighsInf);

  out.add("celebrities", celebrity);
}
