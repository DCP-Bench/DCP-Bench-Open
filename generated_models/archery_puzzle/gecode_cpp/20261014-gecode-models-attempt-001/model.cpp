#include "dcp.h"

// Archery puzzle: the young archer shoots as many arrows as she pleases. Each hit on
// target j scores targets[j] points. Choose the number of hits on each target so that
// the total score comes as close as possible to target_score, over or under, and print
// the hits per target.
class Archery : public dcp::Space {
 protected:
  IntVarArray hits;  // hits[j]: number of arrows on target j
  IntVar dev;        // how far the total score is from the target score

 public:
  explicit Archery(const json& instance) {
    int target = instance.at("target_score").get<int>();
    std::vector<int> targets = instance.at("targets").get<std::vector<int>>();
    int n = static_cast<int>(targets.size());

    // with no arrows the deviation is target, so an optimal total is at most 2 * target
    // and each target can take at most 2 * target / score hits
    hits = IntVarArray(*this, n, 0, 2 * target);
    for (int j = 0; j < n; ++j) dom(*this, hits[j], 0, 2 * target / targets[j]);

    // the total score is the sum of hits times the score of each target
    IntVar total = expr(*this, sum(IntArgs(targets), hits), IPL_BND);

    // the deviation is the distance from the target score, over or under
    dev = expr(*this, abs(total - target));

    branch(*this, hits, INT_VAR_SIZE_MIN(), INT_VAL_SPLIT_MIN());
    minimize(dev);
    output("hits", hits);
  }

  Archery(Archery& s) : dcp::Space(s) {
    hits.update(*this, s.hits);
    dev.update(*this, s.dev);
  }
  Gecode::Space* copy() override { return new Archery(*this); }
};

DCP_MODEL(Archery)
