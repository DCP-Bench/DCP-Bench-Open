// Driver for HiGHS submissions (C++ API).
//
// The submission's build() adds columns and rows to a Highs object. This driver
// sets the options (one thread, no MIP gap, silent, fixed seed), applies the
// declared objective, runs HiGHS, and writes the runner protocol: one "solution"
// record per solution, then one "status" record. The protocol goes to a private
// copy of stdout; the process's own stdout is pointed at stderr, so nothing a
// model or HiGHS prints can reach the protocol.
//
// An optimum counts only when HiGHS reports kOptimal with mip_rel_gap and
// mip_abs_gap at zero. Enumeration pins the objective to the proven optimum and
// adds a binary no-good per solution over the integer columns the declared
// outputs are built from, as the JuMP integration does.
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

#include <unistd.h>

#include "dcp.h"

namespace {

using Clock = std::chrono::steady_clock;

// Integer outputs are rounded when within this distance of an integer.
constexpr double kTolerance = 1e-5;

// The protocol stream, set up in main before anything else runs.
FILE* g_protocol = nullptr;

void Record(const json& record) {
  std::fputs((record.dump() + "\n").c_str(), g_protocol);
  std::fflush(g_protocol);
}

void Status(const std::string& status, double seconds, const std::string& detail = "") {
  Record({{"type", "status"}, {"status", status}, {"solve_seconds", seconds}, {"detail", detail}});
}

void Solution(const json& values) { Record({{"type", "solution"}, {"values", values}}); }

double Seconds(Clock::time_point start) {
  return std::chrono::duration<double>(Clock::now() - start).count();
}

// A problem with the submission or with HiGHS's answer; reported as `error`.
struct SubmissionError : std::runtime_error {
  using std::runtime_error::runtime_error;
};

// What one solve concluded.
enum class Verdict { Solved, Infeasible, Unbounded, InfeasibleOrUnbounded, Timeout };

void Check(HighsStatus status, const std::string& what) {
  if (status != HighsStatus::kOk) throw SubmissionError(what + " failed in HiGHS");
}

// The objective as the driver applies it to HiGHS.
struct Objective {
  bool active = false;
  ObjSense sense = ObjSense::kMinimize;
  std::vector<double> cost;  // per column
  double offset = 0;
};

void ApplyObjective(Highs& h, const Objective& obj) {
  for (std::size_t k = 0; k < obj.cost.size(); ++k)
    Check(h.changeColCost(static_cast<HighsInt>(k), obj.cost[k]), "changeColCost");
  Check(h.changeObjectiveOffset(obj.offset), "changeObjectiveOffset");
  Check(h.changeObjectiveSense(obj.sense), "changeObjectiveSense");
}

// One HiGHS solve within the deadline, with the model status mapped to a verdict.
Verdict Run(Highs& h, Clock::time_point deadline) {
  double left = std::chrono::duration<double>(deadline - Clock::now()).count();
  if (left <= 0.01) return Verdict::Timeout;
  Check(h.setOptionValue("time_limit", left), "setOptionValue(time_limit)");
  if (h.run() == HighsStatus::kError) throw SubmissionError("HiGHS run() returned an error status");
  HighsModelStatus model = h.getModelStatus();
  switch (model) {
    case HighsModelStatus::kOptimal:
      if (h.getInfo().primal_solution_status != kSolutionStatusFeasible)
        throw SubmissionError("HiGHS reports an optimal model without a feasible point");
      return Verdict::Solved;
    case HighsModelStatus::kModelEmpty:
      if (h.getNumCol() > 0) throw SubmissionError("HiGHS reports an empty model with columns");
      return Verdict::Solved;
    case HighsModelStatus::kInfeasible:
      return Verdict::Infeasible;
    case HighsModelStatus::kUnboundedOrInfeasible:
      return Verdict::InfeasibleOrUnbounded;
    case HighsModelStatus::kUnbounded:
      return Verdict::Unbounded;
    case HighsModelStatus::kTimeLimit:
      return Verdict::Timeout;
    case HighsModelStatus::kNotset:
    case HighsModelStatus::kUnknown:
      // HiGHS can stop at the time limit before it sets a status (seen with a 0.2 s limit).
      if (Clock::now() >= deadline - std::chrono::milliseconds(50)) return Verdict::Timeout;
      throw SubmissionError(std::string("HiGHS stopped with model status ") + h.modelStatusToString(model));
    default:
      throw SubmissionError(std::string("HiGHS stopped with model status ") + h.modelStatusToString(model));
  }
}

// Solve with the objective in place. HiGHS reports "infeasible or unbounded" for
// an unbounded MIP; solving again with the objective set aside tells them apart.
Verdict Decide(Highs& h, const Objective& obj, Clock::time_point deadline) {
  Verdict first = Run(h, deadline);
  if (first != Verdict::InfeasibleOrUnbounded) return first;
  if (!obj.active) return Verdict::Infeasible;  // a zero objective cannot be unbounded
  Objective zero = obj;
  std::fill(zero.cost.begin(), zero.cost.end(), 0.0);
  zero.offset = 0;
  ApplyObjective(h, zero);
  Verdict second;
  try {
    second = Run(h, deadline);
  } catch (...) {
    ApplyObjective(h, obj);
    throw;
  }
  ApplyObjective(h, obj);
  switch (second) {
    case Verdict::Solved: return Verdict::Unbounded;
    case Verdict::Infeasible: return Verdict::Infeasible;
    case Verdict::Timeout: return Verdict::Timeout;
    default: throw SubmissionError("HiGHS could not decide between infeasible and unbounded");
  }
}

// Value of an output expression at the solution, rounded to an integer.
long long Evaluate(const dcp::Lin& e, const std::vector<double>& x) {
  double v = e.constant;
  for (const auto& term : e.terms) {
    if (term.first < 0 || static_cast<std::size_t>(term.first) >= x.size())
      throw SubmissionError("output refers to a column that does not exist");
    v += term.second * x[static_cast<std::size_t>(term.first)];
  }
  if (!std::isfinite(v)) throw SubmissionError("an output value is not finite");
  double rounded = std::round(v);
  if (std::fabs(v - rounded) > kTolerance)
    throw SubmissionError("Declared outputs must be integers; got the value " + std::to_string(v));
  return static_cast<long long>(rounded);  // -0.0 becomes 0
}

json Read(const json& layout, const dcp::Outputs& out, const std::vector<double>& x) {
  if (layout.is_object()) return Evaluate(out.exprs().at(layout["e"].get<std::size_t>()), x);
  json result = json::array();
  for (const auto& item : layout) result.push_back(Read(item, out, x));
  return result;
}

json ReadOutputs(const dcp::Outputs& out, const std::vector<double>& x) {
  json values = json::object();
  for (auto it = out.layout().begin(); it != out.layout().end(); ++it)
    values[it.key()] = Read(it.value(), out, x);
  return values;
}

// Columns that the outputs are built from, with the bounds and integrality a
// no-good needs. Returns the reason when a no-good cannot be built.
struct CutColumn {
  HighsInt index;
  double low, high;
};

std::string CutColumns(const Highs& h, const dcp::Outputs& out, std::vector<CutColumn>& cut) {
  const HighsLp& lp = h.getLp();
  std::set<HighsInt> found;
  for (const auto& e : out.exprs())
    for (const auto& term : e.terms) found.insert(term.first);
  for (HighsInt k : found) {
    auto ks = static_cast<std::size_t>(k);
    bool integer = ks < lp.integrality_.size() && lp.integrality_[ks] == HighsVarType::kInteger;
    if (!integer) return "Enumeration needs integer declared outputs; column " + std::to_string(k) + " is continuous";
    double low = lp.col_lower_[ks], high = lp.col_upper_[ks];
    if (!std::isfinite(low) || !std::isfinite(high))
      return "Enumeration needs bounded declared outputs; column " + std::to_string(k) + " is unbounded";
    cut.push_back({k, low, high});
  }
  return "";
}

// Forbids the assignment `x` gives the cut columns, with binary indicators and
// big-M bounds taken from the columns' own bounds. False when no indicator can
// be made, i.e. every cut column is fixed.
bool ForbidAssignment(Highs& h, const std::vector<CutColumn>& cut, const std::vector<double>& x) {
  std::vector<dcp::Lin> indicators;
  for (const auto& c : cut) {
    double v = std::round(x[static_cast<std::size_t>(c.index)]);
    dcp::Lin column = dcp::Lin::col(c.index);
    if (v > c.low) {  // below: x + (high - v + 1) * b <= high; b = 1 forces x <= v - 1
      dcp::Lin b = dcp::new_var(h, 0, 1);
      dcp::add_row(h, column + (c.high - v + 1) * b, -kHighsInf, c.high);
      indicators.push_back(b);
    }
    if (v < c.high) {  // above: x - (v + 1 - low) * a >= low; a = 1 forces x >= v + 1
      dcp::Lin a = dcp::new_var(h, 0, 1);
      dcp::add_row(h, column - (v + 1 - c.low) * a, c.low, kHighsInf);
      indicators.push_back(a);
    }
  }
  if (indicators.empty()) return false;
  dcp::Lin any;
  for (const auto& i : indicators) any = any + i;
  dcp::add_row(h, any, 1, kHighsInf);
  return true;
}

void Configure(Highs& h) {
  Check(h.setOptionValue("output_flag", false), "setOptionValue(output_flag)");
  Check(h.setOptionValue("log_to_console", false), "setOptionValue(log_to_console)");
  Check(h.setOptionValue("threads", HighsInt{1}), "setOptionValue(threads)");
  Check(h.setOptionValue("random_seed", HighsInt{0}), "setOptionValue(random_seed)");
  Check(h.setOptionValue("mip_rel_gap", 0.0), "setOptionValue(mip_rel_gap)");
  Check(h.setOptionValue("mip_abs_gap", 0.0), "setOptionValue(mip_abs_gap)");
}

}  // namespace

