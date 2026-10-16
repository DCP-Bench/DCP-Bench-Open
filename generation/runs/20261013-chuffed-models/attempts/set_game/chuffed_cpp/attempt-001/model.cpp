// Set card game: find three cards from the given cards that form a set. Each card has four
// features (number, fill, colour, shape) with values 1, 2 or 3, given in cards_data as
// [number, fill, colour, shape]. For each feature the three cards must show the same value on
// all three cards or three different values. Output the 0-based indices of the three cards in
// ascending order.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<std::vector<int>> cards = instance.at("cards_data").get<std::vector<std::vector<int>>>();
  int n = static_cast<int>(cards.size());

  // win[k] is the index of the k-th winning card, in ascending order, so each set is listed once
  vec<IntVar*> win;
  createVars(win, 3, 0, n - 1);
  int_rel(win[0], IRT_LT, win[1]);
  int_rel(win[1], IRT_LT, win[2]);

  // for each feature, the value of each winning card is looked up in the column of that feature
  for (int f = 0; f < 4; ++f) {
    vec<int> column;
    for (int i = 0; i < n; ++i) column.push(cards[i][f]);

    vec<IntVar*> value;
    for (int k = 0; k < 3; ++k) {
      IntVar* v = newIntVar(1, 3);
      array_int_element(win[k], column, v);
      value.push(v);
    }

    // the three values are all the same or all different exactly when their sum is a multiple of 3,
    // because the values are 1, 2 or 3 (two equal and one different never sums to a multiple of 3).
    // sum = 3 * multiple, written as value0 + value1 + value2 - 3 * multiple = 0.
    IntVar* multiple = newIntVar(1, 3);
    vec<int> coef;
    coef.push(1);
    coef.push(1);
    coef.push(1);
    coef.push(-3);
    vec<IntVar*> terms;
    terms.push(value[0]);
    terms.push(value[1]);
    terms.push(value[2]);
    terms.push(multiple);
    int_linear(coef, terms, IRT_EQ, 0);
  }

  // the card indices are the decision variables
  branch(win, VAR_INORDER, VAL_MIN);

  json indices = json::array();
  for (int k = 0; k < 3; ++k) indices.push_back(dcp::out(win[k]));
  outputs = {{"winning_cards", indices}};
}
