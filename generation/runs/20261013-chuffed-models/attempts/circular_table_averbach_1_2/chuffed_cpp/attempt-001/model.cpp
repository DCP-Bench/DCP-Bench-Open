// Circular table (Averbach 1.2): three people X, Y, Z of nationalities American, English, French
// sit around a round table playing Hearts and pass cards to the person on their right.
// Seats are 0, 1, 2 and seat 1 is right of 0, seat 2 right of 1, and so on (seat 0 is right of 2).
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // the seats of X, Y and Z (0, 1, 2)
  IntVar* x = newIntVar(0, 2);
  IntVar* y = newIntVar(0, 2);
  IntVar* z = newIntVar(0, 2);
  vec<IntVar*> seats;
  seats.push(x);
  seats.push(y);
  seats.push(z);
  // the three people sit in three different seats
  all_different(seats);

  // the nationality of each person, as the seat of the person who has it
  IntVar* american = newIntVar(0, 2);
  IntVar* english = newIntVar(0, 2);
  IntVar* french = newIntVar(0, 2);
  vec<IntVar*> nations;
  nations.push(american);
  nations.push(english);
  nations.push(french);
  // the three nationalities belong to three different people
  all_different(nations);

  // Y passed three hearts to the American, so the American sits right of Y: american = (y + 1) mod 3
  vec<int> right;
  right.push(1);
  right.push(2);
  right.push(0);
  array_int_element(y, right, american);

  // X passed the queen of spades and two diamonds to the person who passed to the Frenchwoman.
  // X's right neighbour q passed to the Frenchwoman, so the Frenchwoman sits right of q:
  // french = (x + 2) mod 3, which is the seat left of X
  vec<int> two_right;
  two_right.push(2);
  two_right.push(0);
  two_right.push(1);
  array_int_element(x, two_right, french);

  // the seats are the decision variables
  vec<IntVar*> search;
  search.push(x);
  search.push(y);
  search.push(z);
  branch(search, VAR_INORDER, VAL_MIN);

  outputs = {{"american", dcp::out(american)},
             {"english", dcp::out(english)},
             {"french", dcp::out(french)},
             {"x", dcp::out(x)},
             {"y", dcp::out(y)},
             {"z", dcp::out(z)}};
}
