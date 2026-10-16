#include "dcp.h"

// Thick as Thieves: six suspects each make one statement. Innocent suspects tell the
// truth and guilty suspects lie. The getaway car held at most two people, so at least
// four are innocent. Decide who is guilty.
//
// The instance carries no data: the puzzle is fixed, so the constants below come from
// the problem statement (six suspects, car capacity two).

class ThickAsThieves : public dcp::Space {
 protected:
  enum { ARTIE, BILL, CRACKITT, DODGY, EDGY, FINGERS, SUSPECTS };

  BoolVarArray guilty;  // guilty[s]: suspect s did it
  IntVar n_guilty;      // number of guilty suspects

 public:
  explicit ThickAsThieves(const json& instance) {
    (void)instance;
    guilty = BoolVarArray(*this, SUSPECTS, 0, 1);
    n_guilty = expr(*this, sum(guilty), IPL_DEF);

    // the getaway car was barely big enough to hold two, so at most two are guilty
    rel(*this, n_guilty <= 2);
    // a robbery was committed, so at least one is guilty
    rel(*this, n_guilty >= 1);

    // An innocent suspect tells the truth and a guilty one lies, so each suspect is
    // guilty exactly when that suspect's statement is false.

    // ARTIE: "It wasn't me." Artie's statement is false exactly when Artie is guilty,
    // so the rule holds whatever the value of guilty[ARTIE]: no constraint to post.

    // BILL: "Crackitt was in it up to his neck." Bill is guilty exactly when
    // Crackitt is innocent.
    rel(*this, guilty[BILL] == !guilty[CRACKITT]);

    // CRACKITT: "No I wasn't." Crackitt's statement is false exactly when Crackitt
    // is guilty, so the rule holds for either value: no constraint to post.

    // DODGY: "If Crackitt did it, Bill did it with him." The statement is false only
    // when Crackitt did it and Bill did not.
    rel(*this, guilty[DODGY] == (guilty[CRACKITT] && !guilty[BILL]));

    // EDGY: "Nobody did it alone." The statement is false only when exactly one
    // suspect is guilty.
    rel(*this, guilty[EDGY] == (n_guilty == 1));

    // FINGERS: "That's right: it was Artie and Dodgy together." The statement is true
    // only when exactly Artie and Dodgy are guilty, i.e. both are guilty and there are
    // two guilty suspects in total.
    rel(*this, guilty[FINGERS] == !(guilty[ARTIE] && guilty[DODGY] && (n_guilty == 2)));

    branch(*this, guilty, BOOL_VAR_NONE(), BOOL_VAL_MIN());

    output("artie", guilty[ARTIE]);
    output("bill", guilty[BILL]);
    output("crackitt", guilty[CRACKITT]);
    output("dodgy", guilty[DODGY]);
    output("edgy", guilty[EDGY]);
    output("fingers", guilty[FINGERS]);
  }

  ThickAsThieves(ThickAsThieves& s) : dcp::Space(s) {
    guilty.update(*this, s.guilty);
    n_guilty.update(*this, s.n_guilty);
  }
  Gecode::Space* copy() override { return new ThickAsThieves(*this); }
};

DCP_MODEL(ThickAsThieves)
