#include "dcp.h"

// Farmer and cows: cow i (numbered 1 to num_cows) gives i litres of milk. Distribute
// the cows to the sons so that son s gets cows_per_son[s] cows and every son gets the
// same total quantity of milk.
class FarmerAndCows : public dcp::Space {
 protected:
  IntVarArray cow;      // cow[i]: son that receives cow i+1 (0-based)
  BoolVarArray gives;   // gives[i * sons + s] = 1 iff cow i+1 goes to son s

 public:
  explicit FarmerAndCows(const json& instance) {
    int cows = instance.at("num_cows").get<int>();
    int sons = instance.at("num_sons").get<int>();
    std::vector<int> per_son = instance.at("cows_per_son").get<std::vector<int>>();

    cow = IntVarArray(*this, cows, 0, sons - 1);
    gives = BoolVarArray(*this, cows * sons, 0, 1);

    // every cow goes to exactly one son
    for (int i = 0; i < cows; ++i) {
      BoolVarArgs row;
      for (int s = 0; s < sons; ++s) row << gives[i * sons + s];
      channel(*this, row, cow[i], 0);
    }

    // total milk is 1 + 2 + ... + cows; it is shared equally among the sons
    int total = cows * (cows + 1) / 2;
    if (total % sons != 0) {
      this->fail();
      return;
    }
    int share = total / sons;

    IntVarArgs cows_of_cow;
    for (int i = 0; i < cows; ++i) cows_of_cow << cow[i];

    // every son receives the number of cows given in the distribution
    for (int s = 0; s < sons; ++s) count(*this, cows_of_cow, s, IRT_EQ, per_son[s]);

    // every son gets the same quantity of milk: the cow numbers he receives add up to share
    IntArgs milk(cows);
    for (int i = 0; i < cows; ++i) milk[i] = i + 1;
    for (int s = 0; s < sons; ++s) {
      BoolVarArgs son_cows;
      for (int i = 0; i < cows; ++i) son_cows << gives[i * sons + s];
      linear(*this, milk, son_cows, IRT_EQ, share, IPL_DOM);
    }

    // sons who receive the same number of cows are interchangeable (same cow count,
    // same milk target): break the symmetry by value precedence within each such group
    for (int s = 0; s < sons; ++s) {
      bool first_of_group = true;
      for (int t = 0; t < s; ++t)
        if (per_son[t] == per_son[s]) first_of_group = false;
      if (!first_of_group) continue;
      std::vector<int> members;
      for (int t = s; t < sons; ++t)
        if (per_son[t] == per_son[s]) members.push_back(t);
      if (members.size() >= 2) {
        IntArgs values(static_cast<int>(members.size()));
        for (std::size_t k = 0; k < members.size(); ++k) values[static_cast<int>(k)] = members[k];
        precede(*this, cows_of_cow, values);
      }
    }

    // fill one son at a time, giving him the larger cows first: each son's cows are
    // decided before the next son's, which finds a complete split quickly
    for (int s = 0; s < sons; ++s) {
      BoolVarArgs son_cows;
      for (int i = cows - 1; i >= 0; --i) son_cows << gives[i * sons + s];
      branch(*this, son_cows, BOOL_VAR_NONE(), BOOL_VAL_MAX());
    }
    output("cow_assignments", cow);
  }

  FarmerAndCows(FarmerAndCows& s) : dcp::Space(s) {
    cow.update(*this, s.cow);
    gives.update(*this, s.gives);
  }
  Gecode::Space* copy() override { return new FarmerAndCows(*this); }
};

DCP_MODEL(FarmerAndCows)
