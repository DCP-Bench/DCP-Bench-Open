#include <algorithm>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Rehearsal problem: find an order in which to rehearse the pieces of a concert
// so that the total time players spend waiting is minimal.  A player arrives
// just before the first piece they play in and leaves just after the last one;
// the time they are present but not playing is waiting time.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int num_pieces = instance.at("num_pieces").get<int>();
  const int num_players = instance.at("num_players").get<int>();
  const std::vector<int64_t> duration =
      instance.at("duration").get<std::vector<int64_t>>();
  // rehearsal[p][pc] is 1 when player p takes part in piece pc.
  const std::vector<std::vector<int64_t>> rehearsal =
      instance.at("rehearsal").get<std::vector<std::vector<int64_t>>>();

  // rehearsal_order[i] is the piece rehearsed in slot i.
  // in_slot[i][pc] is true exactly when slot i holds piece pc; the permutation
  // matrix form of rehearsal_order, which makes the durations and the
  // "player plays in this slot" tests linear.
  std::vector<IntVar> rehearsal_order;
  std::vector<std::vector<BoolVar>> in_slot(num_pieces);
  for (int i = 0; i < num_pieces; ++i) {
    rehearsal_order.push_back(model.NewIntVar(Domain(0, num_pieces - 1)));
    LinearExpr one_piece;
    LinearExpr piece_index;
    for (int pc = 0; pc < num_pieces; ++pc) {
      in_slot[i].push_back(model.NewBoolVar());
      one_piece += in_slot[i][pc];
      piece_index += pc * in_slot[i][pc];
    }
    model.AddEquality(one_piece, 1);
    model.AddEquality(rehearsal_order[i], piece_index);
  }

  // Each piece is rehearsed exactly once, so the order is a permutation.
  for (int pc = 0; pc < num_pieces; ++pc) {
    LinearExpr slots_of_piece;
    for (int i = 0; i < num_pieces; ++i) slots_of_piece += in_slot[i][pc];
    model.AddEquality(slots_of_piece, 1);
  }

  // arrival[p] and departure[p] are the first and last slots in which player p
  // is present.
  std::vector<IntVar> arrival, departure;
  for (int p = 0; p < num_players; ++p) {
    arrival.push_back(model.NewIntVar(Domain(0, num_pieces - 1)));
    departure.push_back(model.NewIntVar(Domain(0, num_pieces - 1)));
  }

  // duration_in_slot[i]: how long the piece rehearsed in slot i lasts.
  const int64_t longest = *std::max_element(duration.begin(), duration.end());
  std::vector<IntVar> duration_in_slot;
  for (int i = 0; i < num_pieces; ++i) {
    LinearExpr d;
    for (int pc = 0; pc < num_pieces; ++pc) d += duration[pc] * in_slot[i][pc];
    duration_in_slot.push_back(model.NewIntVar(Domain(0, longest)));
    model.AddEquality(duration_in_slot[i], d);
  }

  LinearExpr total_waiting;
  for (int p = 0; p < num_players; ++p) {
    for (int i = 0; i < num_pieces; ++i) {
      // plays: player p plays in the piece rehearsed in slot i.
      BoolVar plays = model.NewBoolVar();
      LinearExpr plays_value;
      for (int pc = 0; pc < num_pieces; ++pc) {
        if (rehearsal[p][pc] == 1) plays_value += in_slot[i][pc];
      }
      model.AddEquality(plays, plays_value);

      // started: slot i is not before the arrival of p.
      // not_ended: slot i is not after the departure of p.
      BoolVar started = model.NewBoolVar();
      model.AddLessOrEqual(arrival[p], i).OnlyEnforceIf(started);
      model.AddGreaterOrEqual(arrival[p], i + 1).OnlyEnforceIf(started.Not());
      BoolVar not_ended = model.NewBoolVar();
      model.AddGreaterOrEqual(departure[p], i).OnlyEnforceIf(not_ended);
      model.AddLessOrEqual(departure[p], i - 1).OnlyEnforceIf(not_ended.Not());

      // A player must be present for every piece they play in.
      model.AddImplication(plays, started);
      model.AddImplication(plays, not_ended);

      // present: p is in the room during slot i.
      BoolVar present = model.NewBoolVar();
      model.AddBoolAnd({started, not_ended}).OnlyEnforceIf(present);
      model.AddBoolOr({started.Not(), not_ended.Not(), present});

      // waiting: p is present in slot i but not playing in it.
      BoolVar waiting = model.NewBoolVar();
      model.AddBoolAnd({present, plays.Not()}).OnlyEnforceIf(waiting);
      model.AddBoolOr({present.Not(), plays, waiting});

      // A waiting player adds the duration of the piece in that slot.
      IntVar wait_time = model.NewIntVar(Domain(0, longest));
      model.AddEquality(wait_time, duration_in_slot[i]).OnlyEnforceIf(waiting);
      model.AddEquality(wait_time, 0).OnlyEnforceIf(waiting.Not());
      total_waiting += wait_time;
    }
  }

  // Minimise the total time players spend waiting.
  model.Minimize(total_waiting);

  json order_out = json::array();
  for (const IntVar& v : rehearsal_order) order_out.push_back(v.index());
  outputs = {{"rehearsal_order", order_out}};
}
