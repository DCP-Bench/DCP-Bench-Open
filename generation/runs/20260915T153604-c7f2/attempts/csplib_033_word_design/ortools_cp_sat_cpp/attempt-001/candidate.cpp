#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

namespace {

// A reified "these two expressions differ" indicator.
BoolVar Differs(CpModelBuilder& model, const LinearExpr& left,
                const LinearExpr& right) {
  BoolVar differs = model.NewBoolVar();
  model.AddNotEqual(left, right).OnlyEnforceIf(differs);
  model.AddEquality(left, right).OnlyEnforceIf(differs.Not());
  return differs;
}

}  // namespace

// DNA word design: words over {A,C,G,T} with a fixed C/G content, pairwise far
// apart, and far from every other word's reverse complement.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();
  const int num_words = instance.at("num_words").get<int>();

  // The alphabet is encoded A=1, C=2, G=3, T=4, as the reference does, so the
  // Watson-Crick complement of a letter is 5 minus it.
  const int64_t kA = 1;
  const int64_t kC = 2;
  const int64_t kG = 3;
  const int64_t kT = 4;

  std::vector<std::vector<IntVar>> words(num_words);
  for (int w = 0; w < num_words; ++w) {
    for (int j = 0; j < n; ++j) {
      words[w].push_back(model.NewIntVar(Domain(kA, kT)));
    }
  }

  // Exactly four of the letters in each word are C or G.
  for (int w = 0; w < num_words; ++w) {
    LinearExpr cg_count;
    for (int j = 0; j < n; ++j) {
      BoolVar is_cg = model.NewBoolVar();
      model.AddLinearConstraint(words[w][j], Domain::FromValues({kC, kG}))
          .OnlyEnforceIf(is_cg);
      model.AddLinearConstraint(words[w][j], Domain::FromValues({kA, kT}))
          .OnlyEnforceIf(is_cg.Not());
      cg_count += is_cg;
    }
    model.AddEquality(cg_count, 4);
  }

  // Distinct words differ in at least four positions.
  for (int x = 0; x < num_words; ++x) {
    for (int y = x + 1; y < num_words; ++y) {
      LinearExpr distance;
      for (int j = 0; j < n; ++j) {
        distance += Differs(model, words[x][j], words[y][j]);
      }
      model.AddGreaterOrEqual(distance, 4);
    }
  }

  // Every word's reverse is at least four positions from every word's
  // complement, the pair of a word with itself included.
  for (int y = 0; y < num_words; ++y) {
    for (int x = 0; x < num_words; ++x) {
      LinearExpr distance;
      for (int j = 0; j < n; ++j) {
        distance += Differs(model, words[x][n - 1 - j], 5 - words[y][j]);
      }
      model.AddGreaterOrEqual(distance, 4);
    }
  }

  json out = json::array();
  for (int w = 0; w < num_words; ++w) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(words[w][j].index());
    out.push_back(row);
  }
  outputs = {{"words", out}};
}
