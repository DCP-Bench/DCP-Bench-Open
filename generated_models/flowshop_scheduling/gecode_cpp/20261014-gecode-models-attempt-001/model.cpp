#include "dcp.h"

// Permutation flow shop: n jobs go through machines 1..M in the same order, and
// every machine processes one job at a time. All jobs follow the same sequence.
// Find the job sequence that minimises the makespan, the time the last job
// finishes on the last machine.
class FlowShop : public dcp::Space {
 protected:
  int n;             // number of jobs
  int m;             // number of machines
  IntVarArray seq;   // seq[k]: job (0-based) in position k of the sequence
  IntVarArray done;  // done[k*m + i]: completion time of position k on machine i
  IntVar makespan;   // completion time of the last position on the last machine

 public:
  explicit FlowShop(const json& instance) {
    n = instance.at("jobs").size();
    m = instance.at("machines").size();
    const auto& times = instance.at("process_time");

    // processing time of job j on machine i, one column per machine
    std::vector<std::vector<int>> column(m, std::vector<int>(n));
    int horizon = 0;  // all work done in sequence bounds every completion time
    for (int j = 0; j < n; ++j) {
      for (int i = 0; i < m; ++i) {
        column[i][j] = times[j][i].get<int>();
        horizon += column[i][j];
      }
    }

    seq = IntVarArray(*this, n, 0, n - 1);
    done = IntVarArray(*this, n * m, 0, horizon);

    // the sequence visits every job exactly once
    distinct(*this, seq, IPL_DOM);

    for (int k = 0; k < n; ++k) {
      for (int i = 0; i < m; ++i) {
        // processing time of the job in position k on machine i
        IntVar p = expr(*this, element(IntArgs(column[i]), seq[k]));
        IntVar c = done[k * m + i];

        // a job starts on machine i only after it has finished on machine i-1
        if (i > 0) rel(*this, done[k * m + i - 1] + p <= c);
        // a machine starts the job in position k only after position k-1 is finished
        if (k > 0) rel(*this, done[(k - 1) * m + i] + p <= c);
        // the first job starts on the first machine at time 0
        if (i == 0 && k == 0) rel(*this, p <= c);
      }
    }

    makespan = done[n * m - 1];

    branch(*this, seq, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, done, INT_VAR_NONE(), INT_VAL_MIN());
    minimize(makespan);
    output("makespan", makespan);
  }

  FlowShop(FlowShop& s) : dcp::Space(s), n(s.n), m(s.m) {
    seq.update(*this, s.seq);
    done.update(*this, s.done);
    makespan.update(*this, s.makespan);
  }
  Gecode::Space* copy() override { return new FlowShop(*this); }
};

DCP_MODEL(FlowShop)
