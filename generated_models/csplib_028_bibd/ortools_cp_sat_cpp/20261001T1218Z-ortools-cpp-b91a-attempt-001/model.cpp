#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Balanced incomplete block design: arrange v objects into b blocks so that
// each block has k objects, each object is in r blocks, and every two distinct
// objects are together in exactly l blocks.  The design is the v by b
// incidence matrix of 0s and 1s.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int v = instance.at("v").get<int>();    // objects
  const int b = instance.at("b").get<int>();    // blocks
  const int r = instance.at("r").get<int>();    // blocks per object
  const int k = instance.at("k").get<int>();    // objects per block
  const int l = instance.at("l").get<int>();    // blocks shared by each pair

  // matrix[i][j] is true when object i is in block j.
  std::vector<std::vector<BoolVar>> matrix(v);
  for (int i = 0; i < v; ++i) {
    for (int j = 0; j < b; ++j) matrix[i].push_back(model.NewBoolVar());
  }

  // Every row (object) adds up to r.
  for (int i = 0; i < v; ++i) {
    LinearExpr blocks_of_object;
    for (int j = 0; j < b; ++j) blocks_of_object += matrix[i][j];
    model.AddEquality(blocks_of_object, r);
  }
  // Every column (block) adds up to k.
  for (int j = 0; j < b; ++j) {
    LinearExpr objects_in_block;
    for (int i = 0; i < v; ++i) objects_in_block += matrix[i][j];
    model.AddEquality(objects_in_block, k);
  }

  // The scalar product of every pair of rows is l: the two objects are
  // together in a block when both entries of that column are 1.  together is
  // pinned to the AND of the two entries in both directions.
  for (int i = 0; i < v; ++i) {
    for (int i2 = i + 1; i2 < v; ++i2) {
      LinearExpr shared_blocks;
      for (int j = 0; j < b; ++j) {
        BoolVar together = model.NewBoolVar();
        model.AddImplication(together, matrix[i][j]);
        model.AddImplication(together, matrix[i2][j]);
        model.AddBoolOr({matrix[i][j].Not(), matrix[i2][j].Not(), together});
        shared_blocks += together;
      }
      model.AddEquality(shared_blocks, l);
    }
  }

  json out = json::array();
  for (int i = 0; i < v; ++i) {
    json row = json::array();
    for (int j = 0; j < b; ++j) row.push_back(matrix[i][j].index());
    out.push_back(row);
  }
  outputs = {{"matrix", out}};
}
