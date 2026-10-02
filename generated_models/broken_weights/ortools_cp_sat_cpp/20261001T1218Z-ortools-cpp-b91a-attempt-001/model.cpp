#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Broken weights: a weight of total m broke into n whole-pound pieces; choose
// the pieces so that every integral weight from 1 to m can be weighed on a
// balance scale, where a piece may go on either side or stay off.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int m = instance.at("m").get<int>();  // total weight
  const int n = instance.at("n").get<int>();  // number of pieces

  // weights[j] is the weight of piece j, from 1 to m.
  std::vector<IntVar> weights;
  for (int j = 0; j < n; ++j) weights.push_back(model.NewIntVar(Domain(1, m)));

  // side[i][j] says where piece j goes when weighing the object of weight
  // i + 1: -1 on the left, +1 on the right, 0 left off the scale.
  std::vector<std::vector<IntVar>> side(m);
  for (int i = 0; i < m; ++i) {
    for (int j = 0; j < n; ++j) {
      side[i].push_back(model.NewIntVar(Domain::FromValues({-1, 0, 1})));
    }
  }

  // The pieces together weigh the total weight.
  LinearExpr total;
  for (int j = 0; j < n; ++j) total += weights[j];
  model.AddEquality(total, m);

  // Every weight from 1 to m can be made: for object weight i + 1 the signed
  // sum of the pieces is i + 1.  Each signed piece is a product of two
  // variables, so it gets an auxiliary variable bounded by -m..m.
  for (int i = 0; i < m; ++i) {
    LinearExpr signed_sum;
    for (int j = 0; j < n; ++j) {
      IntVar signed_piece = model.NewIntVar(Domain(-m, m));
      model.AddMultiplicationEquality(signed_piece, weights[j], side[i][j]);
      signed_sum += signed_piece;
    }
    model.AddEquality(signed_sum, i + 1);
  }

  json weights_out = json::array();
  for (const IntVar& w : weights) weights_out.push_back(w.index());
  outputs = {{"weights", weights_out}};
}
