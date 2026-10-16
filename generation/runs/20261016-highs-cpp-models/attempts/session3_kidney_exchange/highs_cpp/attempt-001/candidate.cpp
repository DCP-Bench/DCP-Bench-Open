// Kidney exchange: n people on a waiting list. compatible[i] is the set of people that
// person i can donate a kidney to (1-based in the data). Anyone who gives a kidney must
// receive one, and no person receives more than one kidney. Maximise the number of people
// who receive a kidney. transplants[i][j] = 1 if person i donates to person j.
#include <set>

#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int n = instance.at("num_people").get<int>();
  const json& compatible = instance.at("compatible");

  // transplants[i][j] is a binary column for each compatible pair; every other pair is the constant 0
  std::vector<std::vector<dcp::Lin>> transplants(n, std::vector<dcp::Lin>(n, dcp::Lin(0)));
  std::vector<dcp::Lin> donates(n), receives(n);
  dcp::Lin total;

  for (int i = 0; i < n; ++i) {
    // the people that person i can donate to, without repeats or self-donation
    std::set<int> targets;
    for (const auto& j1 : compatible.at(i)) {
      int j = j1.get<int>() - 1;
      if (j != i) targets.insert(j);
    }
    for (int j : targets) {
      dcp::Lin x = dcp::new_var(h, 0, 1, true);
      transplants[i][j] = x;
      donates[i] = donates[i] + x;
      receives[j] = receives[j] + x;
      total = total + x;
    }
  }

  for (int i = 0; i < n; ++i) {
    // person i gives at most one kidney
    dcp::add_row(h, donates[i], -kHighsInf, 1);
  }
  for (int i = 0; i < n; ++i) {
    // person i receives at most one kidney
    dcp::add_row(h, receives[i], -kHighsInf, 1);
  }
  for (int i = 0; i < n; ++i) {
    // anyone who gives a kidney must receive one: the number given equals the number received
    dcp::add_row(h, donates[i] - receives[i], 0, 0);
  }

  // maximise the number of people who receive a kidney
  out.maximize(total);
  out.add("transplants", transplants);
}
