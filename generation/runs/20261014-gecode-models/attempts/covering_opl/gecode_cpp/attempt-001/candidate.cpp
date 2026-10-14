#include "dcp.h"

// Covering (set covering with hiring costs): select a set of workers to perform
// all the tasks, minimising the total hiring cost. Each worker is a Boolean
// (hired or not); each task needs at least one hired qualified worker.
class CoveringOpl : public dcp::Space {
 protected:
  BoolVarArray hire;  // hire[w]: worker w+1 is hired
  IntVar total;       // total hiring cost

 public:
  explicit CoveringOpl(const json& instance) {
    int nb_workers = instance.at("nb_workers").get<int>();
    std::vector<int> cost = instance.at("Cost").get<std::vector<int>>();
    const json& qualified = instance.at("Qualified");

    int cost_sum = 0;
    for (int c : cost) cost_sum += c;

    hire = BoolVarArray(*this, nb_workers, 0, 1);
    total = IntVar(*this, 0, cost_sum);

    // every task is performed by at least one hired worker qualified for it
    for (const auto& workers_for_task : qualified) {
      BoolVarArgs cover;
      for (const auto& w : workers_for_task) cover << hire[w.get<int>() - 1];  // workers are 1-based
      linear(*this, cover, IRT_GQ, 1);
    }

    // total hiring cost of the selected workers
    linear(*this, IntArgs(cost), hire, IRT_EQ, total);

    branch(*this, hire, BOOL_VAR_NONE(), BOOL_VAL_MIN());
    minimize(total);
    output("total_cost", total);
    output("workers", hire);
  }

  CoveringOpl(CoveringOpl& s) : dcp::Space(s) {
    hire.update(*this, s.hire);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new CoveringOpl(*this); }
};

DCP_MODEL(CoveringOpl)
