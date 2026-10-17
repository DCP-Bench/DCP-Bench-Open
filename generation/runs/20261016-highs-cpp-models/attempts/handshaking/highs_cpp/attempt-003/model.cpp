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
  const int max_hands = people - 2;  // everyone except self and spouse

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

  // the asked people (everyone except Jocelyn) answer with distinct numbers in 0..max_hands;
  // there are exactly max_hands + 1 of them, so every number is used once.
  // taken[p][v] = 1 when asked person p shook exactly v hands
  std::vector<std::vector<dcp::Lin>> taken(people, std::vector<dcp::Lin>(max_hands + 1, dcp::Lin(0)));
  for (int p = 0; p < people; ++p) {
    if (p == jocelyn) continue;
    for (int v = 0; v <= max_hands; ++v) taken[p][v] = dcp::new_var(h, 0, 1);
  }

  // each asked person has exactly one number of hands, and it is the number of hands shaken
  for (int p = 0; p < people; ++p) {
    if (p == jocelyn) continue;
    dcp::Lin one_answer = 0;
    dcp::Lin answer = 0;
    for (int v = 0; v <= max_hands; ++v) {
      one_answer = one_answer + taken[p][v];
      answer = answer + v * taken[p][v];
    }
    dcp::add_row(h, one_answer, 1, 1);
    dcp::add_row(h, hands[p] - answer, 0, 0);
  }

  // each number is the answer of exactly one asked person
  for (int v = 0; v <= max_hands; ++v) {
    dcp::Lin count = 0;
    for (int p = 0; p < people; ++p)
      if (p != jocelyn) count = count + taken[p][v];
    dcp::add_row(h, count, 1, 1);
  }

  out.add("hil", hands[0]);
}
