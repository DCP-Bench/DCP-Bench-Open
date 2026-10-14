// Driver for Chuffed submissions.
//
// Chuffed keeps its model and solver in process-wide globals (engine, so, sat)
// and cannot be reset, so every solve phase runs in a fork()ed child. The child
// builds the model, solves, and streams solutions as JSON lines through a pipe.
// The parent owns the time budget, deduplicates on the declared outputs and
// prints the protocol records.
#include <poll.h>
#include <signal.h>
#include <sys/wait.h>
#include <unistd.h>

#include <cerrno>
#include <cstdlib>
#include <chrono>
#include <cstdio>
#include <cstring>
#include <iostream>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "dcp.h"
#include "chuffed/core/sat.h"

namespace {
std::vector<IntVar*> g_vars;

void Collect(const json& layout, std::set<int>& used) {
  if (layout.is_object() || layout.is_array()) {
    for (const auto& item : layout) Collect(item, used);
    return;
  }
  if (!layout.is_number_integer()) throw std::runtime_error("Output leaves must be variable indices");
  int index = layout.get<int>();
  if (index < 0 || index >= static_cast<int>(g_vars.size())) throw std::runtime_error("Invalid output variable index");
  used.insert(index);
}

json Read(const json& layout) {
  if (layout.is_object()) {
    json result = json::object();
    for (auto it = layout.begin(); it != layout.end(); ++it) result[it.key()] = Read(it.value());
    return result;
  }
  if (layout.is_array()) {
    json result = json::array();
    for (const auto& item : layout) result.push_back(Read(item));
    return result;
  }
  return g_vars[layout.get<int>()]->getVal();
}

void WriteLine(int fd, const json& line) {
  std::string text = line.dump() + "\n";
  const char* data = text.data();
  size_t left = text.size();
  while (left > 0) {
    ssize_t n = write(fd, data, left);
    if (n < 0) {
      if (errno == EINTR) continue;
      _exit(3);
    }
    data += n;
    left -= static_cast<size_t>(n);
  }
}

int g_fd = -1;

// Chuffed calls exit(0) when posting a constraint fails at the root (TL_FAIL).
// That is a proof of unsatisfiability, so report it as a finished search.
void OnExit() {
  if (g_fd < 0) return;
  std::string text = "{\"end\":\"finished\",\"objective\":false,\"solutions\":0}\n";
  ssize_t ignored = write(g_fd, text.data(), text.size());
  (void)ignored;
}

class DriverProblem : public Problem {
 public:
  void print(std::ostream&) override {}
};

// Runs in the forked child. Phase 1 solves the model as built; phase 2 (only
// for optimization) fixes the objective to `best` and enumerates.
void Child(int fd, const json& request, int phase, long long best, int limit, double seconds) {
  try {
    g_fd = fd;
    std::atexit(OnExit);
    dup2(2, 1);  // anything Chuffed prints to stdout must not reach the protocol
    json outputs;
    Build(request.at("instance"), outputs);
    if (!outputs.is_object() || outputs.empty()) throw std::runtime_error("Expected output dictionary");
    std::set<int> used;
    Collect(outputs, used);
    vec<IntVar*> declared;
    for (int index : used) declared.push(g_vars[index]);
    output_vars(declared);

    // Without a search annotation Chuffed would stop at the root with unfixed
    // variables. Search all integer variables after any branching the model
    // declared, then let VSIDS decide whatever Boolean variables remain.
    vec<Branching*> everything;
    for (unsigned i = 0; i < engine.vars.size(); ++i) everything.push(engine.vars[i]);
    engine.branching->add(new BranchGroup(everything, VAR_INORDER, true));
    so.vsids = true;
    engine.branching->add(&sat);

    IntVar* objective = engine.opt_var;
    bool has_objective = objective != nullptr;
    // Announce the objective before solving: if the parent kills this child at
    // the deadline, it must still know that unproven solutions may not be emitted.
    WriteLine(fd, {{"declared", has_objective}});
    if (phase == 2) {
      if (!has_objective) throw std::runtime_error("Objective disappeared between phases");
      int_rel(objective, IRT_EQ, static_cast<int>(best));
      engine.opt_var = nullptr;
      so.nof_solutions = limit + 1;
    } else {
      so.nof_solutions = has_objective ? 0 : limit;
    }
    so.print_sol = false;
    so.time_out = duration(std::max<long long>(1, static_cast<long long>(seconds * 1000)));
    std::stringstream sink;
    engine.setOutputStream(sink);
    engine.setSolutionCallback([&](Problem*) {
      json line = {{"values", Read(outputs)}};
      if (objective != nullptr) line["objective"] = objective->getVal();
      WriteLine(fd, line);
    });
    DriverProblem problem;
    engine.solve(&problem);
    const char* end = engine.status == RES_SAT ? "sat" : engine.status == RES_UNK ? "unknown" : "finished";
    WriteLine(fd, {{"end", end}, {"solutions", engine.solutions}, {"objective", has_objective}});
    g_fd = -1;
    _exit(0);
  } catch (const std::exception& error) {
    try { WriteLine(fd, {{"error", error.what()}}); } catch (...) {}
    _exit(0);
  } catch (...) {
    try { WriteLine(fd, {{"error", "unknown exception"}}); } catch (...) {}
    _exit(0);
  }
}

struct Phase {
  std::vector<json> values;
  std::vector<long long> objectives;
  std::string end;           // sat | finished | unknown | "" when the child never reported
  bool has_objective = false;
  bool timed_out = false;
  std::string error;
};

using Clock = std::chrono::steady_clock;

double Left(Clock::time_point deadline) {
  return std::chrono::duration<double>(deadline - Clock::now()).count();
}

Phase RunPhase(const json& request, int phase, long long best, int limit, Clock::time_point deadline) {
  Phase result;
  int fds[2];
  if (pipe(fds) != 0) throw std::runtime_error("pipe failed");
  std::cout.flush();
  std::cerr.flush();
  pid_t pid = fork();
  if (pid < 0) throw std::runtime_error("fork failed");
  if (pid == 0) {
    close(fds[0]);
    Child(fds[1], request, phase, best, limit, Left(deadline));
    _exit(0);
  }
  close(fds[1]);
  std::string buffer;
  char chunk[65536];
  while (true) {
    double left = Left(deadline);
    if (left <= 0) { result.timed_out = true; break; }
    pollfd waiting{fds[0], POLLIN, 0};
    int ready = poll(&waiting, 1, static_cast<int>(std::min(left * 1000 + 1, 1000.0)));
    if (ready < 0) {
      if (errno == EINTR) continue;
      break;
    }
    if (ready == 0) continue;
    ssize_t n = read(fds[0], chunk, sizeof(chunk));
    if (n < 0) {
      if (errno == EINTR) continue;
      break;
    }
    if (n == 0) break;
    buffer.append(chunk, static_cast<size_t>(n));
  }
  if (result.timed_out) kill(pid, SIGKILL);
  close(fds[0]);
  int wait_status = 0;
  while (waitpid(pid, &wait_status, 0) < 0 && errno == EINTR) {}

  std::istringstream lines(buffer);
  std::string text;
  while (std::getline(lines, text)) {
    if (text.empty()) continue;
    json line;
    try { line = json::parse(text); } catch (...) { continue; }  // a killed child may leave a partial line
    if (line.contains("values")) {
      result.values.push_back(line["values"]);
      result.objectives.push_back(line.contains("objective") ? line["objective"].get<long long>() : 0);
    } else if (line.contains("declared")) {
      result.has_objective = line["declared"].get<bool>();
    } else if (line.contains("end")) {
      result.end = line["end"].get<std::string>();
      result.has_objective = line["objective"].get<bool>();
    } else if (line.contains("error")) {
      result.error = line["error"].get<std::string>();
    }
  }
  if (!result.timed_out && result.end.empty() && result.error.empty()) {
    if (WIFSIGNALED(wait_status)) result.error = "Chuffed process died with signal " + std::to_string(WTERMSIG(wait_status));
    else result.error = "Chuffed process exited without a result (code " + std::to_string(WEXITSTATUS(wait_status)) + ")";
  }
  return result;
}

void Status(const std::string& status, double seconds, const std::string& detail = "") {
  std::cout << json({{"type", "status"}, {"status", status}, {"solve_seconds", seconds}, {"detail", detail}}).dump() << std::endl;
}

void Solution(const json& values) {
  std::cout << json({{"type", "solution"}, {"values", values}}).dump() << std::endl;
}
}  // namespace

