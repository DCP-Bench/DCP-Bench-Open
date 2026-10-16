#include "dcp.h"

// Candies: hand out candies to children in a line so that every child gets at
// least one, a child with a higher rating than a neighbour gets more candies
// than that neighbour, and the total number of candies is minimal.
class Candies : public dcp::Space {
 protected:
  IntVarArray x;  // x[i]: number of candies for child i
  IntVar z;       // total number of candies

 public:
  explicit Candies(const json& instance) {
    std::vector<int> ratings = instance.at("ratings").get<std::vector<int>>();
    int n = static_cast<int>(ratings.size());

    // every child gets at least 1 candy; a child never needs more than n
    // (the strictly increasing ratings case gives the last child n candies)
    x = IntVarArray(*this, n, 1, n);

    // a child with a higher rating than a sitting neighbour gets more candies
    // than that neighbour; equal ratings impose nothing
    for (int i = 0; i + 1 < n; ++i) {
      if (ratings[i] > ratings[i + 1]) rel(*this, x[i], IRT_GR, x[i + 1]);
      else if (ratings[i] < ratings[i + 1]) rel(*this, x[i], IRT_LE, x[i + 1]);
    }

    // minimise the total number of candies handed out
    z = expr(*this, sum(x), IPL_DOM);

    branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    minimize(z);
    output("x", x);
    output("z", z);
  }

  Candies(Candies& s) : dcp::Space(s) {
    x.update(*this, s.x);
    z.update(*this, s.z);
  }
  Gecode::Space* copy() override { return new Candies(*this); }
};

DCP_MODEL(Candies)
