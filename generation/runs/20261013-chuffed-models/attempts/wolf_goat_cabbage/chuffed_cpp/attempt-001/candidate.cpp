// A farmer ferries a wolf, a goat and a cabbage across a river in a boat that carries the farmer and at most one item.
// Stage t is the state after t crossings; shore 0 is the starting shore and shore 1 the destination.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // the number of stages comes from the instance; the farmer crosses once between consecutive stages
  int stages = instance.at("stage");

  // position of each party at each stage (0 = starting shore, 1 = destination shore)
  vec<IntVar*> wolf, goat, cabbage, boat;
  createVars(wolf, stages, 0, 1, true);
  createVars(goat, stages, 0, 1, true);
  createVars(cabbage, stages, 0, 1, true);
  createVars(boat, stages, 0, 1, true);

  // everything starts on the starting shore
  int_rel(wolf[0], IRT_EQ, 0);
  int_rel(goat[0], IRT_EQ, 0);
  int_rel(cabbage[0], IRT_EQ, 0);
  int_rel(boat[0], IRT_EQ, 0);

  // everything ends on the destination shore
  int_rel(wolf[stages - 1], IRT_EQ, 1);
  int_rel(goat[stages - 1], IRT_EQ, 1);
  int_rel(cabbage[stages - 1], IRT_EQ, 1);
  int_rel(boat[stages - 1], IRT_EQ, 1);

  for (int t = 0; t < stages; ++t) {
    // the wolf would eat the goat, or the goat the cabbage, if the farmer is not with them
    BoolView wolf_apart = newBoolVar();
    int_rel_reif(wolf[t], IRT_NE, goat[t], wolf_apart);
    BoolView farmer_with_goat = newBoolVar();
    int_rel_reif(boat[t], IRT_EQ, goat[t], farmer_with_goat);
    vec<BoolView> safe_wg;
    safe_wg.push(wolf_apart);
    safe_wg.push(farmer_with_goat);
    bool_clause(safe_wg);

    BoolView goat_apart = newBoolVar();
    int_rel_reif(goat[t], IRT_NE, cabbage[t], goat_apart);
    BoolView farmer_with_cabbage = newBoolVar();
    int_rel_reif(boat[t], IRT_EQ, cabbage[t], farmer_with_cabbage);
    vec<BoolView> safe_gc;
    safe_gc.push(goat_apart);
    safe_gc.push(farmer_with_cabbage);
    bool_clause(safe_gc);
  }

  for (int t = 0; t + 1 < stages; ++t) {
    // the farmer rows the boat across at every crossing: the boat changes shore
    vec<int> two;
    two.push(1); two.push(1);
    vec<IntVar*> pair;
    pair.push(boat[t]); pair.push(boat[t + 1]);
    int_linear(two, pair, IRT_EQ, 1);

    // the boat carries at most one item: count the items that change shore
    BoolView wolf_same = newBoolVar();
    int_rel_reif(wolf[t], IRT_EQ, wolf[t + 1], wolf_same);
    BoolView goat_same = newBoolVar();
    int_rel_reif(goat[t], IRT_EQ, goat[t + 1], goat_same);
    BoolView cabbage_same = newBoolVar();
    int_rel_reif(cabbage[t], IRT_EQ, cabbage[t + 1], cabbage_same);
    BoolView wolf_moves = ~wolf_same;
    BoolView goat_moves = ~goat_same;
    BoolView cabbage_moves = ~cabbage_same;
    vec<BoolView> moved;
    moved.push(wolf_moves);
    moved.push(goat_moves);
    moved.push(cabbage_moves);
    IntVar* one = getConstant(1);
    bool_linear(moved, IRT_LE, one);

    // an item can only cross in the boat, so it must be on the farmer's shore before the crossing
    BoolView wolf_with_farmer = newBoolVar();
    int_rel_reif(wolf[t], IRT_EQ, boat[t], wolf_with_farmer);
    vec<BoolView> wolf_ok;
    wolf_ok.push(wolf_same);
    wolf_ok.push(wolf_with_farmer);
    bool_clause(wolf_ok);

    BoolView goat_with_farmer = newBoolVar();
    int_rel_reif(goat[t], IRT_EQ, boat[t], goat_with_farmer);
    vec<BoolView> goat_ok;
    goat_ok.push(goat_same);
    goat_ok.push(goat_with_farmer);
    bool_clause(goat_ok);

    BoolView cabbage_with_farmer = newBoolVar();
    int_rel_reif(cabbage[t], IRT_EQ, boat[t], cabbage_with_farmer);
    vec<BoolView> cabbage_ok;
    cabbage_ok.push(cabbage_same);
    cabbage_ok.push(cabbage_with_farmer);
    bool_clause(cabbage_ok);
  }

  // the positions are the decision variables, stage by stage
  vec<IntVar*> all;
  for (int t = 0; t < stages; ++t) {
    all.push(wolf[t]); all.push(goat[t]); all.push(cabbage[t]); all.push(boat[t]);
  }
  branch(all, VAR_INORDER, VAL_MIN);

  json wolf_out = json::array(), goat_out = json::array(), cabbage_out = json::array(), boat_out = json::array();
  for (int t = 0; t < stages; ++t) {
    wolf_out.push_back(dcp::out(wolf[t]));
    goat_out.push_back(dcp::out(goat[t]));
    cabbage_out.push_back(dcp::out(cabbage[t]));
    boat_out.push_back(dcp::out(boat[t]));
  }
  outputs = {{"wolf_pos", wolf_out}, {"goat_pos", goat_out}, {"cabbage_pos", cabbage_out}, {"boat_pos", boat_out}};
}
