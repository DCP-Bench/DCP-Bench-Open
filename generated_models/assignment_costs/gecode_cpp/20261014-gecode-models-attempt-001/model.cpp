#include "dcp.h"

// Assignment: give each task to one person so that the total cost is minimal.
// Each task is assigned to exactly one person; a person takes at most one task.
class AssignmentCosts : public dcp::Space {
 protected:
  IntVarArray person;  // person[i]: the person doing task i
  IntVarArray cost;    // cost[i]: cost of task i for the person doing it
  IntVar total;        // total cost of the assignment

 public:
  explicit AssignmentCosts(const json& instance) {
    // cost[i][j]: cost of task i when done by person j
    std::vector<std::vector<int>> c = instance.at("cost");
    int tasks = c.size();
    int people = c[0].size();
    int maxc = 0;
    for (const auto& row : c)
      for (int v : row) maxc = std::max(maxc, v);

    person = IntVarArray(*this, tasks, 0, people - 1);
    cost = IntVarArray(*this, tasks, 0, maxc);

    // a person takes at most one task
    distinct(*this, person, IPL_DOM);

    // the cost of a task is the entry for the person who does it
    // x[i][j] is true exactly when person j does task i; this makes each task
    // go to exactly one person
    std::vector<BoolVarArgs> x(tasks);
    for (int i = 0; i < tasks; ++i) {
      IntSharedArray row(IntArgs(c[i]));
      element(*this, row, person[i], cost[i], IPL_DOM);

      for (int j = 0; j < people; ++j) x[i] << BoolVar(*this, 0, 1);
      channel(*this, x[i], person[i], 0, IPL_DOM);
    }

    // total cost is the sum of the costs of the tasks
    IntVarArgs all;
    for (int i = 0; i < tasks; ++i) all << cost[i];
    total = expr(*this, sum(all));

    branch(*this, cost, INT_VAR_REGRET_MIN_MAX(), INT_VAL_MIN());
    branch(*this, person, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    minimize(total);
    output("x", x);
  }

  AssignmentCosts(AssignmentCosts& s) : dcp::Space(s) {
    person.update(*this, s.person);
    cost.update(*this, s.cost);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new AssignmentCosts(*this); }
};

DCP_MODEL(AssignmentCosts)
