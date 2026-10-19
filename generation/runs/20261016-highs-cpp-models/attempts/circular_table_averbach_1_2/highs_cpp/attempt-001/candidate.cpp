// Circular table averbach 1_2: three players X, Y, Z of nationalities American, English and French
// sit around a circular table. Seat 1 is right of seat 0, seat 2 is right of seat 1, and seat 0 is
// right of seat 2. Each person passed three cards to the person on their right.
// Y passed three hearts to the American. X passed the queen of spades and two diamonds to the
// person who passed their cards to the Frenchwoman. Output the seats of X, Y, Z and of the
// American, English and French, where the same value matches a person with a nationality.
#include "dcp.h"

namespace {

// The seat on the right of seat s (seats 0, 1, 2 in a circle).
int right_of(int s) { return (s + 1) % 3; }

}  // namespace

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;  // the puzzle has no instance data
  using dcp::Lin;

  // pick[i][s] = 1 when label i sits in seat s. Labels: 0 X, 1 Y, 2 Z, 3 American, 4 English, 5 French.
  std::vector<std::vector<Lin>> pick(6, std::vector<Lin>(3));
  for (auto& line : pick)
    for (auto& seat : line) seat = dcp::new_var(h, 0, 1);

  // each label is in exactly one seat
  for (int i = 0; i < 6; ++i) {
    Lin one_seat;
    for (int s = 0; s < 3; ++s) one_seat = one_seat + pick[i][s];
    dcp::add_row(h, one_seat, 1, 1);
  }

  // X, Y and Z sit in different seats
  for (int s = 0; s < 3; ++s) {
    Lin used;
    for (int i = 0; i < 3; ++i) used = used + pick[i][s];
    dcp::add_row(h, used, 1, 1);
  }

  // the American, the English and the French sit in different seats
  for (int s = 0; s < 3; ++s) {
    Lin used;
    for (int i = 3; i < 6; ++i) used = used + pick[i][s];
    dcp::add_row(h, used, 1, 1);
  }

  // Y passed three hearts to the American: the American sits on the right of Y
  for (int s = 0; s < 3; ++s)
    dcp::add_row(h, pick[3][right_of(s)] - pick[1][s], 0, 0);

  // X passed the queen of spades and two diamonds to the person who passed to the Frenchwoman:
  // X's right-hand neighbour passed to the Frenchwoman, so the Frenchwoman sits two seats right of X
  for (int s = 0; s < 3; ++s)
    dcp::add_row(h, pick[5][right_of(right_of(s))] - pick[0][s], 0, 0);

  auto seat_of = [&](int label) {
    Lin seat;
    for (int s = 0; s < 3; ++s) seat = seat + static_cast<double>(s) * pick[label][s];
    return seat;
  };
  out.add("x", seat_of(0));
  out.add("y", seat_of(1));
  out.add("z", seat_of(2));
  out.add("american", seat_of(3));
  out.add("english", seat_of(4));
  out.add("french", seat_of(5));
}
