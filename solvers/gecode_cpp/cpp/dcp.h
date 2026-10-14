#pragma once
// Header for Gecode submissions. A submission starts with #include "dcp.h",
// defines a class derived from dcp::Space, and ends with DCP_MODEL(Class).
// See skills/gecode-cpp/SKILL.md for the contract.
#include <gecode/int.hh>
#include <gecode/minimodel.hh>
#include <gecode/search.hh>
#include <gecode/set.hh>

#include <nlohmann/json.hpp>

#include <cstddef>
#include <stdexcept>
#include <string>
#include <vector>

using namespace Gecode;
using nlohmann::json;

namespace dcp {

// Base class of every submission. The model's constructor registers its
// outputs and objective; the driver reads them back through the public
// helpers below.
//
// Output layout: each registered name maps to a nested JSON structure whose
// leaves are either {"i": k} (integer variable ints_[k]), {"b": k} (Boolean
// variable bools_[k]) or a plain JSON number (a constant).
class Space : public Gecode::Space {
 public:
  Space() {}

  Space(Space& s)
      : Gecode::Space(s), layout_(s.layout_), sense_(s.sense_), restarts_(s.restarts_) {
    ints_.resize(s.ints_.size());
    for (std::size_t k = 0; k < s.ints_.size(); ++k) ints_[k].update(*this, s.ints_[k]);
    bools_.resize(s.bools_.size());
    for (std::size_t k = 0; k < s.bools_.size(); ++k) bools_[k].update(*this, s.bools_[k]);
    if (sense_ != 0) objective_.update(*this, s.objective_);
  }

