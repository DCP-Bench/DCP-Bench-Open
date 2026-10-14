#include "dcp.h"

// Twelve-pack problem: given a target number of items, choose how many packs of
// each size to buy so that the total number of items meets or exceeds the target
// as closely as possible. The pack sizes are read from the instance, so any
// number of pack sizes is handled.
class TwelvePack : public dcp::Space {
 protected:
  IntVarArray counts;  // counts[i]: number of packs of size packs[i] used
  IntVar total;        // number of items bought

 public:
  explicit TwelvePack(const json& instance) {
    std::vector<int> packs = instance.at("packs").get<std::vector<int>>();
    int target = instance.at("target").get<int>();

    // the number of packs of each size: an optimal combination never takes more
    // than ceil(target / size) packs of one size, so that bounds each count
    IntVarArgs c;
    for (int size : packs) c << IntVar(*this, 0, target / size + 1);
    counts = IntVarArray(*this, c);

    // total items bought is the sum of pack size times pack count, over every
    // pack size in the instance
    IntVarArgs pack_counts;
    for (int i = 0; i < counts.size(); ++i) pack_counts << counts[i];
    total = expr(*this, sum(IntArgs(packs), pack_counts));

    // the combination must meet or exceed the target
    rel(*this, total, IRT_GQ, target);

    // branch on the pack counts, fewest packs first
    branch(*this, counts, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    // the closest combination: fewest items above the target
    minimize(total);
    output("counts", counts);
  }

  TwelvePack(TwelvePack& s) : dcp::Space(s) {
    counts.update(*this, s.counts);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new TwelvePack(*this); }
};

DCP_MODEL(TwelvePack)
