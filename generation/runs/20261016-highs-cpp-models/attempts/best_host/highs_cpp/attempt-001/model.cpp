// Best host: seat six dinner guests around a round table with six seats, so that no
// two guests who do not get along sit next to each other. Output x lists the guests
// in seating order (0 Andrew, 1 Betty, 2 Cara, 3 Dave, 4 Erica, 5 Frank); seat 5 is
// next to seat 0.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;  // the statement fixes six guests and six seats; no instance field is read
  const int guests = 6;

  // ok[g][k] is true when guest g is allowed to sit next to guest k. These are the
  // "will only sit next to" lists of the statement, written out as a table.
  const bool ok[guests][guests] = {
      // Andrew will only sit next to Dave and Frank
      {false, false, false, true, false, true},
      // Betty will only sit next to Cara and Erica
      {false, false, true, false, true, false},
      // Cara will only sit next to Betty and Frank
      {false, true, false, false, false, true},
      // Dave will only sit next to Andrew and Erica
      {true, false, false, false, true, false},
      // Erica will only sit next to Betty and Dave
      {false, true, false, true, false, false},
      // Frank will only sit next to Andrew and Cara
      {true, false, true, false, false, false},
  };

  // y[p][g] = 1 when guest g sits in seat p
  dcp::Lin y[guests][guests];
  for (int p = 0; p < guests; ++p)
    for (int g = 0; g < guests; ++g) y[p][g] = dcp::new_var(h, 0, 1);

  // each seat holds exactly one guest
  for (int p = 0; p < guests; ++p) {
    dcp::Lin seat;
    for (int g = 0; g < guests; ++g) seat = seat + y[p][g];
    dcp::add_row(h, seat, 1, 1);
  }

  // each guest sits in exactly one seat
  for (int g = 0; g < guests; ++g) {
    dcp::Lin guest;
    for (int p = 0; p < guests; ++p) guest = guest + y[p][g];
    dcp::add_row(h, guest, 1, 1);
  }

  // guests in neighbouring seats (seat 5 is next to seat 0) must get along: a guest
  // in seat p and a guest in the next seat cannot be a pair that does not get along
  for (int p = 0; p < guests; ++p) {
    int q = (p + 1) % guests;
    for (int g = 0; g < guests; ++g)
      for (int k = 0; k < guests; ++k)
        if (g != k && !ok[g][k]) dcp::add_row(h, y[p][g] + y[q][k], -kHighsInf, 1);
  }

  // the guest in each seat, in seating order: x[p] = sum over g of g * y[p][g]
  std::vector<dcp::Lin> x(guests);
  for (int p = 0; p < guests; ++p)
    for (int g = 0; g < guests; ++g) x[p] = x[p] + static_cast<double>(g) * y[p][g];
  out.add("x", x);
}
