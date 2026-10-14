#include "dcp.h"

// Water buckets: start with a full bucket and two empty ones, pour water between
// buckets (each pour is one transfer, and it stops when the source is empty or
// the target is full) until the buckets hold the goal amounts. Minimise the
// number of transfers, and output the states reached after each transfer.
class WaterBucket : public dcp::Space {
 protected:
  int steps;                 // MAX_STEPS: number of states in the sequence
  int pad;                   // PADDING_VALUE: value of the states after the goal
  IntVarArray st;            // st[3k+b]: content of bucket b in state k
  IntVarArray pour;          // pour[k]: transfer from state k to state k+1 (code 3*i+j), or NONE
  IntVar total;              // number of transfers

 public:
  // Pour code 3*i+j moves water from bucket i to bucket j (i != j). NONE means no
  // transfer, which only the padding states may take.
  static const int NONE = 9;

  explicit WaterBucket(const json& instance) {
    steps = instance.at("MAX_STEPS").get<int>();
    pad = instance.at("PADDING_VALUE").get<int>();
    std::vector<int> cap = instance.at("capacities");
    std::vector<int> init = instance.at("initial_state");
    std::vector<int> goal = instance.at("goal_state");

    // every state holds a bucket content between 0 and the capacity, or padding
    IntVarArgs cells;
    for (int k = 0; k < steps; ++k)
      for (int b = 0; b < 3; ++b) cells << IntVar(*this, pad, cap[b]);
    st = IntVarArray(*this, cells);

    pour = IntVarArray(*this, steps - 1, 0, NONE);

    // the first state is the initial one: the full bucket and two empty ones
    for (int b = 0; b < 3; ++b) rel(*this, st[b], IRT_EQ, init[b]);

    // legal transfers, one tuple per (state, pour) with a positive amount poured:
    // the source gives what the target can take, and the rest stays put
    TupleSet moves(7);
    for (int a = 0; a <= cap[0]; ++a)
      for (int b = 0; b <= cap[1]; ++b)
        for (int c = 0; c <= cap[2]; ++c) {
          int s[3] = {a, b, c};
          if (s[0] == goal[0] && s[1] == goal[1] && s[2] == goal[2]) continue;  // no pour leaves the goal
          for (int i = 0; i < 3; ++i)
            for (int j = 0; j < 3; ++j) {
              if (i == j) continue;
              int amount = std::min(s[i], cap[j] - s[j]);
              if (amount <= 0) continue;
              int t[3] = {s[0], s[1], s[2]};
              t[i] -= amount;
              t[j] += amount;
              moves.add(IntArgs({s[0], s[1], s[2], 3 * i + j, t[0], t[1], t[2]}));
            }
        }
    // after the goal, the sequence is padded: no transfer, padding stays padding
    moves.add(IntArgs({goal[0], goal[1], goal[2], NONE, pad, pad, pad}));
    moves.add(IntArgs({pad, pad, pad, NONE, pad, pad, pad}));
    moves.finalize();
    for (int k = 0; k + 1 < steps; ++k) {
      IntVarArgs row;
      for (int b = 0; b < 3; ++b) row << st[3 * k + b];
      row << pour[k];
      for (int b = 0; b < 3; ++b) row << st[3 * (k + 1) + b];
      extensional(*this, row, moves);
    }

    // the sequence ends in the goal state or, if it was reached earlier, in padding
    TupleSet last(3);
    last.add(IntArgs({goal[0], goal[1], goal[2]}));
    last.add(IntArgs({pad, pad, pad}));
    last.finalize();
    IntVarArgs final_state;
    for (int b = 0; b < 3; ++b) final_state << st[3 * (steps - 1) + b];
    extensional(*this, final_state, last);

    // the cost is the number of transfers: pours that are not NONE
    BoolVarArgs transfers;
    for (int k = 0; k + 1 < steps; ++k) transfers << expr(*this, pour[k] != NONE);
    total = expr(*this, sum(transfers));

    branch(*this, pour, INT_VAR_NONE(), INT_VAL_MIN());
    branch(*this, st, INT_VAR_NONE(), INT_VAL_MIN());
    minimize(total);

    std::vector<IntVarArgs> sequence(steps);
    for (int k = 0; k < steps; ++k)
      for (int b = 0; b < 3; ++b) sequence[k] << st[3 * k + b];
    output("cost", total);
    output("sequence", sequence);
  }

  WaterBucket(WaterBucket& s) : dcp::Space(s), steps(s.steps), pad(s.pad) {
    st.update(*this, s.st);
    pour.update(*this, s.pour);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new WaterBucket(*this); }
};

DCP_MODEL(WaterBucket)
