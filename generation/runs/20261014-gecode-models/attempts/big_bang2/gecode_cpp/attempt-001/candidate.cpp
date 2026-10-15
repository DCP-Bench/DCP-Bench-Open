#include "dcp.h"

// Nontransitive dice: five six-faced dice with face values 1..12 whose pairwise
// 'beats' relation is the Rock-Paper-Scissors-Lizard-Spock graph.
// Dice (rows): 0 Rock, 1 Paper, 2 Scissors, 3 Lizard, 4 Spock.
// The instance carries no fields; the sizes and the beats table are fixed by the problem.
class BigBang2 : public dcp::Space {
 protected:
  static const int dice_count = 5;
  static const int faces = 6;
  static const int max_value = 12;
  IntVarArray face;  // face[faces * d + k]: value of face k of die d

  // Die a beats die b when a has a strictly larger face than b in more than half
  // of the 36 pairs of faces, that is in at least 19 pairs.
  void beats(int a, int b) {
    BoolVarArgs wins;
    for (int i = 0; i < faces; ++i)
      for (int j = 0; j < faces; ++j)
        wins << expr(*this, face[faces * a + i] > face[faces * b + j]);
    linear(*this, wins, IRT_GQ, 19);
  }

 public:
  explicit BigBang2(const json& instance) {
    (void)instance;
    face = IntVarArray(*this, dice_count * faces, 1, max_value);

    // the faces of a die are listed in increasing order: a die's beats relations
    // count pairs of faces, so reordering a die's faces changes nothing
    for (int d = 0; d < dice_count; ++d)
      for (int k = 0; k + 1 < faces; ++k)
        rel(*this, face[faces * d + k] <= face[faces * d + k + 1]);

    // Rock(1) crushes Scissors(3)
    beats(0, 2);
    // Rock(1) crushes Lizard(4)
    beats(0, 3);
    // Paper(2) covers Rock(1)
    beats(1, 0);
    // Paper(2) disproves Spock(5)
    beats(1, 4);
    // Scissors(3) cuts Paper(2)
    beats(2, 1);
    // Scissors(3) decapitate Lizard(4)
    beats(2, 3);
    // Lizard(4) eats Paper(2)
    beats(3, 1);
    // Lizard(4) poisons Spock(5)
    beats(3, 4);
    // Spock(5) vaporizes Rock(1)
    beats(4, 0);
    // Spock(5) smashes Scissors(3)
    beats(4, 2);

    // print the dice: one row per die, in the order Rock, Paper, Scissors, Lizard, Spock
    Matrix<IntVarArray> dice(face, faces, dice_count);
    output("dice", dice);

    // search: learn from failures (AFC) and restart with Luby, since the reified
    // face-pair counts propagate weakly
    restarts(100);
    branch(*this, face, INT_VAR_AFC_SIZE_MAX(0.99), INT_VAL_MIN());
  }

  BigBang2(BigBang2& s) : dcp::Space(s) { face.update(*this, s.face); }
  Gecode::Space* copy() override { return new BigBang2(*this); }
};

DCP_MODEL(BigBang2)
