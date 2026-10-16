// Problem: Set card game. The layout has n distinct cards, each card is
// [number, fill, color, shape] with every feature in 1..3. A set is three cards
// such that, for each feature, the three cards show that feature all the same or
// all different. Output the 0-based indices of one set (winning_cards).
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const json& cards = instance.at("cards_data");
  const int n = static_cast<int>(cards.size());
  const int num_features = 4;

  // Three positions of the set. y[k][i] = 1 when position k holds card i.
  std::vector<std::vector<dcp::Lin>> y(3, std::vector<dcp::Lin>(n));
  for (int k = 0; k < 3; ++k)
    for (int i = 0; i < n; ++i) y[k][i] = dcp::new_var(h, 0, 1);

  // // each position holds exactly one card
  for (int k = 0; k < 3; ++k) {
    dcp::Lin sum;
    for (int i = 0; i < n; ++i) sum = sum + y[k][i];
    dcp::add_row(h, sum, 1, 1);
  }

  // // the three positions hold three different cards
  for (int i = 0; i < n; ++i) {
    dcp::Lin sum;
    for (int k = 0; k < 3; ++k) sum = sum + y[k][i];
    dcp::add_row(h, sum, -kHighsInf, 1);
  }

  // Index of the card at each position: idx[k] = sum_i i * y[k][i].
  std::vector<dcp::Lin> idx(3);
  for (int k = 0; k < 3; ++k)
    for (int i = 0; i < n; ++i) idx[k] = idx[k] + static_cast<double>(i) * y[k][i];

  // // the indices of the set are listed in increasing order
  for (int k = 0; k + 1 < 3; ++k) dcp::add_row(h, idx[k + 1] - idx[k], 1, kHighsInf);

  // // for each feature, the three values are all the same or all different.
  // Values are in 1..3, and a triple of values in 1..3 sums to a multiple of 3
  // exactly when it is all equal or all different. So the sum equals 3 t, with t in 1..3.
  for (int f = 0; f < num_features; ++f) {
    dcp::Lin t = dcp::new_var(h, 1, 3);
    dcp::Lin total;
    for (int k = 0; k < 3; ++k)
      for (int i = 0; i < n; ++i)
        total = total + static_cast<double>(cards[i][f].get<int>()) * y[k][i];
    dcp::add_row(h, total - 3.0 * t, 0, 0);
  }

  out.add("winning_cards", idx);
}
