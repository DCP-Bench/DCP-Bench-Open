#include "dcp.h"

// Bales of hay: find the weight of each of n bales, given the weights of all
// pairs of bales (each pair weighed together, the pair weights listed in
// numerical order without saying which pair gave which weight).
class BalesOfHay : public dcp::Space {
 protected:
  IntVarArray bales;  // bales[i]: weight of bale i, listed in increasing order

 public:
  explicit BalesOfHay(const json& instance) {
    // the number of bales and the sorted list of pairwise weights come from the instance
    int n = instance.at("n").get<int>();
    std::vector<int> weights = instance.at("weights").get<std::vector<int>>();

    // the list holds one weight per pair of bales (n(n-1)/2 entries), sorted
    // every bale weighs between 0 and the heaviest pair weight
    int wmax = weights.back();
    int total = 0;
    for (int w : weights) total += w;

    bales = IntVarArray(*this, n, 0, wmax);

    // each pair of bales has a total weight; the totals of all pairs must be exactly
    // the listed weights (each listed weight used as often as it occurs in the list)
    IntVarArgs sums;
    for (int i = 0; i < n; ++i)
      for (int j = i + 1; j < n; ++j) sums << expr(*this, bales[i] + bales[j]);

    std::vector<int> distinct;
    std::vector<int> multiplicity;
    for (int w : weights) {
      if (distinct.empty() || distinct.back() != w) {
        distinct.push_back(w);
        multiplicity.push_back(1);
      } else {
        ++multiplicity.back();
      }
    }
    // every pair total takes one of the listed values, and value v occurs as often as in the list
    const int kinds = static_cast<int>(distinct.size());
    IntSetArgs cards(kinds);
    IntArgs values(kinds);
    for (int k = 0; k < kinds; ++k) {
      values[k] = distinct[k];
      cards[k] = IntSet(multiplicity[k], multiplicity[k]);
    }
    count(*this, sums, cards, values, IPL_DOM);

    // implied: each bale is in n-1 pairs, so (n-1) times the sum of the bales equals
    // the sum of all pair weights
    IntArgs coef(n);
    for (int i = 0; i < n; ++i) coef[i] = n - 1;
    linear(*this, coef, bales, IRT_EQ, total);

    // the bales are listed in increasing order (the convention of the reference answer)
    for (int i = 0; i + 1 < n; ++i) rel(*this, bales[i], IRT_LQ, bales[i + 1]);

    branch(*this, bales, INT_VAR_NONE(), INT_VAL_MIN());
    output("bales", bales);
  }

  BalesOfHay(BalesOfHay& s) : dcp::Space(s) { bales.update(*this, s.bales); }
  Gecode::Space* copy() override { return new BalesOfHay(*this); }
};

DCP_MODEL(BalesOfHay)
