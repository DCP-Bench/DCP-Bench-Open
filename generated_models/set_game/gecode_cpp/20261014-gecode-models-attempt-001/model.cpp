// Set (card game): pick three of the dealt cards that form a set.
// A card is [number, fill, color, shape], each value in 1..3. Three cards form a
// set when, on every feature, the three cards are all the same or all different.
// Output: the 0-based indices of the three cards, in increasing order.

#include "dcp.h"

class SetGame : public dcp::Space {
 protected:
  IntVarArray win;   // win[k]: 0-based index of the k-th card of the set
  IntVarArray feat;  // feat[3*f + k]: value of feature f on the k-th card of the set

 public:
  explicit SetGame(const json& instance) {
    std::vector<std::vector<int>> cards =
        instance.at("cards_data").get<std::vector<std::vector<int>>>();
    int n = static_cast<int>(cards.size());
    const int features = 4;  // number, fill, color, shape

    win = IntVarArray(*this, 3, 0, n - 1);
    feat = IntVarArray(*this, 3 * features, 1, 3);

    // the three cards are different cards, listed in increasing index order
    rel(*this, win[0], IRT_LE, win[1]);
    rel(*this, win[1], IRT_LE, win[2]);

    // the feature values of each chosen card, read from the dealt cards
    for (int f = 0; f < features; ++f) {
      std::vector<int> column(n);
      for (int i = 0; i < n; ++i) column[i] = cards[i][f];
      for (int k = 0; k < 3; ++k)
        element(*this, IntArgs(column), win[k], feat[3 * f + k]);
    }

    // on each feature the three values are all the same or all different
    TupleSet same_or_all_different(3);
    for (int a = 1; a <= 3; ++a)
      for (int b = 1; b <= 3; ++b)
        for (int c = 1; c <= 3; ++c)
          if ((a == b && b == c) || (a != b && b != c && a != c))
            same_or_all_different.add(IntArgs({a, b, c}));
    same_or_all_different.finalize();
    for (int f = 0; f < features; ++f) {
      IntVarArgs values;
      for (int k = 0; k < 3; ++k) values << feat[3 * f + k];
      extensional(*this, values, same_or_all_different);
    }

    branch(*this, win, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("winning_cards", win);
  }

  SetGame(SetGame& s) : dcp::Space(s) {
    win.update(*this, s.win);
    feat.update(*this, s.feat);
  }
  Gecode::Space* copy() override { return new SetGame(*this); }
};

DCP_MODEL(SetGame)
