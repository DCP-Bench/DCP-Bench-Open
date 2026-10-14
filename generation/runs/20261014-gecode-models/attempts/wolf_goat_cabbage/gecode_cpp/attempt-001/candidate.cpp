#include "dcp.h"

// Wolf, goat and cabbage: a farmer must ferry a wolf, a goat and a cabbage across a
// river one at a time, without the wolf eating the goat or the goat eating the cabbage.
// Positions are stages 0..n-1 (n = stage count from the instance); 0 = starting shore,
// 1 = destination shore. Everything starts on shore 0 and ends on shore 1.
class WolfGoatCabbage : public dcp::Space {
 protected:
  IntVarArray wolf;     // wolf[t]: wolf on the destination shore at stage t
  IntVarArray goat;     // goat[t]: goat on the destination shore at stage t
  IntVarArray cabbage;  // cabbage[t]: cabbage on the destination shore at stage t
  IntVarArray boat;     // boat[t]: farmer's boat on the destination shore at stage t

 public:
  explicit WolfGoatCabbage(const json& instance) {
    int n = instance.at("stage").get<int>();
    wolf = IntVarArray(*this, n, 0, 1);
    goat = IntVarArray(*this, n, 0, 1);
    cabbage = IntVarArray(*this, n, 0, 1);
    boat = IntVarArray(*this, n, 0, 1);

    // everything starts on the starting shore
    rel(*this, wolf[0], IRT_EQ, 0);
    rel(*this, goat[0], IRT_EQ, 0);
    rel(*this, cabbage[0], IRT_EQ, 0);
    rel(*this, boat[0], IRT_EQ, 0);

    // everything ends on the destination shore
    rel(*this, wolf[n - 1], IRT_EQ, 1);
    rel(*this, goat[n - 1], IRT_EQ, 1);
    rel(*this, cabbage[n - 1], IRT_EQ, 1);
    rel(*this, boat[n - 1], IRT_EQ, 1);

    IntVarArray* items[3] = {&wolf, &goat, &cabbage};  // the three items, in the description's order

    for (int t = 0; t + 1 < n; ++t) {
      // the farmer crosses the river at every stage (the boat alternates shores)
      rel(*this, boat[t] != boat[t + 1]);

      // at most one item crosses per stage: the boat carries the farmer and a single item
      BoolVarArgs moved;
      for (int k = 0; k < 3; ++k) {
        BoolVar m(*this, 0, 1);
        rel(*this, (*items[k])[t], IRT_NQ, (*items[k])[t + 1], m);
        moved << m;
        // an item can only cross on the boat, so it must be on the farmer's shore
        rel(*this, (*items[k])[t], IRT_EQ, boat[t], imp(m));
      }
      linear(*this, moved, IRT_LQ, 1);
    }

    for (int t = 0; t < n; ++t) {
      // the wolf would eat the goat if left unattended: they may share a shore only with the farmer
      BoolVar wolf_with_goat(*this, 0, 1);
      rel(*this, wolf[t], IRT_EQ, goat[t], wolf_with_goat);
      rel(*this, wolf[t], IRT_EQ, boat[t], imp(wolf_with_goat));

      // the goat would eat the cabbage if left unattended: same rule for goat and cabbage
      BoolVar goat_with_cabbage(*this, 0, 1);
      rel(*this, goat[t], IRT_EQ, cabbage[t], goat_with_cabbage);
      rel(*this, goat[t], IRT_EQ, boat[t], imp(goat_with_cabbage));
    }

    // decisions: the item positions in stage order, then the boat
    branch(*this, wolf, INT_VAR_NONE(), INT_VAL_MIN());
    branch(*this, goat, INT_VAR_NONE(), INT_VAL_MIN());
    branch(*this, cabbage, INT_VAR_NONE(), INT_VAL_MIN());
    branch(*this, boat, INT_VAR_NONE(), INT_VAL_MIN());

    output("boat_pos", boat);
    output("cabbage_pos", cabbage);
    output("goat_pos", goat);
    output("wolf_pos", wolf);
  }

  WolfGoatCabbage(WolfGoatCabbage& s) : dcp::Space(s) {
    wolf.update(*this, s.wolf);
    goat.update(*this, s.goat);
    cabbage.update(*this, s.cabbage);
    boat.update(*this, s.boat);
  }
  Gecode::Space* copy() override { return new WolfGoatCabbage(*this); }
};

DCP_MODEL(WolfGoatCabbage)
