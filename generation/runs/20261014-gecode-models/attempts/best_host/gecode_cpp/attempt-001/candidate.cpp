#include "dcp.h"

// Dinner party seating: six guests (0 Andrew, 1 Betty, 2 Cara, 3 Dave, 4 Erica,
// 5 Frank) sit around a round table of six seats. Arrange them so that the number
// of neighbouring pairs who do not get along is minimal.

class BestHost : public dcp::Space {
 protected:
  IntVarArray x;       // x[k]: guest sitting in seat k
  IntVar conflicts;    // number of neighbouring pairs that do not get along

 public:
  explicit BestHost(const json& instance) : x(*this, 6, 0, 5) {
    (void)instance;    // the problem has no instance fields; the data below is the problem's own
    const int n = 6;

    // problem data: the guests each guest will sit next to (their get-along list)
    const std::vector<std::vector<int>> gets_along = {
        {3, 5},   // Andrew sits only next to Dave and Frank
        {2, 4},   // Betty sits only next to Cara and Erica
        {1, 5},   // Cara sits only next to Betty and Frank
        {0, 4},   // Dave sits only next to Andrew and Erica
        {1, 3},   // Erica sits only next to Betty and Dave
        {0, 2}};  // Frank sits only next to Andrew and Cara

    // the pairs that do not get along, as ordered pairs (a, b), a != b
    TupleSet conflicting(2);
    for (int a = 0; a < n; ++a)
      for (int b = 0; b < n; ++b) {
        if (a == b) continue;
        bool along = false;
        for (int g : gets_along[a]) along = along || (g == b);
        if (!along) conflicting.add(IntArgs({a, b}));
      }
    conflicting.finalize();

    // every guest sits in exactly one seat, and every seat holds one guest
    distinct(*this, x, IPL_DOM);

    // a conflict is counted for every pair of seats next to each other around the table
    // (seat k and seat k+1, with seat 5 next to seat 0)
    BoolVarArgs clash;
    for (int k = 0; k < n; ++k) {
      IntVarArgs pair;
      pair << x[k] << x[(k + 1) % n];
      BoolVar c(*this, 0, 1);
      extensional(*this, pair, conflicting, true, Reify(c, RM_EQV), IPL_DOM);
      clash << c;
    }

    // total number of conflicts at dinner
    conflicts = expr(*this, sum(clash));

    // minimise the conflicts; seats are decided, and the conflicts follow from them
    branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    minimize(conflicts);
    output("x", x);
  }

  BestHost(BestHost& s) : dcp::Space(s) {
    x.update(*this, s.x);
    conflicts.update(*this, s.conflicts);
  }
  Gecode::Space* copy() override { return new BestHost(*this); }
};

DCP_MODEL(BestHost)
