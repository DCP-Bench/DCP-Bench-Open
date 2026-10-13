// Rehearsal: order the pieces of a concert so that the total time players spend present but not
// playing is minimal; a player arrives just before their first piece and leaves just after their last.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("num_pieces");
  int num_players = instance.at("num_players");
  std::vector<int> duration = instance.at("duration").get<std::vector<int>>();
  std::vector<std::vector<int>> rehearsal = instance.at("rehearsal").get<std::vector<std::vector<int>>>();
  int total_duration = 0;
  for (int d : duration) total_duration += d;

  // rehearsal_order[s] = piece rehearsed in slot s; slot[p] = slot in which piece p is rehearsed
  vec<IntVar*> rehearsal_order, slot;
  createVars(rehearsal_order, n, 0, n - 1);
  createVars(slot, n, 0, n - 1);
  // every piece is rehearsed exactly once
  all_different(rehearsal_order);
  inverse(slot, rehearsal_order);

  // before[q][p] = 1 if piece q is rehearsed before piece p
  // start[p] = start time of piece p = total duration of the pieces rehearsed before it
  vec<IntVar*> start, finish;
  for (int p = 0; p < n; ++p) {
    vec<int> coef;
    vec<IntVar*> terms;
    for (int q = 0; q < n; ++q) {
      if (q == p) continue;
      BoolView b = newBoolVar();
      int_rel_reif(slot[q], IRT_LT, slot[p], b);
      IntVar* bi = newIntVar(0, 1);
      bool2int(b, bi);
      coef.push(duration[q]);
      terms.push(bi);
    }
    IntVar* s = newIntVar(0, total_duration);
    int_linear(coef, terms, IRT_EQ, s);
    start.push(s);
    IntVar* f = newIntVar(0, total_duration);
    int_rel(f, IRT_EQ, s, duration[p]);
    finish.push(f);
  }

  // a player is present from the start of their first piece to the end of their last piece;
  // the waiting time is the time present minus the time spent playing
  vec<IntVar*> present;
  int playing = 0;
  for (int k = 0; k < num_players; ++k) {
    vec<IntVar*> starts, finishes;
    for (int p = 0; p < n; ++p) {
      if (rehearsal[k][p]) {
        starts.push(start[p]);
        finishes.push(finish[p]);
        playing += duration[p];
      }
    }
    if (starts.size() == 0) continue;
    IntVar* arrive = newIntVar(0, total_duration);
    IntVar* leave = newIntVar(0, total_duration);
    minimum(starts, arrive);
    maximum(finishes, leave);
    IntVar* stay = newIntVar(0, total_duration);
    int_minus(leave, arrive, stay);
    present.push(stay);
  }
  // total waiting time of all players
  IntVar* time_present = newIntVar(0, total_duration * num_players);
  int_linear(present, IRT_EQ, time_present);
  IntVar* waiting = newIntVar(0, total_duration * num_players);
  int_rel(time_present, IRT_EQ, waiting, playing);  // time present = waiting + time playing

  // minimize the total waiting time
  branch(rehearsal_order, VAR_INORDER, VAL_MIN);
  optimize(waiting, OPT_MIN);

  json order = json::array();
  for (int s = 0; s < n; ++s) order.push_back(dcp::out(rehearsal_order[s]));
  outputs = {{"rehearsal_order", order}};
}
