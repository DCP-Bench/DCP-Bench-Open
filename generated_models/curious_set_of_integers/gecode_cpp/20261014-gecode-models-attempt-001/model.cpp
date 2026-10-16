#include "dcp.h"

// Curious set of integers: the set 1, 3, 8, 120 plus one unknown number x >= 0 such
// that the product of any two members of the set is one less than a perfect square.
// The four given integers are problem data; the unknown is the single output number.
class CuriousSetOfIntegers : public dcp::Space {
 protected:
  IntVar number;      // the fifth number, 0 <= number <= max_val
  IntVarArray roots;  // roots[i]: square root of (given[i] * number + 1)

 public:
  explicit CuriousSetOfIntegers(const json& instance) {
    int n = instance.at("n");          // size of the set, including the unknown
    int max_val = instance.at("max_val");
    const std::vector<int> given = {1, 3, 8, 120};  // the set from the description
    if (n != static_cast<int>(given.size()) + 1)
      throw std::invalid_argument("the set must hold the four given integers and one unknown");

    // the fifth number lies between 0 and the instance bound
    number = IntVar(*this, 0, max_val);

    // the largest product is 120 * max_val + 1, so its root is bounded by the sqrt of that
    int root_max = static_cast<int>(std::floor(std::sqrt(120.0 * max_val + 1.0))) + 1;
    roots = IntVarArray(*this, static_cast<int>(given.size()), 0, root_max);

    // the product of each given integer with the fifth number is one less than a perfect square
    for (int i = 0; i < static_cast<int>(given.size()); ++i) {
      IntVar product_plus_one = expr(*this, given[i] * number + 1);
      rel(*this, roots[i] * roots[i] == product_plus_one);
    }

    // the products of two given integers are checked by hand: 1*3+1=4, 1*8+1=9,
    // 1*120+1=121, 3*8+1=25, 3*120+1=361, 8*120+1=961 are all squares

    branch(*this, roots, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, number, INT_VAL_MIN());
    output("number", number);
  }

  CuriousSetOfIntegers(CuriousSetOfIntegers& s) : dcp::Space(s) {
    number.update(*this, s.number);
    roots.update(*this, s.roots);
  }
  Gecode::Space* copy() override { return new CuriousSetOfIntegers(*this); }
};

DCP_MODEL(CuriousSetOfIntegers)
