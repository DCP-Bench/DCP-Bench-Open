// Wolf, goat and cabbage river crossing: a farmer ferries a wolf, a goat and a cabbage from the
// starting shore (0) to the destination shore (1) in stages. The boat carries the farmer and at
// most one item. If left unattended together, the wolf eats the goat, or the goat eats the cabbage.
// Output: at each stage, the shore (0 starting, 1 destination) of the wolf, goat, cabbage and boat.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  // the number of stages comes from the instance
  const int S = instance.at("stage").get<int>();

  // one shore variable per item and per stage: 0 starting shore, 1 destination shore
  std::vector<dcp::Lin> boat, wolf, goat, cabbage;
  for (int t = 0; t < S; ++t) {
    boat.push_back(dcp::new_var(h, 0, 1));
    wolf.push_back(dcp::new_var(h, 0, 1));
    goat.push_back(dcp::new_var(h, 0, 1));
    cabbage.push_back(dcp::new_var(h, 0, 1));
  }

  // all of the farmer, wolf, goat and cabbage start on the starting shore
  dcp::add_row(h, boat[0], 0, 0);
  dcp::add_row(h, wolf[0], 0, 0);
  dcp::add_row(h, goat[0], 0, 0);
  dcp::add_row(h, cabbage[0], 0, 0);

  // all of them are on the destination shore at the last stage
  dcp::add_row(h, boat[S - 1], 1, 1);
  dcp::add_row(h, wolf[S - 1], 1, 1);
  dcp::add_row(h, goat[S - 1], 1, 1);
  dcp::add_row(h, cabbage[S - 1], 1, 1);

  for (int t = 0; t + 1 < S; ++t) {
    // the boat crosses at every stage: the farmer changes shore
    dcp::add_row(h, boat[t] + boat[t + 1], 1, 1);

    // the boat carries the farmer and at most one item
    // move[k] = 1 when item k crosses at this stage (it changes shore)
    dcp::Lin move_wolf = dcp::new_var(h, 0, 1);
    dcp::Lin move_goat = dcp::new_var(h, 0, 1);
    dcp::Lin move_cabbage = dcp::new_var(h, 0, 1);
    // an item that changes shore must be on the farmer's shore when the boat leaves
    // (x changes => x = boat at the departure stage; move = 1 whenever x changes)
    dcp::Lin* moves[3] = {&move_wolf, &move_goat, &move_cabbage};
    dcp::Lin* items_now[3] = {&wolf[t], &goat[t], &cabbage[t]};
    dcp::Lin* items_next[3] = {&wolf[t + 1], &goat[t + 1], &cabbage[t + 1]};
    for (int k = 0; k < 3; ++k) {
      dcp::Lin& m = *moves[k];
      dcp::Lin& now = *items_now[k];
      dcp::Lin& next = *items_next[k];
      dcp::add_row(h, next - now - m, -kHighsInf, 0);
      dcp::add_row(h, now - next - m, -kHighsInf, 0);
      dcp::add_row(h, now - boat[t] + m, -kHighsInf, 1);
      dcp::add_row(h, boat[t] - now + m, -kHighsInf, 1);
    }
    // the farmer takes at most one item across
    dcp::add_row(h, move_wolf + move_goat + move_cabbage, -kHighsInf, 1);
  }

  for (int t = 0; t < S; ++t) {
    // the wolf may not be left with the goat without the farmer: wolf and goat on the same
    // shore need the farmer on that shore, so wolf + goat - farmer lies in 0..1
    dcp::add_row(h, wolf[t] + goat[t] - boat[t], 0, 1);
    // the goat may not be left with the cabbage without the farmer
    dcp::add_row(h, goat[t] + cabbage[t] - boat[t], 0, 1);
  }

  out.add("boat_pos", boat);
  out.add("wolf_pos", wolf);
  out.add("goat_pos", goat);
  out.add("cabbage_pos", cabbage);
}
