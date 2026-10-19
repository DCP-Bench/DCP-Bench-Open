// session3_people_in_a_room: 13 people, 4 of them male, enter a room one at a time.
// Find an order of entry (sequence, 0 = male, 1 = female) so that the ratio of
// females to males in the room at any one time is no greater than 7/3.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int people = 13;
  const int males = 4;
  const int females = people - males;

  // x[i] = 1 when the i-th person to enter (0-based position) is female.
  std::vector<dcp::Lin> x;
  for (int i = 0; i < people; ++i) x.push_back(dcp::new_var(h, 0, 1));

  // There are 4 males and 9 females in total: exactly 9 entries are female.
  {
    dcp::Lin total;
    for (int i = 0; i < people; ++i) total = total + x[i];
    dcp::add_row(h, total, females, females);
  }

  // At any time t (after t people have entered) the females F_t and males M_t = t - F_t
  // in the room satisfy F_t / M_t <= 7/3, written without division as 3 F_t <= 7 M_t.
  // Substituting M_t = t - F_t gives 10 F_t <= 7 t.
  for (int t = 1; t <= people; ++t) {
    // the females among the first t entries, at most 7/3 of the males among them
    dcp::Lin in_room_females;
    for (int i = 0; i < t; ++i) in_room_females = in_room_females + x[i];
    dcp::add_row(h, 10.0 * in_room_females, -kHighsInf, 7.0 * t);
  }

  out.add("sequence", x);
}
