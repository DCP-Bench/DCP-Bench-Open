// Who killed Aunt Agatha? Three people live in Dreadsbury Mansion: Agatha herself, the
// butler and Charles. The killer is one of them, hates the victim, and is no richer than
// the victim. The output is the 0-based index of the killer (in the order of `names`).
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const auto& names = instance.at("names");
  const int n = static_cast<int>(names.size());

  // The three people are looked up by name in the instance, so the indices follow the data.
  auto index_of = [&](const std::string& who) {
    for (int i = 0; i < n; ++i)
      if (names[i].get<std::string>() == who) return i;
    throw std::runtime_error("no person named " + who);
  };
  const int agatha = index_of("Agatha herself");
  const int butler = index_of("the butler");
  const int charles = index_of("Charles");

  // Wealth ranks: any strict ordering of n people fits in the levels 0..n-1, so the
  // differences of two wealth values are at most n-1, which is the big-M for the richer rows.
  const double max_wealth = n - 1;
  std::vector<dcp::Lin> wealth(n);
  for (int i = 0; i < n; ++i) wealth[i] = dcp::new_var(h, 0, max_wealth);

  // richer[i][j] = 1 when person i is richer than person j (wealth[i] > wealth[j]).
  std::vector<std::vector<dcp::Lin>> richer(n, std::vector<dcp::Lin>(n));
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) richer[i][j] = dcp::new_var(h, 0, 1, true);
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) {
      // richer means wealth[i] - wealth[j] >= 1; otherwise wealth[i] - wealth[j] <= 0.
      // Same-person pairs (i == j) therefore can never be richer than themselves.
      dcp::add_row(h, wealth[i] - wealth[j] - max_wealth * richer[i][j], -kHighsInf, 0);
      dcp::add_row(h, wealth[i] - wealth[j] - max_wealth * richer[i][j], 1 - max_wealth, kHighsInf);
    }

  // hates[i][j] = 1 when person i hates person j.
  std::vector<std::vector<dcp::Lin>> hates(n, std::vector<dcp::Lin>(n));
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) hates[i][j] = dcp::new_var(h, 0, 1, true);

  // killed[i] = 1 when person i is the killer; exactly one killer.
  std::vector<dcp::Lin> killed(n);
  for (int i = 0; i < n; ++i) killed[i] = dcp::new_var(h, 0, 1, true);
  {
    dcp::Lin total;
    for (int i = 0; i < n; ++i) total = total + killed[i];
    dcp::add_row(h, total, 1, 1);  // exactly one killer
  }

  // A killer always hates the victim: killed[i] implies hates[i][agatha].
  for (int i = 0; i < n; ++i) dcp::add_row(h, killed[i] - hates[i][agatha], -kHighsInf, 0);

  // The killer is no richer than the victim: killed[i] implies not richer[i][agatha].
  for (int i = 0; i < n; ++i) dcp::add_row(h, killed[i] + richer[i][agatha], -kHighsInf, 1);

  // Agatha hates everybody except the butler (herself included).
  for (int j = 0; j < n; ++j) {
    if (j == butler) dcp::add_row(h, hates[agatha][j], 0, 0);
    else dcp::add_row(h, hates[agatha][j], 1, 1);
  }

  // Charles hates no one that Agatha hates: hates[agatha][j] implies not hates[charles][j].
  for (int j = 0; j < n; ++j) dcp::add_row(h, hates[charles][j] + hates[agatha][j], -kHighsInf, 1);

  // The butler hates everyone not richer than Aunt Agatha.
  for (int j = 0; j < n; ++j) dcp::add_row(h, hates[butler][j] + richer[j][agatha], 1, kHighsInf);

  // The butler hates everyone whom Agatha hates: hates[agatha][j] implies hates[butler][j].
  for (int j = 0; j < n; ++j) dcp::add_row(h, hates[butler][j] - hates[agatha][j], 0, kHighsInf);

  // No one hates everyone: each person misses at least one hatred.
  for (int i = 0; i < n; ++i) {
    dcp::Lin count;
    for (int j = 0; j < n; ++j) count = count + hates[i][j];
    dcp::add_row(h, count, -kHighsInf, n - 1);
  }

  // Output: the killer's index.
  dcp::Lin killer;
  for (int i = 0; i < n; ++i) killer = killer + static_cast<double>(i) * killed[i];
  out.add("killer", killer);
}
