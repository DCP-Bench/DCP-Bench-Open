// Five floors puzzle: Baker, Cooper, Fletcher, Miller and Smith live on the first five floors
// of an apartment house, one person per floor. Find the floor of each person (B, C, F, M, S).
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;  // the puzzle has no instance data
  const int floors = 5;
  const int people = 5;
  // People: 0 = Baker (B), 1 = Cooper (C), 2 = Fletcher (F), 3 = Miller (M), 4 = Smith (S).
  // Each person has one binary column per floor: y[p][f] = 1 when person p lives on floor f (f = 1..5).
  std::vector<std::vector<dcp::Lin>> y(people, std::vector<dcp::Lin>(floors + 1));
  for (int p = 0; p < people; ++p)
    for (int f = 1; f <= floors; ++f) y[p][f] = dcp::new_var(h, 0, 1);

  // Each person lives on exactly one floor.
  for (int p = 0; p < people; ++p) {
    dcp::Lin one;
    for (int f = 1; f <= floors; ++f) one = one + y[p][f];
    dcp::add_row(h, one, 1, 1);
  }
  // They all live on different floors: each floor holds exactly one person.
  for (int f = 1; f <= floors; ++f) {
    dcp::Lin one;
    for (int p = 0; p < people; ++p) one = one + y[p][f];
    dcp::add_row(h, one, 1, 1);
  }

  // The floor number of each person, as an integer from 1 to 5.
  std::vector<dcp::Lin> floor_of(people);
  for (int p = 0; p < people; ++p) {
    floor_of[p] = dcp::new_var(h, 1, floors);
    dcp::Lin weighted;
    for (int f = 1; f <= floors; ++f) weighted = weighted + double(f) * y[p][f];
    dcp::add_row(h, floor_of[p] - weighted, 0, 0);
  }
  const dcp::Lin& B = floor_of[0];
  const dcp::Lin& C = floor_of[1];
  const dcp::Lin& F = floor_of[2];
  const dcp::Lin& M = floor_of[3];
  const dcp::Lin& S = floor_of[4];

  // Baker does not live on the fifth floor.
  dcp::add_row(h, y[0][5], 0, 0);
  // Cooper does not live on the first floor.
  dcp::add_row(h, y[1][1], 0, 0);
  // Fletcher does not live on either the fifth or the first floor.
  dcp::add_row(h, y[2][5], 0, 0);
  dcp::add_row(h, y[2][1], 0, 0);
  // Miller lives on a higher floor than Cooper.
  dcp::add_row(h, M - C, 1, kHighsInf);

  // Smith does not live on a floor adjacent to Fletcher's, and Fletcher does not live on a floor
  // adjacent to Cooper's. Two floors are adjacent when they differ by 1. With all floors different,
  // "not adjacent" means the difference is at least 2 in one direction.
  // The binary s = 1 picks the direction a - b >= 2, s = 0 picks b - a >= 2.
  // The difference of two floors is at most floors - 1 in size, so M = floors + 1 is a valid big-M.
  const double bigM = floors + 1;
  auto not_adjacent = [&](const dcp::Lin& a, const dcp::Lin& b) {
    dcp::Lin s = dcp::new_var(h, 0, 1);
    dcp::add_row(h, a - b - bigM * s, 2 - bigM, kHighsInf);
    dcp::add_row(h, b - a + bigM * s, 2, kHighsInf);
  };
  // Smith not adjacent to Fletcher.
  not_adjacent(S, F);
  // Fletcher not adjacent to Cooper.
  not_adjacent(F, C);

  out.add("B", B);
  out.add("C", C);
  out.add("F", F);
  out.add("M", M);
  out.add("S", S);
}
