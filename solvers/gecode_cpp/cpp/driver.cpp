// Driver for Gecode submissions.
//
// Gecode has no process-wide state, so every search runs in this process on
// a single thread. The search engines are given the time left before the
// deadline through a TimeStop. Protocol records match the chuffed driver:
// one "solution" line per solution, then one "status" line.
#include <algorithm>
#include <chrono>
#include <cstdio>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

#include "dcp.h"

namespace {

using Clock = std::chrono::steady_clock;

enum class Outcome { Limit, Exhausted, Timeout };

// Solutions found so far, with their values in the same order.
struct Pool {
  std::vector<std::unique_ptr<dcp::Space>> spaces;
  std::vector<json> values;
};

double Seconds(Clock::time_point start) {
  return std::chrono::duration<double>(Clock::now() - start).count();
}

long long Millis(Clock::time_point deadline) {
  return std::chrono::duration_cast<std::chrono::milliseconds>(deadline - Clock::now()).count();
}

void Status(const std::string& status, double seconds, const std::string& detail = "") {
  std::cout << json({{"type", "status"}, {"status", status}, {"solve_seconds", seconds}, {"detail", detail}}).dump()
            << std::endl;
}

void Solution(const json& values) {
  std::cout << json({{"type", "solution"}, {"values", values}}).dump() << std::endl;
}

// Outputs and the objective are assigned by values() and by the fallback
// branching. A propagator still pending at a solution is only noted on
// stderr: some globals stay alive with all variables fixed, and the
// evaluator checks every solution against the reference anyway.
void CheckSolved(dcp::Space& solution) {
  long long pending = PropagatorGroup::all.size(solution);
  if (pending > 0) std::cerr << "note: " << pending << " propagators not subsumed at solution\n";
}

// Enumerate distinct solutions (distinct on the declared outputs) of a
// constrained root, appending them to the pool until the limit is reached.
Outcome Enumerate(dcp::Space* root, int limit, Clock::time_point deadline, Pool& pool) {
  unsigned int scale = root->restart_scale();
  (void)root->status();  // propagate any constraint posted since the last clone
  while (true) {
    if (static_cast<int>(pool.values.size()) >= limit) return Outcome::Limit;
    long long ms = Millis(deadline);
    if (ms <= 0) return Outcome::Timeout;
    std::unique_ptr<dcp::Space> copy(static_cast<dcp::Space*>(root->clone()));
    for (const auto& found : pool.spaces) copy->forbid(*found);

    Search::Options options;
    options.threads = 1;
    Search::TimeStop stop(static_cast<unsigned long int>(ms));
    options.stop = &stop;
    std::unique_ptr<dcp::Space> solution;
    bool stopped = false;
    if (scale > 0) {
      options.cutoff = Search::Cutoff::luby(scale);
      RBS<dcp::Space, DFS> engine(copy.get(), options);
      solution.reset(engine.next());
      stopped = engine.stopped();
    } else {
      DFS<dcp::Space> engine(copy.get(), options);
      solution.reset(engine.next());
      stopped = engine.stopped();
    }
    if (!solution) return stopped ? Outcome::Timeout : Outcome::Exhausted;
    CheckSolved(*solution);
    pool.values.push_back(solution->values());
    pool.spaces.push_back(std::move(solution));
  }
}

void Finish(Outcome outcome, const Pool& pool, double seconds) {
  for (const auto& values : pool.values) Solution(values);
  switch (outcome) {
    case Outcome::Limit: Status("limit", seconds); break;
    case Outcome::Timeout: Status("timeout", seconds); break;
    case Outcome::Exhausted: Status(pool.values.empty() ? "unsat" : "complete", seconds); break;
  }
}

}  // namespace

int main() {
  auto start = Clock::now();
  try {
    json request;
    std::cin >> request;
    double budget = request.at("execution_timeout").get<double>();
    // Finish a little before the runner's own timer so the status is ours.
    auto deadline = start + std::chrono::duration_cast<Clock::duration>(
                                std::chrono::duration<double>(std::max(0.1, budget - 0.3)));
    int limit = request.at("solution_limit");
    if (limit < 1) throw std::runtime_error("solution_limit must be positive");

    std::unique_ptr<dcp::Space> root(dcp_make(request.at("instance")));
    if (!root->has_outputs()) throw std::runtime_error("Expected output dictionary");
    if (root->status() == SS_FAILED) {
      Status("unsat", Seconds(start));
      return 0;
    }
    root->branch_outputs();

    if (!root->has_objective()) {
      Pool pool;
      Outcome outcome = Enumerate(root.get(), limit, deadline, pool);
      Finish(outcome, pool, Seconds(start));
      return 0;
    }

    // Optimization: a branch-and-bound search on a clone of the root. The
    // last solution is optimal only if the search finished without a stop.
    Search::Options options;
    options.threads = 1;
    Search::TimeStop stop(static_cast<unsigned long int>(std::max(1LL, Millis(deadline))));
    options.stop = &stop;
    std::unique_ptr<dcp::Space> last;
    bool stopped = false;
    auto improve = [&](auto& engine) {
      while (true) {
        dcp::Space* solution = engine.next();
        if (solution == nullptr) break;
        last.reset(solution);
      }
      stopped = engine.stopped();
    };
    std::unique_ptr<dcp::Space> bab_root(static_cast<dcp::Space*>(root->clone()));
    if (root->restart_scale() > 0) {
      options.cutoff = Search::Cutoff::luby(root->restart_scale());
      RBS<dcp::Space, BAB> engine(bab_root.get(), options);
      improve(engine);
    } else {
      BAB<dcp::Space> engine(bab_root.get(), options);
      improve(engine);
    }
    if (stopped) {
      Status("timeout", Seconds(start));
      return 0;
    }
    if (!last) {
      Status("unsat", Seconds(start));
      return 0;
    }
    CheckSolved(*last);

    Pool pool;
    long long best = last->objective_value();
    pool.values.push_back(last->values());
    pool.spaces.push_back(std::move(last));
    if (limit == 1) {
      Finish(Outcome::Limit, pool, Seconds(start));
      return 0;
    }

    // Enumerate the other optimal solutions: the objective is fixed to the
    // optimum, and the optimum itself is excluded by the no-goods.
    std::unique_ptr<dcp::Space> optimal(static_cast<dcp::Space*>(root->clone()));
    optimal->constrain_objective(best);
    Outcome outcome = Enumerate(optimal.get(), limit, deadline, pool);
    Finish(outcome, pool, Seconds(start));
  } catch (const std::exception& error) {
    Status("error", 0, error.what());
  } catch (...) {
    Status("error", 0, "unknown exception");
  }
  return 0;
}