int main() {
  auto start = Clock::now();
  g_protocol = fdopen(dup(1), "w");
  if (g_protocol == nullptr) return 1;
  dup2(2, 1);
  try {
    json request;
    std::cin >> request;
    double budget = request.at("execution_timeout").get<double>();
    // Finish a little before the runner's own timer so the status is ours.
    auto deadline = start + std::chrono::duration_cast<Clock::duration>(
                                std::chrono::duration<double>(std::max(0.1, budget - 0.3)));
    int limit = request.at("solution_limit");
    if (limit < 1) throw SubmissionError("solution_limit must be positive");

    Highs h;
    Configure(h);
    dcp::Outputs out;
    build(request.at("instance"), h, out);
    Configure(h);  // a submission cannot change the forced options
    if (out.empty()) throw SubmissionError("build registered no outputs");

    // Objective: the driver owns it. Other columns get cost 0.
    const HighsInt n = h.getNumCol();
    for (const auto& e : out.exprs())
      for (const auto& term : e.terms)
        if (term.first < 0 || term.first >= n) throw SubmissionError("output refers to a column that does not exist");
    Objective obj;
    obj.cost.assign(static_cast<std::size_t>(n), 0.0);
    if (out.has_objective()) {
      obj.active = true;
      obj.sense = out.sense() > 0 ? ObjSense::kMinimize : ObjSense::kMaximize;
      obj.offset = out.objective().constant;
      for (const auto& term : out.objective().terms) {
        if (term.first < 0 || term.first >= n) throw SubmissionError("objective refers to a column that does not exist");
        obj.cost[static_cast<std::size_t>(term.first)] += term.second;
      }
    }
    ApplyObjective(h, obj);

    Verdict verdict = Decide(h, obj, deadline);
    if (verdict == Verdict::Infeasible) {
      Status("unsat", Seconds(start));
      return 0;
    }
    if (verdict == Verdict::Unbounded) {
      Status("error", Seconds(start), "The objective is unbounded");
      return 0;
    }
    if (verdict == Verdict::Timeout) {
      Status("timeout", Seconds(start), obj.active ? "Candidate optimum was not proven" : "");
      return 0;
    }

    // Solved: the solution is proven optimal when there is an objective.
    std::vector<double> x = h.getSolution().col_value;
    x.resize(static_cast<std::size_t>(n), 0.0);
    json values = ReadOutputs(out, x);
    if (limit == 1) {
      Solution(values);
      Status("limit", Seconds(start));
      return 0;
    }

    std::vector<CutColumn> cut;
    std::string reason = CutColumns(h, out, cut);
    if (!reason.empty()) {
      Status("unsupported", Seconds(start), reason);
      return 0;
    }
    if (obj.active) {
      // Pin the objective to the proven optimum, within the tolerance.
      double value = out.objective().constant;
      for (const auto& term : out.objective().terms) value += term.second * x[static_cast<std::size_t>(term.first)];
      dcp::Lin pinned = out.objective();
      pinned.constant = 0;
      double best = value - out.objective().constant;
      dcp::add_row(h, pinned, best - kTolerance, best + kTolerance);
    }

    std::set<std::string> seen;
    int count = 0;
    while (true) {
      std::string key = values.dump();
      if (seen.insert(key).second) {
        Solution(values);
        if (++count >= limit) {
          Status("limit", Seconds(start));
          return 0;
        }
      }
      if (!ForbidAssignment(h, cut, x)) {
        Status("complete", Seconds(start));
        return 0;
      }
      verdict = Decide(h, obj, deadline);
      if (verdict == Verdict::Infeasible) {
        Status("complete", Seconds(start));
        return 0;
      }
      if (verdict == Verdict::Unbounded) throw SubmissionError("The objective is unbounded");
      if (verdict == Verdict::Timeout) {
        Status("timeout", Seconds(start));
        return 0;
      }
      x = h.getSolution().col_value;
      x.resize(static_cast<std::size_t>(n), 0.0);
      values = ReadOutputs(out, x);
    }
  } catch (const std::exception& error) {
    Status("error", 0, error.what());
  } catch (...) {
    Status("error", 0, "unknown exception");
  }
  return 0;
}
