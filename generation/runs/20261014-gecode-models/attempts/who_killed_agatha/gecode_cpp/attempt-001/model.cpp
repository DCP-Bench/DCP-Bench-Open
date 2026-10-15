#include "dcp.h"

// Who killed Aunt Agatha? Someone in Dreadsbury Mansion killed her. Agatha, the
// butler and Charles are the only people living there. Output: 0-based index of
// the killer (0 = Agatha herself, 1 = the butler, 2 = Charles).
class WhoKilledAgatha : public dcp::Space {
 protected:
  static const int AGATHA = 0;
  static const int BUTLER = 1;
  static const int CHARLES = 2;

  int n;                   // number of people living in the mansion
  BoolVarArray hates;      // hates[x*n + y] = 1 iff x hates y
  BoolVarArray richer;     // richer[x*n + y] = 1 iff x is richer than y
  BoolVarArray is_killer;  // is_killer[x] = 1 iff x is the killer (one-hot)
  IntVar killer;           // index of the killer

  BoolVar hate(int x, int y) const { return hates[x * n + y]; }
  BoolVar richer_than(int x, int y) const { return richer[x * n + y]; }

  // a implies b, as the clause (not a) or b
  void implies(BoolVar a, BoolVar b) {
    BoolVarArgs pos, neg;
    pos << b;
    neg << a;
    clause(*this, BOT_OR, pos, neg, 1);
  }

  // not both a and b, as the clause (not a) or (not b)
  void not_both(BoolVar a, BoolVar b) {
    BoolVarArgs pos, neg;
    neg << a << b;
    clause(*this, BOT_OR, pos, neg, 1);
  }

  // a or b
  void either(BoolVar a, BoolVar b) {
    BoolVarArgs pos, neg;
    pos << a << b;
    clause(*this, BOT_OR, pos, neg, 1);
  }

 public:
  explicit WhoKilledAgatha(const json& instance) {
    std::vector<std::string> names = instance.at("names").get<std::vector<std::string>>();
    if (names.size() != 3) throw std::invalid_argument("expected three people: Agatha, the butler, Charles");
    n = static_cast<int>(names.size());

    hates = BoolVarArray(*this, n * n, 0, 1);
    richer = BoolVarArray(*this, n * n, 0, 1);
    is_killer = BoolVarArray(*this, n, 0, 1);
    killer = IntVar(*this, 0, n - 1);

    // the killer is one of the people living in the mansion (killer domain above)
    channel(*this, is_killer, killer);

    // a killer always hates his victim, Aunt Agatha
    for (int x = 0; x < n; ++x) implies(is_killer[x], hate(x, AGATHA));

    // and is no richer than his victim, Aunt Agatha
    for (int x = 0; x < n; ++x) not_both(is_killer[x], richer_than(x, AGATHA));

    // Charles hates no one that Agatha hates
    for (int x = 0; x < n; ++x) not_both(hate(AGATHA, x), hate(CHARLES, x));

    // Agatha hates everybody except the butler
    for (int x = 0; x < n; ++x) rel(*this, hate(AGATHA, x), IRT_EQ, x == BUTLER ? 0 : 1);

    // the butler hates everyone not richer than Aunt Agatha
    for (int x = 0; x < n; ++x) either(richer_than(x, AGATHA), hate(BUTLER, x));

    // the butler hates everyone whom Agatha hates
    for (int x = 0; x < n; ++x) implies(hate(AGATHA, x), hate(BUTLER, x));

    // noone hates everyone: each person fails to hate at least one person
    for (int x = 0; x < n; ++x) {
      BoolVarArgs pos, neg;
      for (int y = 0; y < n; ++y) neg << hate(x, y);
      clause(*this, BOT_OR, pos, neg, 1);
    }

    // richer is a comparison of wealth: no one is richer than himself,
    // richer is asymmetric and transitive
    for (int x = 0; x < n; ++x) {
      BoolVarArgs pos, neg;
      neg << richer_than(x, x);
      clause(*this, BOT_OR, pos, neg, 1);
    }
    for (int x = 0; x < n; ++x)
      for (int y = x + 1; y < n; ++y) not_both(richer_than(x, y), richer_than(y, x));
    for (int x = 0; x < n; ++x)
      for (int y = 0; y < n; ++y)
        for (int z = 0; z < n; ++z) {
          BoolVarArgs pos, neg;
          pos << richer_than(x, z);
          neg << richer_than(x, y) << richer_than(y, z);
          clause(*this, BOT_OR, pos, neg, 1);
        }

    branch(*this, killer, INT_VAL_MIN());
    branch(*this, is_killer, BOOL_VAR_NONE(), BOOL_VAL_MIN());
    branch(*this, hates, BOOL_VAR_NONE(), BOOL_VAL_MIN());
    branch(*this, richer, BOOL_VAR_NONE(), BOOL_VAL_MIN());

    output("killer", killer);
  }

  WhoKilledAgatha(WhoKilledAgatha& s) : dcp::Space(s), n(s.n) {
    hates.update(*this, s.hates);
    richer.update(*this, s.richer);
    is_killer.update(*this, s.is_killer);
    killer.update(*this, s.killer);
  }

  Gecode::Space* copy() override { return new WhoKilledAgatha(*this); }
};

DCP_MODEL(WhoKilledAgatha)
