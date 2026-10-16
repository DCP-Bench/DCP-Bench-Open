#include "dcp.h"

// Equal-sized groups: split a sorted list of N elements into K contiguous groups
// by choosing K-1 split points, never between two equal elements, so that the
// total deviation of the group sizes from round(N/K) is as small as possible.
class EqualSizedGroups : public dcp::Space {
 protected:
  IntVarArray x;  // x[i]: 1-based index of the last element of group i+1
  IntVar total;   // total deviation of the group sizes from the ideal size

 public:
  explicit EqualSizedGroups(const json& instance) {
    std::vector<int> a = instance.at("a").get<std::vector<int>>();
    int k = instance.at("k").get<int>();
    int n = static_cast<int>(a.size());

    // ideal group size round(N/K), halves rounded up (taken from the instance)
    int ideal = (2 * n + k) / (2 * k);

    // a split is allowed only after element j (1-based) when a[j-1] != a[j]:
    // items with the same value must stay in the same group
    std::vector<int> breaks;
    for (int j = 1; j < n; ++j)
      if (a[j - 1] != a[j]) breaks.push_back(j);

    x = IntVarArray(*this, k - 1, 1, n - 1);
    for (int i = 0; i < k - 1; ++i) dom(*this, x[i], IntSet(IntArgs(breaks)));

    // split points in increasing order, so every group is non-empty
    for (int i = 0; i + 1 < k - 1; ++i) rel(*this, x[i], IRT_LE, x[i + 1]);

    // deviation of each group size from the ideal size; the first group starts
    // at 0 and the last group ends at N
    IntVar zero(*this, 0, 0);
    IntVar end(*this, n, n);
    IntVarArgs deviation;
    for (int g = 0; g < k; ++g) {
      IntVar left = zero;
      if (g > 0) left = x[g - 1];
      IntVar right = end;
      if (g < k - 1) right = x[g];
      deviation << expr(*this, abs(right - left - ideal));
    }

    // total error = sum of the deviations
    total = expr(*this, sum(deviation));

    branch(*this, x, INT_VAR_NONE(), INT_VAL_MIN());
    minimize(total);
    output("x", x);
  }

  EqualSizedGroups(EqualSizedGroups& s) : dcp::Space(s) {
    x.update(*this, s.x);
    total.update(*this, s.total);
  }

  Gecode::Space* copy() override { return new EqualSizedGroups(*this); }
};

DCP_MODEL(EqualSizedGroups)
