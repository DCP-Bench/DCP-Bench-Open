// Initials queue: ten people in a queue, each with initials that are an alphabetically
// ordered pair of distinct letters from A to E (0 to 4). No two people share initials,
// and no person shares a letter with the person in front of them. BE is at the front,
// CD is right behind, and BD is at the end of the queue. Output queue[i] = [first, second]
// letter of the person at position i, counting from the front.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int letters = 5;
  const int people = 10;

  // All alphabetically ordered pairs (a, b), a < b, of the letters 0 to 4.
  std::vector<std::pair<int, int>> pairs;
  for (int a = 0; a < letters; ++a)
    for (int b = a + 1; b < letters; ++b) pairs.push_back({a, b});
  const int np = static_cast<int>(pairs.size());

  auto pair_index = [&](int a, int b) {
    for (int p = 0; p < np; ++p)
      if (pairs[p].first == a && pairs[p].second == b) return p;
    throw std::logic_error("no such pair");
  };

  // y[i][p] is 1 when the person at position i has the pair p.
  std::vector<std::vector<dcp::Lin>> y(people, std::vector<dcp::Lin>(np));
  for (int i = 0; i < people; ++i)
    for (int p = 0; p < np; ++p) y[i][p] = dcp::new_var(h, 0, 1);

  // each person has exactly one pair of initials
  for (int i = 0; i < people; ++i) {
    dcp::Lin s;
    for (int p = 0; p < np; ++p) s = s + y[i][p];
    dcp::add_row(h, s, 1, 1);
  }

  // no two people have the same initials
  for (int p = 0; p < np; ++p) {
    dcp::Lin s;
    for (int i = 0; i < people; ++i) s = s + y[i][p];
    dcp::add_row(h, s, -kHighsInf, 1);
  }

  // no one shares a letter with the person in front of them:
  // for each letter, the two neighbours cannot both carry it
  for (int i = 0; i + 1 < people; ++i) {
    for (int L = 0; L < letters; ++L) {
      dcp::Lin s;
      for (int p = 0; p < np; ++p) {
        if (pairs[p].first == L || pairs[p].second == L) s = s + y[i][p] + y[i + 1][p];
      }
      dcp::add_row(h, s, -kHighsInf, 1);
    }
  }

  // BE is at the front of the queue
  dcp::add_row(h, y[0][pair_index(1, 4)], 1, 1);
  // CD is right behind BE
  dcp::add_row(h, y[1][pair_index(2, 3)], 1, 1);
  // BD is right at the end of the queue
  dcp::add_row(h, y[people - 1][pair_index(1, 3)], 1, 1);

  // the queue: first and second letter of each person, from the front
  std::vector<std::vector<dcp::Lin>> queue(people, std::vector<dcp::Lin>(2));
  for (int i = 0; i < people; ++i) {
    dcp::Lin first;
    dcp::Lin second;
    for (int p = 0; p < np; ++p) {
      first = first + static_cast<double>(pairs[p].first) * y[i][p];
      second = second + static_cast<double>(pairs[p].second) * y[i][p];
    }
    queue[i][0] = first;
    queue[i][1] = second;
  }
  out.add("queue", queue);
}
