#include "dcp.h"

// Job shop scheduling: several jobs, each a fixed sequence of tasks, each task
// run on one specific machine. Schedule all tasks so the makespan (the time
// until all jobs are complete) is as small as possible.
class JobShop : public dcp::Space {
 protected:
  IntVarArray start;  // start[t]: start time of task t (tasks numbered job by job, in job order)
  IntVar makespan;    // time at which the last task completes

 public:
  explicit JobShop(const json& instance) {
    // read the jobs: each job is a list of [machine, duration] tasks in order
    const json& jobs = instance.at("jobs_data");
    std::vector<int> dur;                  // dur[t]: duration of task t
    std::vector<int> mach;                 // mach[t]: machine of task t
    std::vector<std::vector<int>> job_tasks;  // job_tasks[j]: task numbers of job j, in order
    int horizon = 0;                       // sum of all durations, an upper bound on the makespan
    int num_machines = 0;
    for (const auto& job : jobs) {
      std::vector<int> tasks;
      for (const auto& task : job) {
        int m = task[0].get<int>();
        int d = task[1].get<int>();
        tasks.push_back(static_cast<int>(dur.size()));
        dur.push_back(d);
        mach.push_back(m);
        horizon += d;
        if (m + 1 > num_machines) num_machines = m + 1;
      }
      job_tasks.push_back(tasks);
    }
    int T = static_cast<int>(dur.size());
    start = IntVarArray(*this, T, 0, horizon);

    // no task of a job starts until the previous task of that job is completed
    for (const auto& tasks : job_tasks)
      for (std::size_t k = 0; k + 1 < tasks.size(); ++k) {
        int a = tasks[k];
        int b = tasks[k + 1];
        rel(*this, start[a] + dur[a] <= start[b]);
      }

    // a machine can only work on one task at a time (each task runs to completion
    // once started, since its duration is fixed)
    for (int m = 0; m < num_machines; ++m) {
      std::vector<int> on_machine;
      for (int t = 0; t < T; ++t)
        if (mach[t] == m) on_machine.push_back(t);
      if (on_machine.empty()) continue;
      IntVarArgs s;
      IntArgs d(static_cast<int>(on_machine.size()));
      for (std::size_t i = 0; i < on_machine.size(); ++i) {
        s << start[on_machine[i]];
        d[static_cast<int>(i)] = dur[on_machine[i]];
      }
      unary(*this, s, d);
    }

    // the makespan is the completion time of the last task of all jobs
    IntVarArgs ends;
    for (int t = 0; t < T; ++t) ends << expr(*this, start[t] + dur[t]);
    makespan = IntVar(*this, 0, horizon);
    max(*this, ends, makespan);

    // branch on the start times: Luby restarts with activity-based variable choice,
    // then split the domain of the chosen start time
    restarts(100);
    branch(*this, start, INT_VAR_AFC_SIZE_MAX(0.99), INT_VAL_SPLIT_MIN());
    minimize(makespan);
    output("makespan", makespan);
  }

  JobShop(JobShop& s) : dcp::Space(s) {
    start.update(*this, s.start);
    makespan.update(*this, s.makespan);
  }
  Gecode::Space* copy() override { return new JobShop(*this); }
};

DCP_MODEL(JobShop)
