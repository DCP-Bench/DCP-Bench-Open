// Thick as thieves: six suspects, at least four innocent; the innocent tell the truth and the guilty
// lie. Decide who is guilty from what they said.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  enum { ARTIE, BILL, CRACKITT, DODGY, EDGY, FINGERS };

  // guilty[s] = 1 if suspect s is guilty
  vec<IntVar*> guilty;
  createVars(guilty, 6, 0, 1, true);
  vec<BoolView> is_guilty;
  for (int s = 0; s < 6; ++s) {
    BoolView b = newBoolVar();
    bool2int(b, guilty[s]);
    is_guilty.push(b);
  }

  // the getaway car held barely two, so at least four of them are innocent
  int_linear(guilty, IRT_LE, 2);

  // ARTIE: "It wasn't me." He tells the truth exactly when he is innocent, which holds for any
  // value of guilty[ARTIE], so it adds no constraint.

  // BILL: "Crackitt was in it up to his neck." Bill is guilty exactly when this is false.
  int_rel_reif(guilty[CRACKITT], IRT_EQ, 0, is_guilty[BILL]);

  // CRACKITT: "No I wasn't." Crackitt is guilty exactly when "I was not guilty" is false, which
  // holds for any value of guilty[CRACKITT], so it adds no constraint.

  // DODGY: "If Crackitt did it, Bill did it with him." Dodgy is guilty exactly when this is false,
  // that is when Crackitt is guilty and Bill is not.
  {
    vec<int> coef;
    vec<IntVar*> terms;
    coef.push(1);  terms.push(guilty[CRACKITT]);
    coef.push(-1); terms.push(guilty[BILL]);
    int_linear(coef, terms, IRT_GE, 1, is_guilty[DODGY]);
  }

  // EDGY: "Nobody did it alone." Edgy is guilty exactly when this is false, that is when exactly
  // one suspect is guilty.
  int_linear(guilty, IRT_EQ, 1, is_guilty[EDGY]);

  // FINGERS: "That's right: it was Artie and Dodgy together." Fingers is guilty exactly when this
  // is false, that is when Artie and Dodgy are not both guilty.
  {
    vec<IntVar*> pair;
    pair.push(guilty[ARTIE]);
    pair.push(guilty[DODGY]);
    int_linear(pair, IRT_LE, 1, is_guilty[FINGERS]);
  }

  branch(guilty, VAR_INORDER, VAL_MIN);
  outputs = {{"artie", dcp::out(guilty[ARTIE])}, {"bill", dcp::out(guilty[BILL])},
             {"crackitt", dcp::out(guilty[CRACKITT])}, {"dodgy", dcp::out(guilty[DODGY])},
             {"edgy", dcp::out(guilty[EDGY])}, {"fingers", dcp::out(guilty[FINGERS])}};
}
