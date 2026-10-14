#include "dcp.h"

// Football team selection: choose players from goalkeeper, defender, midfielder
// and striker groups, spend as much as possible without going over the GBP 30
// million limit, and buy at least eleven players with the required numbers of
// each position. Prices are in GBP thousands (0.73 million = 730), so the total
// is an integer in thousands.
class Football : public dcp::Space {
 protected:
  IntVarArray x;  // x[i] = 1 if player i is bought; players in the order g1..g3, d1..d8, m1..m10, s1..s5
  IntVar z;       // total price of the chosen players, in GBP thousands

 public:
  explicit Football(const json& instance) {
    (void)instance;  // the data is fixed by the problem statement

    // prices of the 26 listed players, in GBP thousands
    const int goalkeepers = 3, defenders = 8, midfielders = 10, strikers = 5;
    const int players = goalkeepers + defenders + midfielders + strikers;
    const int gk0 = 0, df0 = gk0 + goalkeepers, mf0 = df0 + defenders, st0 = mf0 + midfielders;
    const std::vector<int> price = {
        730, 1280, 3880,                                        // g1..g3
        920, 1310, 1620, 2410, 2790, 3280, 3910, 4570,          // d1..d8
        1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130,  // m1..m10
        4460, 6470, 7780, 8390, 9500};                          // s1..s5
    const int budget = 30000;  // GBP 30 million, in thousands

    x = IntVarArray(*this, players, 0, 1);
    z = IntVar(*this, 0, budget);

    // helper: the Boolean variables of a group, from index `from` for `n` players
    auto group = [&](int from, int n) {
      IntVarArgs g;
      for (int i = from; i < from + n; ++i) g << x[i];
      return g;
    };
    IntVarArgs all;
    for (int i = 0; i < players; ++i) all << x[i];

    // must buy exactly 1 goalkeeper
    linear(*this, group(gk0, goalkeepers), IRT_EQ, 1);

    // must buy 2 or more defenders
    linear(*this, group(df0, defenders), IRT_GQ, 2);

    // must buy 3 or more midfielders
    linear(*this, group(mf0, midfielders), IRT_GQ, 3);

    // must buy 2 or more strikers
    linear(*this, group(st0, strikers), IRT_GQ, 2);

    // must buy at least eleven players in total
    linear(*this, all, IRT_GQ, 11);

    // total price z is the sum of the prices of the bought players
    linear(*this, IntArgs(price), all, IRT_EQ, z);

    // the chairman's limit: the total price must not go over GBP 30 million
    linear(*this, IntArgs(price), all, IRT_LQ, budget);

    // spend as much as you can: maximise the total price
    maximize(z);

    branch(*this, x, INT_VAR_NONE(), INT_VAL_MAX());
    output("z", z);
  }

  Football(Football& s) : dcp::Space(s) {
    x.update(*this, s.x);
    z.update(*this, s.z);
  }
  Gecode::Space* copy() override { return new Football(*this); }
};

DCP_MODEL(Football)
