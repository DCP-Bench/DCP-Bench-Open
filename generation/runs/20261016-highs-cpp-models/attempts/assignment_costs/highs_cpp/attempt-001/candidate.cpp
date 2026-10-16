#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const json& cost = instance.at("cost");
  const int tasks = static_cast<int>(cost.size());
  const int people = static_cast<int>(cost[0].size());

  // x[i][j] = 1 when task i is assigned to person j.
  std::vector<std::vector<dcp::Lin>> x(tasks, std::vector<dcp::Lin>(people));
  for (int i = 0; i < tasks; ++i)
    for (int j = 0; j < people; ++j) x[i][j] = dcp::new_var(h, 0, 1);

  // Each task is assigned to exactly one person.
  for (int i = 0; i < tasks; ++i) {
    dcp::Lin row;
    for (int j = 0; j < people; ++j) row = row + x[i][j];
    dcp::add_row(h, row, 1, 1);
  }

  // Each person takes at most one task; not every person needs a task.
  for (int j = 0; j < people; ++j) {
    dcp::Lin col;
    for (int i = 0; i < tasks; ++i) col = col + x[i][j];
    dcp::add_row(h, col, -kHighsInf, 1);
  }

  // The total cost of the chosen assignments is minimised.
  dcp::Lin total;
  for (int i = 0; i < tasks; ++i)
    for (int j = 0; j < people; ++j)
      total = total + static_cast<double>(cost[i][j].get<int>()) * x[i][j];
  out.minimize(total);

  out.add("x", x);
}
