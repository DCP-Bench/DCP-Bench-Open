#include "dcp.h"

// Birthday coins: 15 coins (half-crowns, shillings and sixpences) add up to
// £1 5s 6d. How many half-crowns were given?
class BirthdayCoins : public dcp::Space {
 protected:
  IntVar half_crowns;  // number of half-crowns
  IntVar shillings;    // number of shillings
  IntVar sixpences;    // number of sixpences

 public:
  explicit BirthdayCoins(const json& instance)
      : half_crowns(*this, 1, 15), shillings(*this, 1, 15), sixpences(*this, 1, 15) {
    (void)instance;  // the problem has no instance data; the figures below come from the statement

    IntVarArgs coins;
    coins << half_crowns << shillings << sixpences;

    // he was given 15 coins in all
    linear(*this, coins, IRT_EQ, 15);

    // the coins add up to £1 5s 6d = 306 pence; a half-crown is 30 pence,
    // a shilling 12 pence, a sixpence 6 pence
    linear(*this, IntArgs({30, 12, 6}), coins, IRT_EQ, 306, IPL_DOM);

    branch(*this, coins, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("half_crowns", half_crowns);
  }

  BirthdayCoins(BirthdayCoins& s) : dcp::Space(s) {
    half_crowns.update(*this, s.half_crowns);
    shillings.update(*this, s.shillings);
    sixpences.update(*this, s.sixpences);
  }
  Gecode::Space* copy() override { return new BirthdayCoins(*this); }
};

DCP_MODEL(BirthdayCoins)
