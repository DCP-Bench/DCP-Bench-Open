// Car selection: assign participants to cars, each participant to at most one car
// and each car to at most one participant, maximising the number of assignments.
// Only pairs the participant is interested in may be assigned.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const json& interest = instance.at("possible_assignments");
  int participants = static_cast<int>(interest.size());
  int cars = participants > 0 ? static_cast<int>(interest[0].size()) : 0;

  // assignments[i][j] = 1 if participant i is assigned to car j
  std::vector<std::vector<dcp::Lin>> assignments(participants, std::vector<dcp::Lin>(cars));
  for (int i = 0; i < participants; ++i) {
    for (int j = 0; j < cars; ++j) {
      // a participant not interested in a car cannot be assigned to it: upper bound 0
      int wanted = interest[i][j].get<int>();
      assignments[i][j] = dcp::new_var(h, 0, wanted != 0 ? 1 : 0);
    }
  }

  // each participant is assigned to at most one car
  for (int i = 0; i < participants; ++i) {
    dcp::Lin row;
    for (int j = 0; j < cars; ++j) row = row + assignments[i][j];
    dcp::add_row(h, row, -kHighsInf, 1);
  }

  // each car is assigned to at most one participant
  for (int j = 0; j < cars; ++j) {
    dcp::Lin column;
    for (int i = 0; i < participants; ++i) column = column + assignments[i][j];
    dcp::add_row(h, column, -kHighsInf, 1);
  }

  // the number of assignments made is maximised
  dcp::Lin total;
  for (int i = 0; i < participants; ++i)
    for (int j = 0; j < cars; ++j) total = total + assignments[i][j];
  out.maximize(total);

  out.add("assignments", assignments);
}
