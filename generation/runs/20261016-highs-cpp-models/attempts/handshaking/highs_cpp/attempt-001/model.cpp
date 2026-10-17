// Handshaking (Halmos). Hilary and Jocelyn are married and invite num_couples couples who
// are friends. Everyone shakes hands with others, never with self or with their spouse.
// Jocelyn then asks everyone except herself how many hands they shook; all answers differ.
// Output: the number of hands Hilary shook (hil).
#include "dcp.h"

// Persons: 0 = Hilary, 1 = Jocelyn, then the couples as (2 + 2k, 3 + 2k) for k = 0..n-1.
int spouse(int i) {
  if (i == 0) return 1;
  if (i == 1) return 0;
  return (i % 2 == 0) ? i + 1 : i - 1;
}

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int n = instance.at("num_couples").get<int>();
  const int people = 2 * n + 2;
  const int jocelyn = 1;

  // shake[i][j] = 1 when persons i and j shake hands; symmetric, zero on the diagonal and for spouses.
  std::vector<std::vector<dcp::Lin>> shake(people, std::vector<dcp::Lin>(people, dcp::Lin(0)));
  for (int i = 0; i < people; ++i)
    for (int j = i + 1; j < people; ++j) {
      // nobody shakes hands with his or her spouse
      if (spouse(i) == j) continue;
      shake[i][j] = dcp::new_var(h, 0, 1);
      shake[j][i] = shake[i][j];
    }

  // hands[i] = number of hands person i shook
  std::vector<dcp::Lin> hands(people, dcp::Lin(0));
  for (int i = 0; i < people; ++i)
    for (int j = 0; j < people; ++j) hands[i] = hands[i] + shake[i][j];

  // the most hands anyone can shake is everyone except self and spouse
  const int max_hands = people - 2;
  const double M = max_hands + 1;

  // all answers are different: every asked person (everyone except Jocelyn) differs from every other
  for (int i = 0; i < people; ++i) {
    if (i == jocelyn) continue;
    for (int j = i + 1; j < people; ++j) {
      if (j == jocelyn) continue;
      dcp::Lin differ = dcp::new_var(h, 0, 1);  // 0: hands[i] > hands[j]; 1: hands[j] > hands[i]
      // hands[i] - hands[j] >= 1 when differ = 0
      dcp::add_row(h, hands[i] - hands[j] + M * differ, 1, kHighsInf);
      // hands[j] - hands[i] >= 1 when differ = 1
      dcp::add_row(h, hands[j] - hands[i] - M * differ, 1 - M, kHighsInf);
    }
  }

  out.add("hil", hands[0]);
}