  // Post the fallback branching over every registered output and the
  // objective. Called once on the root space before any search.
  void branch_outputs() {
    IntVarArgs all;
    for (const auto& x : ints_) all << x;
    if (sense_ != 0) all << objective_;
    if (all.size() > 0) branch(*this, all, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    BoolVarArgs bools;
    for (const auto& x : bools_) bools << x;
    if (bools.size() > 0) branch(*this, bools, BOOL_VAR_NONE(), BOOL_VAL_MIN());
    // Propagate so the space is stable and can be cloned.
    (void)status();
  }

  // Values of every registered output, keyed by output name. Throws if an
  // output is not assigned, which means the model did not branch on it.
  json values() const {
    json result = json::object();
    for (auto it = layout_.begin(); it != layout_.end(); ++it) result[it.key()] = read(it.value(), it.key());
    return result;
  }

  bool has_objective() const { return sense_ != 0; }

  bool has_outputs() const { return !layout_.empty(); }

  // Objective value of a fixed solution.
  long long objective_value() const {
    if (sense_ == 0) throw std::logic_error("no objective");
    return objective_.val();
  }

  // Restart scale requested by the model, or 0 for plain DFS/BAB.
  unsigned int restart_scale() const { return restarts_; }

  // Post the no-good: at least one registered variable differs from its
  // value in `solution`. An empty set of outputs makes the space fail.
  void forbid(const Space& solution) {
    BoolVarArgs differs;
    for (std::size_t k = 0; k < ints_.size(); ++k) {
      BoolVar b(*this, 0, 1);
      rel(*this, ints_[k], IRT_NQ, solution.ints_[k].val(), b);
      differs << b;
    }
    for (std::size_t k = 0; k < bools_.size(); ++k) {
      BoolVar b(*this, 0, 1);
      rel(*this, bools_[k], IRT_NQ, solution.bools_[k].val(), b);
      differs << b;
    }
    if (differs.size() == 0) {
      this->fail();
      return;
    }
    clause(*this, BOT_OR, differs, BoolVarArgs(), 1);
  }

  // Post objective == value (used to enumerate all optimal solutions).
  void constrain_objective(long long value) {
    if (sense_ == 0) throw std::logic_error("no objective");
    rel(*this, objective_, IRT_EQ, static_cast<int>(value));
  }

  // Gecode calls this on every search node with the incumbent solution. It
  // posts a strict improvement bound on the objective.
  void constrain(const Gecode::Space& best) override {
    if (sense_ == 0) return;
    const Space& incumbent = static_cast<const Space&>(best);
    int bound = incumbent.objective_.val();
    if (sense_ > 0) rel(*this, objective_, IRT_LE, bound - 1);
    else rel(*this, objective_, IRT_GR, bound);
  }

 protected:
  // Register a named output. Registering the same name twice is an error.
  void output(const std::string& name, IntVar x) { add(name, leaf_int(x)); }
  void output(const std::string& name, BoolVar x) { add(name, leaf_bool(x)); }
  void output(const std::string& name, const IntVarArgs& x) { add(name, int_array(x)); }
  void output(const std::string& name, const IntVarArray& x) { add(name, int_array(x)); }
  void output(const std::string& name, const BoolVarArgs& x) { add(name, bool_array(x)); }
  void output(const std::string& name, const BoolVarArray& x) { add(name, bool_array(x)); }
  void output(const std::string& name, const std::vector<IntVarArgs>& x) {
    json rows = json::array();
    for (const auto& row : x) rows.push_back(int_array(row));
    add(name, rows);
  }
  void output(const std::string& name, const std::vector<BoolVarArgs>& x) {
    json rows = json::array();
    for (const auto& row : x) rows.push_back(bool_array(row));
    add(name, rows);
  }
  void output(const std::string& name, const Matrix<IntVarArgs>& x) { add(name, int_matrix(x)); }
  void output(const std::string& name, const Matrix<IntVarArray>& x) { add(name, int_matrix(x)); }
  void output(const std::string& name, int c) { add(name, c); }
  void output(const std::string& name, const std::vector<int>& c) { add(name, json(c)); }

  // Objective; at most one call per model.
  void minimize(IntVar x) { set_objective(x, 1); }
  void maximize(IntVar x) { set_objective(x, -1); }

  // Restart the search with a Luby cutoff of this scale. Completeness is kept
  // because the cutoff grows without bound.
  void restarts(unsigned int scale) { restarts_ = scale; }

 private:
  void add(const std::string& name, json layout) {
    if (layout_.contains(name)) throw std::logic_error("output " + name + " is registered twice");
    layout_[name] = std::move(layout);
  }

  void set_objective(IntVar x, int sense) {
    if (sense_ != 0) throw std::logic_error("objective is already set");
    objective_ = x;
    sense_ = sense;
  }

  json leaf_int(IntVar x) {
    ints_.push_back(x);
    return json{{"i", ints_.size() - 1}};
  }

  json leaf_bool(BoolVar x) {
    bools_.push_back(x);
    return json{{"b", bools_.size() - 1}};
  }

  template <class Array>
  json int_array(const Array& x) {
    json result = json::array();
    for (int i = 0; i < x.size(); ++i) result.push_back(leaf_int(x[i]));
    return result;
  }

  template <class Array>
  json bool_array(const Array& x) {
    json result = json::array();
    for (int i = 0; i < x.size(); ++i) result.push_back(leaf_bool(x[i]));
    return result;
  }

  // Outer index is the row, so the nested list reads row by row.
  template <class Mat>
  json int_matrix(const Mat& m) {
    json rows = json::array();
    for (int r = 0; r < m.height(); ++r) {
      json row = json::array();
      for (int c = 0; c < m.width(); ++c) row.push_back(leaf_int(m(c, r)));
      rows.push_back(row);
    }
    return rows;
  }

  json read(const json& layout, const std::string& name) const {
    if (layout.is_object()) {
      if (layout.contains("i")) {
        const IntVar& x = ints_.at(layout["i"].get<std::size_t>());
        if (!x.assigned()) throw std::runtime_error("output " + name + " is not assigned: branch on it");
        return x.val();
      }
      const BoolVar& x = bools_.at(layout["b"].get<std::size_t>());
      if (!x.assigned()) throw std::runtime_error("output " + name + " is not assigned: branch on it");
      return x.val();
    }
    if (layout.is_array()) {
      json result = json::array();
      for (const auto& item : layout) result.push_back(read(item, name));
      return result;
    }
    return layout;
  }

  std::vector<IntVar> ints_;
  std::vector<BoolVar> bools_;
  json layout_ = json::object();
  IntVar objective_;
  int sense_ = 0;  // 0 none, 1 minimize, -1 maximize
  unsigned int restarts_ = 0;
};

}  // namespace dcp

// The submission defines this. It returns a freshly constructed model.
dcp::Space* dcp_make(const json& instance);

#define DCP_MODEL(M) \
  dcp::Space* dcp_make(const json& instance) { return new M(instance); }
