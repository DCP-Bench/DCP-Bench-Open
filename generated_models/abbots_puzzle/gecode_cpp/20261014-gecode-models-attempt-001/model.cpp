#include "dcp.h"

// Abbot's puzzle: 100 bushels of corn are distributed among 100 people so that
// each man gets 3 bushels, each woman 2 bushels and each child half a bushel.
// There are five times as many women as men. Find the numbers of men, women and
// children.
class AbbotsPuzzle : public dcp::Space {
 protected:
  IntVar men;
  IntVar women;
  IntVar children;

 public:
  explicit AbbotsPuzzle(const json& instance) {
    // the problem fixes 100 people and 100 bushels; the instance has no fields
    const int people = 100;
    const int bushels = 100;

    men = IntVar(*this, 0, people);
    women = IntVar(*this, 0, people);
    children = IntVar(*this, 0, people);

    // the 100 people are men, women and children
    IntVarArgs heads;
    heads << men << women << children;
    linear(*this, IntArgs({1, 1, 1}), heads, IRT_EQ, people);

    // the 100 bushels are paid out: 3 per man, 2 per woman, half per child.
    // Both sides are doubled so that the half bushel has an integer coefficient.
    IntVarArgs bushelsPaid;
    bushelsPaid << men << women << children;
    linear(*this, IntArgs({6, 4, 1}), bushelsPaid, IRT_EQ, 2 * bushels);

    // there are five times as many women as men
    IntVarArgs womenAndMen;
    womenAndMen << women << men;
    linear(*this, IntArgs({1, -5}), womenAndMen, IRT_EQ, 0);

    IntVarArgs counts;
    counts << men << women << children;
    branch(*this, counts, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("children", children);
    output("men", men);
    output("women", women);
  }

  AbbotsPuzzle(AbbotsPuzzle& s) : dcp::Space(s) {
    men.update(*this, s.men);
    women.update(*this, s.women);
    children.update(*this, s.children);
  }

  Gecode::Space* copy() override { return new AbbotsPuzzle(*this); }
};

DCP_MODEL(AbbotsPuzzle)
