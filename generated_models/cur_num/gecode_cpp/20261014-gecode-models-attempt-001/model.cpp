#include "dcp.h"

// Peculiar number: a number between 1 and 10000, other than 48, such that
// adding 1 gives a square and adding 1 to its half also gives a square.
class Peculiar : public dcp::Space {
 protected:
  IntVar peculiar;  // the number printed
  IntVar half;      // half of the number (the number is even)
  IntVar root;      // root * root = peculiar + 1
  IntVar root_half; // root_half * root_half = half + 1

 public:
  explicit Peculiar(const json& instance) {
    (void)instance;  // the problem has no instance fields; the constants come from the description
    peculiar = IntVar(*this, 1, 10000);
    half = IntVar(*this, 1, 5000);
    root = IntVar(*this, 1, 101);       // 101^2 = 10201 > 10001
    root_half = IntVar(*this, 1, 71);   // 71^2 = 5041 > 5001

    // the answer is another number, not the 48 of the description
    rel(*this, peculiar, IRT_NQ, 48);

    // the half of the number is a whole number
    rel(*this, peculiar == 2 * half);

    // adding 1 to the number gives a square number
    rel(*this, root * root == peculiar + 1);

    // adding 1 to the half of the number gives a square number
    rel(*this, root_half * root_half == half + 1);

    // the number first, then the auxiliaries that define it
    branch(*this, peculiar, INT_VAL_MIN());
    IntVarArgs rest;
    rest << half << root << root_half;
    branch(*this, rest, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("peculiar", peculiar);
  }

  Peculiar(Peculiar& s) : dcp::Space(s) {
    peculiar.update(*this, s.peculiar);
    half.update(*this, s.half);
    root.update(*this, s.root);
    root_half.update(*this, s.root_half);
  }
  Gecode::Space* copy() override { return new Peculiar(*this); }
};

DCP_MODEL(Peculiar)
