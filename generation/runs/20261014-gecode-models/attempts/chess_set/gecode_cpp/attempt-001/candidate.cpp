#include "dcp.h"

// Chess set production: decide how many small and large boxwood chess sets to
// make each week so that total profit is maximised, subject to lathe time and
// boxwood supply.
//
// The problem has no instance data. Its numbers are fixed by the statement and
// are mirrored here as problem constants.
class ChessSet : public dcp::Space {
 protected:
  IntVar small_set;  // number of small sets made per week
  IntVar large_set;  // number of large sets made per week
  IntVar max_profit; // total weekly profit in dollars

 public:
  explicit ChessSet(const json& instance) {
    (void)instance;  // no instance fields; all data below is from the statement

    // problem constants from the statement
    const int lathe_hours = 4 * 40;   // four lathes, 40-hour week each
    const int boxwood_kg = 200;       // boxwood obtainable per week
    const int small_lathe_h = 3;      // machining hours per small set
    const int large_lathe_h = 2;      // machining hours per large set
    const int small_kg = 1;           // boxwood per small set
    const int large_kg = 3;           // boxwood per large set
    const int small_profit = 5;       // profit per small set
    const int large_profit = 20;      // profit per large set

    // a set count cannot exceed what the lathes alone allow
    small_set = IntVar(*this, 0, lathe_hours / small_lathe_h);
    large_set = IntVar(*this, 0, lathe_hours / large_lathe_h);

    IntVarArgs x;
    x << small_set << large_set;

    // the lathes have 160 hours per week available
    linear(*this, IntArgs({small_lathe_h, large_lathe_h}), x, IRT_LQ, lathe_hours);

    // only 200 kg of boxwood per week can be obtained
    linear(*this, IntArgs({small_kg, large_kg}), x, IRT_LQ, boxwood_kg);

    // profit: $5 per small set and $20 per large set
    max_profit = expr(*this, small_profit * small_set + large_profit * large_set);
    maximize(max_profit);

    branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MAX());

    output("small_set", small_set);
    output("large_set", large_set);
    output("max_profit", max_profit);
  }

  ChessSet(ChessSet& s) : dcp::Space(s) {
    small_set.update(*this, s.small_set);
    large_set.update(*this, s.large_set);
    max_profit.update(*this, s.max_profit);
  }
  Gecode::Space* copy() override { return new ChessSet(*this); }
};

DCP_MODEL(ChessSet)
