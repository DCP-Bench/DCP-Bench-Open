#include "dcp.h"

// Three coins: starting from the given faces, make all coins face the same way
// (all heads or all tails) in exactly num_moves moves, where each move flips one coin.
// steps[t][c] is the state of coin c after t moves (True = tails, False = heads).
class ThreeCoins : public dcp::Space {
 protected:
  BoolVarArray s;  // s[t * coins + c]: coin c is tails after t moves

 public:
  explicit ThreeCoins(const json& instance) {
    int moves = instance.at("num_moves").get<int>();
    std::vector<int> init = instance.at("init");
    int coins = static_cast<int>(init.size());

    s = BoolVarArray(*this, (moves + 1) * coins, 0, 1);

    // the first row is the starting state of the coins
    for (int c = 0; c < coins; ++c)
      rel(*this, s[c], IRT_EQ, init[c]);

    // each move flips exactly one coin: the coins that differ between consecutive states number one
    for (int t = 0; t < moves; ++t) {
      BoolVarArgs flipped;
      for (int c = 0; c < coins; ++c) {
        BoolVar d(*this, 0, 1);
        rel(*this, s[t * coins + c], BOT_XOR, s[(t + 1) * coins + c], d);
        flipped << d;
      }
      linear(*this, flipped, IRT_EQ, 1);
    }

    // the final state has all coins facing the same way
    int last = moves * coins;
    for (int c = 1; c < coins; ++c)
      rel(*this, s[last + c] == s[last]);

    branch(*this, s, BOOL_VAR_NONE(), BOOL_VAL_MIN());

    // steps: one list of coin states per state, starting from the initial one
    std::vector<BoolVarArgs> steps;
    for (int t = 0; t <= moves; ++t) {
      BoolVarArgs row;
      for (int c = 0; c < coins; ++c) row << s[t * coins + c];
      steps.push_back(row);
    }
    output("steps", steps);
  }

  ThreeCoins(ThreeCoins& other) : dcp::Space(other) { s.update(*this, other.s); }
  Gecode::Space* copy() override { return new ThreeCoins(*this); }
};

DCP_MODEL(ThreeCoins)
