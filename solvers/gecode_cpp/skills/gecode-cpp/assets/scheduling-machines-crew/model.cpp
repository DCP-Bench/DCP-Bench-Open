// Parallel machines with a shared crew: every task runs once, without interruption,
// on one of the identical machines, not before its release time; a machine runs one
// task at a time; the tasks running at any moment need at most crew_size workers.
// Minimise the time the last task ends.
// Shows optional unary (one per machine), cumulative, max, value precedence for
// interchangeable machines, and branch and bound with Luby restarts.
#include <gecode/int.hh>
#include <gecode/minimodel.hh>
#include <gecode/search.hh>
#include <algorithm>
#include <iostream>
#include <vector>
using namespace Gecode;

const int kMachines = 2, kCrewSize = 3;
const std::vector<int> kDuration = {3, 2, 4, 2, 3, 1};
const std::vector<int> kCrew = {2, 1, 2, 1, 1, 2};
const std::vector<int> kRelease = {0, 0, 1, 2, 3, 0};

class Machines : public IntMinimizeSpace {
 protected:
  IntVarArray start, machine;
  IntVar makespan;

 public:
  Machines() {
    int tasks = kDuration.size();
    int horizon = 0;
    for (int t = 0; t < tasks; ++t) horizon = std::max(horizon, kRelease[t]) + kDuration[t];
    start = IntVarArray(*this, tasks, 0, horizon);
    machine = IntVarArray(*this, tasks, 0, kMachines - 1);
    makespan = IntVar(*this, 0, horizon);

    // a task starts no earlier than its release time
    for (int t = 0; t < tasks; ++t) rel(*this, start[t] >= kRelease[t]);

    // a machine runs one task at a time: task t is on machine k when on[k][t]
    std::vector<BoolVarArgs> on(kMachines, BoolVarArgs(tasks));
    for (int t = 0; t < tasks; ++t) {
      BoolVarArgs choice(kMachines);
      for (int k = 0; k < kMachines; ++k) choice[k] = on[k][t] = BoolVar(*this, 0, 1);
      channel(*this, choice, machine[t]);  // exactly one machine per task
    }
    for (int k = 0; k < kMachines; ++k) unary(*this, start, IntArgs(kDuration), on[k]);

    // the crew is shared: at most kCrewSize workers busy at any time
    cumulative(*this, kCrewSize, start, IntArgs(kDuration), IntArgs(kCrew));

    // the makespan is the latest end
    IntVarArgs end;
    for (int t = 0; t < tasks; ++t) end << expr(*this, start[t] + kDuration[t]);
    max(*this, end, makespan);

    // identical machines: machine k+1 is used only after machine k
    precede(*this, machine, IntArgs::create(kMachines, 0));

    branch(*this, start, INT_VAR_MIN_MIN(), INT_VAL_MIN());
    branch(*this, machine, INT_VAR_NONE(), INT_VAL_MIN());
  }
  Machines(Machines& s) : IntMinimizeSpace(s) {
    start.update(*this, s.start);
    machine.update(*this, s.machine);
    makespan.update(*this, s.makespan);
  }
  Space* copy() override { return new Machines(*this); }
  IntVar cost() const override { return makespan; }
  void print() const {
    std::cout << "Makespan: " << makespan.val() << "\n";
    for (int t = 0; t < start.size(); ++t)
      std::cout << "  task " << t << ": machine " << machine[t].val() << ", start " << start[t].val() << "\n";
  }
};

int main() {
  Search::Options opts;
  opts.cutoff = Search::Cutoff::luby(100);  // restart scale; still complete
  Machines* root = new Machines;
  RBS<Machines, BAB> engine(root, opts);
  delete root;
  Machines* best = nullptr;
  while (Machines* s = engine.next()) {
    delete best;
    best = s;
  }
  if (best == nullptr) {
    std::cout << (engine.stopped() ? "Stopped, no schedule" : "No schedule") << "\n";
    return 0;
  }
  best->print();
  if (engine.stopped()) std::cout << "(not proven optimal)\n";
  delete best;
  return 0;
}
