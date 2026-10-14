#include "dcp.h"

// Even Fibonacci numbers: the sum of all even-valued terms of the sequence 1, 2, 3, 5, 8, ...
// that do not exceed four million (res).
class FibonacciEven : public dcp::Space {
 protected:
  IntVarArray term;  // term[k]: the (k+1)-th term of the sequence 1, 2, 3, 5, 8, ...
  IntVar res;        // sum of the even terms that do not exceed four million

 public:
  explicit FibonacciEven(const json& instance) {
    (void)instance;  // the problem has no instance data; the limit and the start are fixed by the description
    const int limit = 4000000;  // "do not exceed four million"
    const int n = 40;           // the 33rd term already exceeds four million; 40 terms leave margin
    term = IntVarArray(*this, n, 1, 200000000);  // term 40 is 165580141, so this domain holds every term

    // the sequence starts with 1 and 2
    rel(*this, term[0], IRT_EQ, 1);
    rel(*this, term[1], IRT_EQ, 2);

    // each new term is the sum of the previous two terms
    for (int k = 2; k < n; ++k) rel(*this, term[k] == term[k - 1] + term[k - 2]);

    // sum of the even-valued terms that do not exceed four million
    IntVarArgs contribution;
    for (int k = 0; k < n; ++k) {
      BoolVar not_above = expr(*this, term[k] <= limit);
      BoolVar is_even = expr(*this, (term[k] % 2) == 0);
      BoolVar take = expr(*this, not_above && is_even);
      contribution << expr(*this, term[k] * take);
    }
    res = expr(*this, sum(contribution));

    branch(*this, term, INT_VAR_NONE(), INT_VAL_MIN());
    output("res", res);
  }

  FibonacciEven(FibonacciEven& s) : dcp::Space(s) {
    term.update(*this, s.term);
    res.update(*this, s.res);
  }
  Gecode::Space* copy() override { return new FibonacciEven(*this); }
};

DCP_MODEL(FibonacciEven)
