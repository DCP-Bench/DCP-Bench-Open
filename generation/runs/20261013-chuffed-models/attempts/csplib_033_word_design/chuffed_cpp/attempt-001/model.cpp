// DNA word design: find num_words words of length n over {A,C,G,T} (1,2,3,4) with the properties of the problem.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");
  int num_words = instance.at("num_words");
  const int min_distance = 4;  // words differ in at least 4 positions (problem statement)
  const int gc_symbols = 4;    // each word has 4 symbols from {C, G} (problem statement)

  // words[i][k] is the letter at position k of word i: 1 for A, 2 for C, 3 for G, 4 for T
  vec<vec<IntVar*>> words;
  createVars(words, num_words, n, 1, 4, true);

  // complement[i][k] is the Watson-Crick complement of words[i][k]: A<->T and C<->G, that is 5 - letter
  vec<vec<IntVar*>> complement;
  createVars(complement, num_words, n, 1, 4, true);
  for (int i = 0; i < num_words; ++i)
    for (int k = 0; k < n; ++k) bin_linear(words[i][k], complement[i][k], IRT_EQ, 5);

  // each word in S has 4 symbols from {C, G}
  vec<int> is_cg_table;  // indexed by letter 0..4: C and G count
  is_cg_table.push(0);
  is_cg_table.push(0);
  is_cg_table.push(1);
  is_cg_table.push(1);
  is_cg_table.push(0);
  for (int i = 0; i < num_words; ++i) {
    vec<IntVar*> is_cg;
    for (int k = 0; k < n; ++k) {
      IntVar* b = newIntVar(0, 1);
      array_int_element(words[i][k], is_cg_table, b);
      is_cg.push(b);
    }
    int_linear(is_cg, IRT_EQ, gc_symbols);
  }

  // each pair of distinct words in S differ in at least 4 positions
  for (int i = 0; i < num_words; ++i)
    for (int j = i + 1; j < num_words; ++j) {
      vec<BoolView> differs;
      createVars(differs, n);
      for (int k = 0; k < n; ++k) int_rel_reif(words[i][k], IRT_NE, words[j][k], differs[k]);
      IntVar* distance_ok = getConstant(min_distance);
      bool_linear(differs, IRT_GE, distance_ok);
    }

  // each pair of words x and y in S (also x = y) are such that the reverse of x and the complement of y
  // differ in at least 4 positions
  for (int i = 0; i < num_words; ++i)
    for (int j = 0; j < num_words; ++j) {
      vec<BoolView> differs;
      createVars(differs, n);
      for (int k = 0; k < n; ++k) int_rel_reif(words[i][n - 1 - k], IRT_NE, complement[j][k], differs[k]);
      IntVar* distance_ok = getConstant(min_distance);
      bool_linear(differs, IRT_GE, distance_ok);
    }

  // S is a set, so the order of its words does not matter: list them in strictly increasing lexicographic order
  // (the words are pairwise different, so this removes only permutations of the same set)
  for (int i = 0; i + 1 < num_words; ++i) lex(words[i], words[i + 1], true);

  vec<IntVar*> flat;
  flatten(words, flat);
  branch(flat, VAR_INORDER, VAL_MIN);
  json rows = json::array();
  for (int i = 0; i < num_words; ++i) {
    json row = json::array();
    for (int k = 0; k < n; ++k) row.push_back(dcp::out(words[i][k]));
    rows.push_back(row);
  }
  outputs = {{"words", rows}};
}
