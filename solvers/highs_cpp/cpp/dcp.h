#pragma once
// Header for HiGHS submissions. A submission starts with #include "dcp.h" and
// defines
//
//     void build(const json& instance, Highs& h, dcp::Outputs& out);
//
// It adds columns and rows to `h` with the HiGHS C++ API, registers its declared
// outputs and its objective on `out`, and returns. The driver (driver.cpp) sets
// the options, solves, proves the optimum and enumerates.
#include <cstddef>
#include <cmath>
#include <map>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include <nlohmann/json.hpp>

#include "Highs.h"

using nlohmann::json;

namespace dcp {

// An affine expression over HiGHS columns: constant + sum of coefficient * column.
// A number converts to a constant; Lin::col(k) is column k (HighsInt index).
struct Lin {
  std::vector<std::pair<HighsInt, double>> terms;
  double constant = 0;

  Lin() {}
  Lin(double c) : constant(c) {}  // implicit: 3 and 2.5 are constants
  static Lin col(HighsInt k) {
    Lin e;
    e.terms.push_back({k, 1.0});
    return e;
  }
};

inline Lin operator+(Lin a, const Lin& b) {
  a.constant += b.constant;
  a.terms.insert(a.terms.end(), b.terms.begin(), b.terms.end());
  return a;
}
inline Lin operator*(double c, Lin a) {
  a.constant *= c;
  for (auto& term : a.terms) term.second *= c;
  return a;
}
inline Lin operator*(Lin a, double c) { return c * a; }
inline Lin operator-(Lin a, const Lin& b) { return a + (-1.0) * b; }
inline Lin operator-(const Lin& a) { return (-1.0) * a; }

// Adds a column with bounds [lower, upper] (use -kHighsInf / kHighsInf for none) and
// returns it as an expression. Integer columns get HiGHS integrality.
inline Lin new_var(Highs& h, double lower, double upper, bool integer = true) {
  HighsInt k = h.getNumCol();
  if (h.addVar(lower, upper) != HighsStatus::kOk) throw std::runtime_error("HiGHS addVar failed");
  if (integer && h.changeColIntegrality(k, HighsVarType::kInteger) != HighsStatus::kOk)
    throw std::runtime_error("HiGHS changeColIntegrality failed");
  return Lin::col(k);
}

// Adds the row lower <= expression <= upper. The expression's constant moves to the bounds.
inline void add_row(Highs& h, const Lin& e, double lower, double upper) {
  std::map<HighsInt, double> merged;
  for (const auto& term : e.terms) merged[term.first] += term.second;
  std::vector<HighsInt> index;
  std::vector<double> value;
  for (const auto& kv : merged) {
    if (kv.second == 0) continue;
    index.push_back(kv.first);
    value.push_back(kv.second);
  }
  double shift = e.constant;
  double lo = lower == -kHighsInf ? -kHighsInf : lower - shift;
  double hi = upper == kHighsInf ? kHighsInf : upper - shift;
  if (h.addRow(lo, hi, static_cast<HighsInt>(index.size()), index.data(), value.data()) != HighsStatus::kOk)
    throw std::runtime_error("HiGHS addRow failed");
}

// Declared outputs and the objective. Each output name maps to a number, a Lin
// (an integer-valued expression over columns), or a nested std::vector of these.
class Outputs {
 public:
  void add(const std::string& name, const Lin& value) {
    if (layout_.contains(name)) throw std::logic_error("output " + name + " is registered twice");
    exprs_.push_back(value);
    json leaf = json::object();
    leaf["e"] = exprs_.size() - 1;
    layout_[name] = leaf;
  }

  template <class T>
  void add(const std::string& name, const std::vector<T>& values) {
    if (layout_.contains(name)) throw std::logic_error("output " + name + " is registered twice");
    layout_[name] = nested(values);
  }

  // The objective, minimised or maximised. At most one call.
  void minimize(const Lin& e) { set_objective(e, 1); }
  void maximize(const Lin& e) { set_objective(e, -1); }

  // ---- used by the driver ----
  bool empty() const { return layout_.empty(); }
  bool has_objective() const { return sense_ != 0; }
  int sense() const { return sense_; }  // 1 minimise, -1 maximise, 0 none
  const Lin& objective() const { return objective_; }
  const std::vector<Lin>& exprs() const { return exprs_; }
  const json& layout() const { return layout_; }

 private:
  template <class T>
  json nested(const std::vector<T>& values) {
    json array = json::array();
    for (const auto& v : values) array.push_back(nested(v));
    return array;
  }
  json nested(const Lin& e) {
    exprs_.push_back(e);
    json leaf = json::object();
    leaf["e"] = exprs_.size() - 1;
    return leaf;
  }

  void set_objective(const Lin& e, int sense) {
    if (sense_ != 0) throw std::logic_error("objective is already set");
    objective_ = e;
    sense_ = sense;
  }

  json layout_ = json::object();
  std::vector<Lin> exprs_;
  Lin objective_;
  int sense_ = 0;
};

}  // namespace dcp

// Defined by the submission.
void build(const json& instance, Highs& h, dcp::Outputs& out);
