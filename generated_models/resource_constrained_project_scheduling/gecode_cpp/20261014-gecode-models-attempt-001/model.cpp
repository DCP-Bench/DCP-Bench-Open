#include "dcp.h"

// Resource-constrained project scheduling: every job runs once, without interruption,
// for its duration; a job starts only after all of its predecessors have finished; at
// any moment the jobs running use at most each resource's capacity. Minimise the
// makespan (the time the last job finishes). Start times are integers from 0.
class ProjectScheduling : public dcp::Space {
 protected:
  IntVarArray start;   // start[j]: start time of job j
  IntVar makespan;     // latest finish time over all jobs

 public:
  explicit ProjectScheduling(const json& instance) {
    std::vector<int> duration = instance.at("durations_data");
    std::vector<int> capacity = instance.at("resource_capacities_data");
    std::vector<std::vector<int>> need = instance.at("resource_needs_data");   // need[j][r]
    std::vector<std::vector<int>> links = instance.at("successors_link_data"); // [pred, succ]
    int jobs = duration.size(), resources = capacity.size();

    // a schedule that runs the jobs one after another fits in the sum of the durations
    int horizon = 0;
    for (int d : duration) horizon += d;

    start = IntVarArray(*this, jobs, 0, horizon);
    makespan = IntVar(*this, 0, horizon);

    // a job starts only when each of its predecessors has finished
    for (const auto& link : links) {
      int pred = link[0], succ = link[1];
      rel(*this, start[pred] + duration[pred] <= start[succ]);
    }

    // each resource: the jobs running at any time use at most its capacity
    for (int r = 0; r < resources; ++r) {
      IntArgs use(jobs);
      for (int j = 0; j < jobs; ++j) use[j] = need[j][r];
      cumulative(*this, capacity[r], start, IntArgs(duration), use);
    }

    // the makespan is the latest finish time
    IntVarArgs finish;
    for (int j = 0; j < jobs; ++j) finish << expr(*this, start[j] + duration[j]);
    max(*this, finish, makespan);

    restarts(100);
    branch(*this, start, INT_VAR_AFC_SIZE_MAX(0.99), INT_VAL_MIN());
    branch(*this, makespan, INT_VAL_MIN());
    minimize(makespan);
    output("start_time", start);
  }

  ProjectScheduling(ProjectScheduling& s) : dcp::Space(s) {
    start.update(*this, s.start);
    makespan.update(*this, s.makespan);
  }
  Gecode::Space* copy() override { return new ProjectScheduling(*this); }
};

DCP_MODEL(ProjectScheduling)
