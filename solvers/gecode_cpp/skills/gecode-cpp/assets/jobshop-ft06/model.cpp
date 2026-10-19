// Job shop, Fisher and Thompson's 6 x 6 instance ft06: each job visits its machines
// in a fixed order, every machine runs one task at a time, minimise the makespan.
#include <gecode/int.hh>
#include <gecode/minimodel.hh>
#include <gecode/search.hh>
#include <algorithm>
#include <iostream>
#include <utility>
#include <vector>
using namespace Gecode;

// Each job lists (machine, duration) in its processing order.
static const std::vector<std::vector<std::pair<int, int>>> jobs = {
    {{2, 1}, {0, 3}, {1, 6}, {3, 7}, {5, 3}, {4, 6}},
    {{1, 8}, {2, 5}, {4, 10}, {5, 10}, {0, 10}, {3, 4}},
    {{2, 5}, {3, 4}, {5, 8}, {0, 9}, {1, 1}, {4, 7}},
    {{1, 5}, {0, 5}, {2, 5}, {3, 3}, {4, 8}, {5, 9}},
    {{2, 9}, {1, 3}, {4, 5}, {5, 4}, {0, 3}, {3, 1}},
    {{1, 3}, {3, 3}, {5, 9}, {0, 10}, {4, 4}, {2, 1}},
};

class JobShop : public IntMinimizeSpace {
 protected:
  std::vector<int> machine, duration;  // per task; tasks numbered job by job
  IntVarArray start;                   // start[t]: start time of task t
  IntVar makespan;

 public:
  JobShop() {
    int horizon = 0;
    for (const auto& job : jobs)
      for (const auto& [m, d] : job) {
        machine.push_back(m);
        duration.push_back(d);
        horizon += d;
      }
    int tasks = duration.size();
    int machines = 0;
    for (int m : machine) machines = std::max(machines, m + 1);
    start = IntVarArray(*this, tasks, 0, horizon);
    makespan = IntVar(*this, 0, horizon);

    // the tasks of a job run in order: each ends before the next one starts
    int t = 0;
    for (const auto& job : jobs) {
      for (size_t k = 0; k + 1 < job.size(); ++k)
        rel(*this, start[t + k] + duration[t + k] <= start[t + k + 1]);
      t += job.size();
    }

    // a machine runs one task at a time
    for (int m = 0; m < machines; ++m) {
      IntVarArgs s;
      IntArgs d;
      for (int i = 0; i < tasks; ++i)
        if (machine[i] == m) {
          s << start[i];
          d << duration[i];
        }
      unary(*this, s, d);
    }

    // the makespan is the latest end
    IntVarArgs ends;
    for (int i = 0; i < tasks; ++i) ends << expr(*this, start[i] + duration[i]);
    max(*this, ends, makespan);

    branch(*this, start, INT_VAR_MIN_MIN(), INT_VAL_MIN());
  }
  JobShop(JobShop& s)
      : IntMinimizeSpace(s), machine(s.machine), duration(s.duration) {
    start.update(*this, s.start);
    makespan.update(*this, s.makespan);
  }
  Space* copy() override { return new JobShop(*this); }
  IntVar cost() const override { return makespan; }
  void print() const { std::cout << "Makespan: " << makespan.val() << "\n"; }
};

int main() {
  JobShop* root = new JobShop;
  BAB<JobShop> engine(root);
  delete root;
  JobShop* best = nullptr;
  while (JobShop* s = engine.next()) {  // each solution is strictly shorter
    delete best;
    best = s;
  }
  if (best == nullptr) {
    std::cout << (engine.stopped() ? "Limit reached before a schedule was found\n" : "No schedule\n");
    return 0;
  }
  best->print();
  if (engine.stopped()) std::cout << "(not proven optimal)\n";
  delete best;
  return 0;
}
