#include "dcp.h"

// Finding celebrities: a party of n guests with a "knows" relation. A celebrity
// is a guest whom everybody knows and who knows only other celebrities. At
// least one celebrity is present. Output the celebrity flags in input order.
class FindingCelebrities : public dcp::Space {
 protected:
  int n;
  BoolVarArray celeb;  // celeb[c] = 1 if guest c is a celebrity

 public:
  explicit FindingCelebrities(const json& instance) {
    std::vector<std::vector<int>> knows;
    for (const auto& row : instance.at("graph")) {
      std::vector<int> r;
      for (const auto& x : row) r.push_back(x.get<int>());
      knows.push_back(r);
    }
    n = static_cast<int>(knows.size());
    celeb = BoolVarArray(*this, n, 0, 1);

    // everybody at the party knows a celebrity (the guest's own entry included)
    for (int c = 0; c < n; ++c)
      for (int i = 0; i < n; ++i)
        if (knows[i][c] == 0) rel(*this, celeb[c] == 0);

    // a celebrity knows only other celebrities
    for (int c = 0; c < n; ++c)
      for (int j = 0; j < n; ++j)
        if (j != c && knows[c][j] == 1) rel(*this, (celeb[c] == 1) >> (celeb[j] == 1));

    // at least one celebrity is present
    linear(*this, celeb, IRT_GQ, 1);

    branch(*this, celeb, BOOL_VAR_NONE(), BOOL_VAL_MIN());
    output("celebrities", celeb);
  }

  FindingCelebrities(FindingCelebrities& s) : dcp::Space(s), n(s.n) {
    celeb.update(*this, s.celeb);
  }
  Gecode::Space* copy() override { return new FindingCelebrities(*this); }
};

DCP_MODEL(FindingCelebrities)
