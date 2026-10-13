// Three coins: flip coins one at a time so that after exactly num_moves moves all coins show the same face.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int num_moves = instance.at("num_moves");
  std::vector<int> init = instance.at("init").get<std::vector<int>>();
  int num_coins = static_cast<int>(init.size());
  int num_states = num_moves + 1;

  // face[t][c] = 1 if coin c shows tails (True) after t moves; face[0] is the starting position
  vec<vec<IntVar*>> face;
  createVars(face, num_states, num_coins, 0, 1, true);

  // the coins start as given in the instance (1 = tails, 0 = heads)
  for (int c = 0; c < num_coins; ++c) {
    int_rel(face[0][c], IRT_EQ, init[c]);
  }

  for (int t = 0; t < num_moves; ++t) {
    // flip[c] = 1 when move t turns coin c over, which is exactly when its face changes
    vec<BoolView> flip;
    for (int c = 0; c < num_coins; ++c) {
      BoolView f = newBoolVar();
      vec<int> coef;
      coef.push(1);
      coef.push(1);
      vec<IntVar*> pair;
      pair.push(face[t + 1][c]);
      pair.push(face[t][c]);
      // f <-> (the face after the move differs from the face before it)
      int_linear(coef, pair, IRT_EQ, 1, f);
      flip.push(f);
    }
    // each move turns over exactly one coin
    bool_linear(flip, IRT_EQ, getConstant(1));
  }

  // after the last move all coins show the same face
  int last = num_moves;
  for (int c = 1; c < num_coins; ++c) {
    int_rel(face[last][c], IRT_EQ, face[last][0]);
  }

  // search over the faces of the moves in order
  vec<IntVar*> flat;
  flatten(face, flat);
  branch(flat, VAR_INORDER, VAL_MIN);

  json steps = json::array();
  for (int t = 0; t < num_states; ++t) {
    json row = json::array();
    for (int c = 0; c < num_coins; ++c) {
      row.push_back(dcp::out(face[t][c]));
    }
    steps.push_back(row);
  }
  outputs = {{"steps", steps}};
}
