#include "dcp.h"

// Aircraft landing on one runway: land every aircraft at an exact time inside its
// time window, in the fixed landing sequence given by the instance, with the minimum
// separation between consecutive landings, and minimise the total penalty for
// landing before or after the target time.
class AircraftLanding : public dcp::Space {
 protected:
  IntVarArray landing;  // landing[i]: landing time of the i-th aircraft in the sequence
  IntVarArray penalty;  // penalty[i]: penalty of the i-th aircraft for its landing time
  IntVar total;         // total penalty, the objective

 public:
  explicit AircraftLanding(const json& instance) {
    std::vector<int> earliest = instance.at("earliest_landing");
    std::vector<int> latest = instance.at("latest_landing");
    std::vector<int> target = instance.at("target_landing");
    std::vector<int> penalty_before = instance.at("penalty_before");
    std::vector<int> penalty_after = instance.at("penalty_after");
    const auto& separation = instance.at("separation_time");
    int n = static_cast<int>(earliest.size());

    // each aircraft lands within its time window
    IntVarArgs times;
    for (int i = 0; i < n; ++i) times << IntVar(*this, earliest[i], latest[i]);
    landing = IntVarArray(*this, times);

    // penalty for landing before the target: penalty_before per unit of time early,
    // and penalty_after per unit of time late. Each penalty is bounded below by both
    // costs; the objective minimises their sum, so each settles at the larger one,
    // which is the penalty of the landing time.
    IntVarArgs penalties;
    for (int i = 0; i < n; ++i) {
      int ub = std::max(0, std::max(penalty_before[i] * (target[i] - earliest[i]),
                                    penalty_after[i] * (latest[i] - target[i])));
      IntVar p(*this, 0, ub);
      penalties << p;
      // penalty >= penalty_before * (target - landing), early side
      IntVarArgs early;
      early << p << landing[i];
      linear(*this, IntArgs({1, penalty_before[i]}), early, IRT_GQ, penalty_before[i] * target[i]);
      // penalty >= penalty_after * (landing - target), late side
      linear(*this, IntArgs({1, -penalty_after[i]}), early, IRT_GQ, -penalty_after[i] * target[i]);
    }
    penalty = IntVarArray(*this, penalties);

    // consecutive landings respect the separation: a later aircraft lands at least
    // separation_time[i][j] after an earlier one (i < j, fixed sequence)
    for (int i = 0; i < n; ++i) {
      for (int j = i + 1; j < n; ++j) {
        int gap = separation[i][j].get<int>();
        IntVarArgs pair;
        pair << landing[j] << landing[i];
        linear(*this, IntArgs({1, -1}), pair, IRT_GQ, gap);
      }
    }

    // total penalty is the sum of the penalties of all aircraft
    total = expr(*this, sum(penalties));

    branch(*this, landing, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, penalty, INT_VAR_NONE(), INT_VAL_MIN());
    minimize(total);
    output("landing_times", landing);
    output("total_penalty", total);
  }

  AircraftLanding(AircraftLanding& s) : dcp::Space(s) {
    landing.update(*this, s.landing);
    penalty.update(*this, s.penalty);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new AircraftLanding(*this); }
};

DCP_MODEL(AircraftLanding)
