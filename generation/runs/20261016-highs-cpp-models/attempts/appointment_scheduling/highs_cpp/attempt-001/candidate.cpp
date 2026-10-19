#include "dcp.h"

// Schedule every person into one interview slot, based on the free-busy matrix m.
// m[i][j] = 1 means person i is free in slot j; 0 means busy.
void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const auto& m = instance.at("m");
  const int people = static_cast<int>(m.size());
  const int slots = people == 0 ? 0 : static_cast<int>(m[0].size());

  // x[i][j] = 1 when person i is assigned to slot j; it may be 1 only where person i is free.
  std::vector<std::vector<dcp::Lin>> x(people, std::vector<dcp::Lin>(slots));
  for (int i = 0; i < people; ++i)
    for (int j = 0; j < slots; ++j)
      x[i][j] = dcp::new_var(h, 0, m[i][j].get<int>());

  // every person is assigned exactly one slot
  for (int i = 0; i < people; ++i) {
    dcp::Lin total = 0;
    for (int j = 0; j < slots; ++j) total = total + x[i][j];
    dcp::add_row(h, total, 1, 1);
  }

  // every slot holds at most one person
  for (int j = 0; j < slots; ++j) {
    dcp::Lin total = 0;
    for (int i = 0; i < people; ++i) total = total + x[i][j];
    dcp::add_row(h, total, -kHighsInf, 1);
  }

  out.add("x", x);
}