namespace dcp {
int out(IntVar* v) {
  if (v == nullptr) throw std::runtime_error("Null output variable");
  g_vars.push_back(v);
  return static_cast<int>(g_vars.size()) - 1;
}
}  // namespace dcp

int main() {
  auto start = Clock::now();
  try {
    json request;
    std::cin >> request;
    double budget = request.at("execution_timeout").get<double>();
    // Finish a little before the runner's own timer so the status is ours.
    auto deadline = start + std::chrono::duration_cast<Clock::duration>(std::chrono::duration<double>(std::max(0.1, budget - 0.3)));
    int limit = request.at("solution_limit");
    if (limit < 1) throw std::runtime_error("solution_limit must be positive");
    auto seconds = [&] { return std::chrono::duration<double>(Clock::now() - start).count(); };

    Phase first = RunPhase(request, 1, 0, limit, deadline);
    if (!first.error.empty()) { Status("error", seconds(), first.error); return 0; }

    if (!first.has_objective) {
      std::set<std::string> seen;
      int count = 0;
      for (const auto& values : first.values) {
        if (!seen.insert(values.dump()).second) continue;
        Solution(values);
        if (++count >= limit) break;
      }
      if (first.timed_out || first.end == "unknown") Status("timeout", seconds());
      else if (count >= limit) Status("limit", seconds());
      else Status(count ? "complete" : "unsat", seconds());
      return 0;
    }

    // Optimization: nothing is emitted until the optimum is proven.
    if (first.timed_out || first.end != "finished") { Status("timeout", seconds()); return 0; }
    if (first.values.empty()) { Status("unsat", seconds()); return 0; }
    json optimum = first.values.back();
    long long best = first.objectives.back();
    Solution(optimum);
    if (limit == 1) { Status("limit", seconds()); return 0; }

    Phase second = RunPhase(request, 2, best, limit, deadline);
    if (!second.error.empty()) { Status("error", seconds(), second.error); return 0; }
    std::set<std::string> seen{optimum.dump()};
    int count = 1;
    for (const auto& values : second.values) {
      if (count >= limit) break;
      if (!seen.insert(values.dump()).second) continue;
      Solution(values);
      ++count;
    }
    if (count >= limit) Status("limit", seconds());
    else if (second.timed_out || second.end != "finished") Status("timeout", seconds());
    else Status("complete", seconds());
  } catch (const std::exception& error) { Status("error", 0, error.what()); }
}
