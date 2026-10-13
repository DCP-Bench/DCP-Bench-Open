// Nontransitive dice: five dice whose "beats" relations match Rock-Paper-Scissors-Lizard-Spock.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // Problem constants from the statement: 5 dice, 6 faces, face values 1..12.
  const int n_dice = 5, n_faces = 6, lo = 1, hi = 12;
  // 0 Rock, 1 Paper, 2 Scissors, 3 Lizard, 4 Spock
  // the ten "beats" relationships (winner, loser), numbered as in the statement
  const int beats[10][2] = {{0, 2}, {0, 3}, {1, 0}, {1, 4}, {2, 1},
                            {2, 3}, {3, 1}, {3, 4}, {4, 0}, {4, 2}};

  // dice[d][f] is the value of face f of die d (faces may be in any order)
  vec<vec<IntVar*>> dice;
  createVars(dice, n_dice, n_faces, lo, hi);

  // Which die beats which only depends on the multiset of faces, so the search works on a
  // sorted copy of every die; dice[d] is linked to it by a permutation, which keeps every
  // face order of the output possible. This shrinks the search space a lot.
  vec<vec<IntVar*>> sorted_dice, where;
  createVars(sorted_dice, n_dice, n_faces, lo, hi);
  createVars(where, n_dice, n_faces, 0, n_faces - 1, true);
  for (int d = 0; d < n_dice; ++d) {
    for (int f = 0; f + 1 < n_faces; ++f) int_rel(sorted_dice[d][f], IRT_LE, sorted_dice[d][f + 1]);
    all_different(where[d]);
    // dice[d][f] is the face of the sorted die at position where[d][f]
    for (int f = 0; f < n_faces; ++f)
      array_var_int_element_bound(where[d][f], sorted_dice[d], dice[d][f]);
  }

  // die A beats die B if A has a strictly larger face value than B in more than half of
  // all possible pairs of faces
  for (int r = 0; r < 10; ++r) {
    int a = beats[r][0], b = beats[r][1];
    vec<BoolView> wins;
    for (int i = 0; i < n_faces; ++i)
      for (int j = 0; j < n_faces; ++j) {
        BoolView w = newBoolVar();
        int_rel_reif(sorted_dice[a][i], IRT_GT, sorted_dice[b][j], w);
        wins.push(w);
      }
    // strictly more than half of the 36 pairs
    IntVar* count = newIntVar(0, n_faces * n_faces);
    bool_linear(wins, IRT_EQ, count);
    int_rel(count, IRT_GT, n_faces * n_faces / 2);
  }

  vec<IntVar*> all;
  for (int d = 0; d < n_dice; ++d)
    for (int f = 0; f < n_faces; ++f) all.push(sorted_dice[d][f]);
  branch(all, VAR_INORDER, VAL_MIN);

  json out = json::array();
  for (int d = 0; d < n_dice; ++d) {
    json row = json::array();
    for (int f = 0; f < n_faces; ++f) row.push_back(dcp::out(dice[d][f]));
    out.push_back(row);
  }
  outputs = {{"dice", out}};
}
