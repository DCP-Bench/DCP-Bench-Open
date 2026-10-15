# DCP-Bench examples for gecode_cpp

Two complete submissions for invented problems, each run through the gecode_cpp
driver in the image on the instance shown. They show globals working together:
a matrix with gcc, a regular expression and table costs; optional unary resources, a
cumulative crew, value precedence and restarts.

## Shift roster: Matrix, gcc, REG, count, element, minimise

Instance: `{"workers": 4, "days": 7, "max_nights": 3, "demand": [[1,1],[1,1],[2,1],[1,1],[1,1],[1,0],[0,1]], "cost": [[3,5],[4,4],[2,6],[5,3]]}`.
Proven optimum 36 in 0.1 s.

```cpp
#include "dcp.h"

// Shift roster: give every worker a shift (0 off, 1 day, 2 night) on every day so
// that each day's demand is met, no one works a day shift right after a night,
// nights come in runs of at most two, and the total cost of the roster is minimal.
class Roster : public dcp::Space {
 protected:
  IntVarArray shift;  // workers x days, row-major: shift[w * days + d]
  IntVar total;

 public:
  explicit Roster(const json& instance) {
    int workers = instance.at("workers"), days = instance.at("days");
    int max_nights = instance.at("max_nights");
    shift = IntVarArray(*this, workers * days, 0, 2);
    Matrix<IntVarArray> m(shift, days, workers);  // m(day, worker)

    // each day needs exactly demand[d] = [day shifts, night shifts]; the rest are off
    for (int d = 0; d < days; ++d) {
      int day = instance.at("demand")[d][0], night = instance.at("demand")[d][1];
      count(*this, m.col(d), IntSetArgs({IntSet(0, workers), IntSet(day, day), IntSet(night, night)}),
            IntArgs({0, 1, 2}));
    }

    // no day shift right after a night, and at most two nights in a row
    REG off(0), early(1), night(2);
    DFA rules(*(off | early | night(1, 2) + off) + night(0, 2));
    for (int w = 0; w < workers; ++w) extensional(*this, m.row(w), rules);

    // a worker has at most max_nights nights in the period
    for (int w = 0; w < workers; ++w) count(*this, m.row(w), 2, IRT_LQ, max_nights);

    // cost[w] = [day shift cost, night shift cost]; minimise the total
    IntVarArgs costs;
    for (int w = 0; w < workers; ++w) {
      IntArgs price({0, instance.at("cost")[w][0].get<int>(), instance.at("cost")[w][1].get<int>()});
      for (int d = 0; d < days; ++d) costs << expr(*this, element(price, m(d, w)));
    }
    total = expr(*this, sum(costs));

    branch(*this, shift, INT_VAR_AFC_SIZE_MAX(0.99), INT_VAL_MIN());
    minimize(total);
    output("roster", m);
    output("total", total);
  }

  Roster(Roster& s) : dcp::Space(s) {
    shift.update(*this, s.shift);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new Roster(*this); }
};

DCP_MODEL(Roster)
```

## Parallel machines with a shared crew: optional unary, cumulative, precede, restarts

Instance: `{"machines": 2, "crew_size": 3, "duration": [3, 2, 4, 2, 3, 1], "crew": [2, 1, 2, 1, 1, 2], "release": [0, 0, 1, 2, 3, 0]}`.
Proven optimum 8 (the work bound) in under 0.01 s.

```cpp
#include "dcp.h"

// Parallel machines with a shared crew: every task runs once, without interruption,
// on one of the identical machines, not before its release time; a machine runs one
// task at a time; the tasks running at any moment need at most crew_size workers.
// Minimise the time the last task ends.
class Machines : public dcp::Space {
 protected:
  IntVarArray start, machine;
  IntVar makespan;

 public:
  explicit Machines(const json& instance) {
    std::vector<int> duration = instance.at("duration"), crew = instance.at("crew"),
                     release = instance.at("release");
    int tasks = duration.size(), machines = instance.at("machines");
    int horizon = 0;
    for (int t = 0; t < tasks; ++t) horizon = std::max(horizon, release[t]) + duration[t];
    start = IntVarArray(*this, tasks, 0, horizon);
    machine = IntVarArray(*this, tasks, 0, machines - 1);
    makespan = IntVar(*this, 0, horizon);

    // a task starts no earlier than its release time
    for (int t = 0; t < tasks; ++t) rel(*this, start[t] >= release[t]);

    // a machine runs one task at a time: task t is on machine k when on[k][t]
    std::vector<BoolVarArgs> on(machines, BoolVarArgs(tasks));
    for (int t = 0; t < tasks; ++t) {
      BoolVarArgs choice(machines);
      for (int k = 0; k < machines; ++k) choice[k] = on[k][t] = BoolVar(*this, 0, 1);
      channel(*this, choice, machine[t]);
    }
    for (int k = 0; k < machines; ++k) unary(*this, start, IntArgs(duration), on[k]);

    // the crew is shared: at most crew_size workers busy at any time
    cumulative(*this, instance.at("crew_size").get<int>(), start, IntArgs(duration), IntArgs(crew));

    // the makespan is the latest end
    IntVarArgs end;
    for (int t = 0; t < tasks; ++t) end << expr(*this, start[t] + duration[t]);
    max(*this, end, makespan);

    // identical machines: machine k+1 is used only after machine k
    precede(*this, machine, IntArgs::create(machines, 0));

    restarts(100);
    branch(*this, start, INT_VAR_MIN_MIN(), INT_VAL_MIN());
    branch(*this, machine, INT_VAR_NONE(), INT_VAL_MIN());
    minimize(makespan);
    output("start", start);
    output("machine", machine);
    output("makespan", makespan);
  }

  Machines(Machines& s) : dcp::Space(s) {
    start.update(*this, s.start);
    machine.update(*this, s.machine);
    makespan.update(*this, s.makespan);
  }
  Gecode::Space* copy() override { return new Machines(*this); }
};

DCP_MODEL(Machines)
```
