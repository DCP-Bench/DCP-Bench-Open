#include "dcp.h"

// Kidney exchange: n people on a waiting list. compatible[i] lists the people that
// person i can donate a kidney to. Anyone who gives a kidney must receive one, and no
// person receives more than one kidney. Maximise the number of people who receive one.
class KidneyExchange : public dcp::Space {
 protected:
  int n;
  IntVarArray succ;  // succ[i]: the person that i donates to; succ[i] == i means i takes part in no transplant

 public:
  explicit KidneyExchange(const json& instance) {
    n = instance.at("num_people").get<int>();
    const auto& compatible = instance.at("compatible");

    // the waiting list: one variable per person, the person they donate to
    succ = IntVarArray(*this, n, 0, n - 1);

    // i can donate to the people in compatible[i] (the data numbers people from 1);
    // i may also stay out of every transplant, which is recorded as succ[i] == i
    for (int i = 0; i < n; ++i) {
      std::vector<int> options{i};
      for (const auto& j : compatible[i]) {
        int p = j.get<int>() - 1;
        if (p != i) options.push_back(p);
      }
      std::sort(options.begin(), options.end());
      options.erase(std::unique(options.begin(), options.end()), options.end());
      dom(*this, succ[i], IntSet(IntArgs(options)));
    }

    // anyone who gives a kidney must receive one, and no person receives more than one:
    // succ is a permutation, so the transplants form disjoint cycles
    distinct(*this, succ, IPL_DOM);

    // transplants[i][j] is 1 if person i donates to person j; nobody donates to themselves
    std::vector<BoolVarArgs> transplants(n);
    BoolVarArgs all;
    for (int i = 0; i < n; ++i) {
      for (int j = 0; j < n; ++j) {
        BoolVar x(*this, 0, 1);
        if (i == j) {
          rel(*this, x, IRT_EQ, 0);
        } else {
          rel(*this, succ[i], IRT_EQ, j, x);
        }
        transplants[i] << x;
        all << x;
      }
    }

    // maximise the number of people who receive a kidney (each receipt is one transplant)
    IntVar receivers = expr(*this, sum(all));
    maximize(receivers);

    branch(*this, succ, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("transplants", transplants);
  }

  KidneyExchange(KidneyExchange& s) : dcp::Space(s), n(s.n) { succ.update(*this, s.succ); }
  Gecode::Space* copy() override { return new KidneyExchange(*this); }
};

DCP_MODEL(KidneyExchange)
