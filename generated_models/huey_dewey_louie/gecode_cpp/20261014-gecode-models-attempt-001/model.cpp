#include "dcp.h"

// Huey, Dewey and Louie are questioned about guilt. Each makes a statement, and
// because they are cub scouts who cannot tell a lie, every statement is true.
// Decide who (if anyone) is guilty. Each guilty flag is a Boolean: 1 = guilty.
class HueyDeweyLouie : public dcp::Space {
 protected:
  BoolVar huey, dewey, louie;

 public:
  // The problem has no instance fields: the statements are the whole specification.
  explicit HueyDeweyLouie(const json& instance) : huey(*this, 0, 1), dewey(*this, 0, 1), louie(*this, 0, 1) {
    (void)instance;

    // Huey: "Dewey and Louie have equal share in it; if one is guilty, so is the other."
    // Dewey and Louie are guilty together or not at all.
    rel(*this, dewey, IRT_EQ, louie);

    // Dewey: "If Huey is guilty, then so am I."
    rel(*this, (huey == 1) >> (dewey == 1));

    // Louie: "Dewey and I are not both guilty."
    BoolVarArgs dewey_and_louie;
    dewey_and_louie << dewey << louie;
    linear(*this, dewey_and_louie, IRT_LQ, 1);

    // branch on the three guilt flags; the statements above already fix every one of them
    BoolVarArgs flags;
    flags << huey << dewey << louie;
    branch(*this, flags, BOOL_VAR_NONE(), BOOL_VAL_MIN());

    output("huey", huey);
    output("dewey", dewey);
    output("louie", louie);
  }

  HueyDeweyLouie(HueyDeweyLouie& s) : dcp::Space(s) {
    huey.update(*this, s.huey);
    dewey.update(*this, s.dewey);
    louie.update(*this, s.louie);
  }

  Gecode::Space* copy() override { return new HueyDeweyLouie(*this); }
};

DCP_MODEL(HueyDeweyLouie)
