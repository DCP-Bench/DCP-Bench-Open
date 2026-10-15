#include "dcp.h"

// Circular table (Averbach): three players X, Y and Z of nationalities American,
// English and French sit around a circular table with seats 0, 1 and 2. Each
// passes three cards to the person on their right, so seat p passes to seat
// (p + 1) mod 3. The model finds the seat of each player and each nationality.
class CircularTableAverbach : public dcp::Space {
 protected:
  IntVar x, y, z;                     // seat of X, Y and Z
  IntVar american, english, french;   // seat of the American, English and French person

 public:
  // The instance has no fields: the seats and clues come from the problem statement.
  explicit CircularTableAverbach(const json& instance) {
    (void)instance;
    x = IntVar(*this, 0, 2);
    y = IntVar(*this, 0, 2);
    z = IntVar(*this, 0, 2);
    american = IntVar(*this, 0, 2);
    english = IntVar(*this, 0, 2);
    french = IntVar(*this, 0, 2);

    // X, Y and Z sit in three different seats
    IntVarArgs players;
    players << x << y << z;
    distinct(*this, players, IPL_DOM);

    // the American, the English and the French sit in three different seats
    IntVarArgs nationalities;
    nationalities << american << english << french;
    distinct(*this, nationalities, IPL_DOM);

    // Y passed three hearts to the American, so the American sits on Y's right:
    // american = (y + 1) mod 3
    element(*this, IntArgs({1, 2, 0}), y, american);

    // X passed the queen of spades and two diamonds to the person who passed
    // their cards to the Frenchwoman. That person sits at french - 1 and X passes
    // to x + 1, so french = (x + 2) mod 3
    element(*this, IntArgs({2, 0, 1}), x, french);

    // branch on every seat; the domains are 0..2, so this fixes the whole assignment
    IntVarArgs all;
    all << x << y << z << american << english << french;
    branch(*this, all, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("american", american);
    output("english", english);
    output("french", french);
    output("x", x);
    output("y", y);
    output("z", z);
  }

  CircularTableAverbach(CircularTableAverbach& s) : dcp::Space(s) {
    x.update(*this, s.x);
    y.update(*this, s.y);
    z.update(*this, s.z);
    american.update(*this, s.american);
    english.update(*this, s.english);
    french.update(*this, s.french);
  }

  Gecode::Space* copy() override { return new CircularTableAverbach(*this); }
};

DCP_MODEL(CircularTableAverbach)
