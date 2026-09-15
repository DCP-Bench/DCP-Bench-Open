#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

namespace {

struct Transition {
  int tail;
  int64_t label;
  int head;
};

// Build the run-length automaton for one line's clue, mirroring the
// reference's transition_function.  Zero entries are padding and are skipped;
// nonzero entries are the block lengths in order.
std::vector<Transition> TransitionFunction(const std::vector<int64_t>& pattern,
                                           std::vector<int>* final_states) {
  std::vector<Transition> func;
  int n_states = 0;
  for (const int64_t block_length : pattern) {
    if (block_length == 0) continue;
    func.push_back({n_states, 0, n_states});
    for (int64_t k = 0; k < block_length; ++k) {
      func.push_back({n_states, 1, n_states + 1});
      ++n_states;
    }
    func.push_back({n_states, 0, n_states + 1});
    ++n_states;
  }
  func.push_back({n_states, 0, n_states});
  // A line may end on the last filled cell or on trailing blanks.  An all-zero
  // clue leaves n_states at 0, so the first of these is -1 and is dropped.
  final_states->clear();
  for (const int state : {n_states - 1, n_states}) {
    if (state >= 0) final_states->push_back(state);
  }
  return func;
}

void AddRunConstraint(CpModelBuilder& model, const std::vector<IntVar>& line,
                      const std::vector<int64_t>& pattern) {
  std::vector<int> final_states;
  const std::vector<Transition> func = TransitionFunction(pattern, &final_states);
  AutomatonConstraint automaton = model.AddAutomaton(line, 0, final_states);
  for (const Transition& t : func) {
    automaton.AddTransition(t.tail, t.head, t.label);
  }
}

}  // namespace

// Nonogram: fill the grid so every row and column matches its run-length clue.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<std::vector<int64_t>> row_rules =
      instance.at("row_rules").get<std::vector<std::vector<int64_t>>>();
  const std::vector<std::vector<int64_t>> col_rules =
      instance.at("col_rules").get<std::vector<std::vector<int64_t>>>();
  const int n_rows = static_cast<int>(row_rules.size());
  const int n_cols = static_cast<int>(col_rules.size());

  std::vector<std::vector<IntVar>> board(n_rows);
  for (int r = 0; r < n_rows; ++r) {
    for (int c = 0; c < n_cols; ++c) {
      board[r].push_back(model.NewIntVar(Domain(0, 1)));
    }
  }

  for (int r = 0; r < n_rows; ++r) {
    AddRunConstraint(model, board[r], row_rules[r]);
  }
  for (int c = 0; c < n_cols; ++c) {
    std::vector<IntVar> column;
    for (int r = 0; r < n_rows; ++r) column.push_back(board[r][c]);
    AddRunConstraint(model, column, col_rules[c]);
  }

  json out = json::array();
  for (int r = 0; r < n_rows; ++r) {
    json row = json::array();
    for (int c = 0; c < n_cols; ++c) row.push_back(board[r][c].index());
    out.push_back(row);
  }
  outputs = {{"board", out}};
}
