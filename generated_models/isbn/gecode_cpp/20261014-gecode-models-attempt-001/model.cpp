#include "dcp.h"

// ISBN-13 validation and check digit calculation: fill in the unknown digits (-1)
// of a 13-digit ISBN so that it is valid and starts with 978 or 979.
class Isbn : public dcp::Space {
 protected:
  IntVarArray isbn;  // isbn[i]: digit i of the ISBN
  IntVar k;          // weighted digit sum is 10 * k

 public:
  explicit Isbn(const json& instance) {
    std::vector<int> init = instance.at("isbn_init").get<std::vector<int>>();

    // every digit is 0..9
    isbn = IntVarArray(*this, 13, 0, 9);

    // digits given in the instance stay as they are; -1 marks an unknown digit
    for (int i = 0; i < 13; ++i)
      if (init[i] != -1) rel(*this, isbn[i] == init[i]);

    // the ISBN starts with 978 or 979: first digit 9, second digit 7, third digit 8 or 9
    rel(*this, isbn[0] == 9);
    rel(*this, isbn[1] == 7);
    rel(*this, isbn[2] >= 8);

    // the digits weighted alternately by 1 and 3 (starting with 1) sum to a multiple of 10,
    // which is exactly the check digit rule (10 - sum % 10) % 10 applied to the last digit.
    // The weighted sum of 13 digits is at most 9 * (7 * 1 + 6 * 3) = 225, so k is at most 22.
    k = IntVar(*this, 0, 22);
    IntVarArgs terms;
    IntArgs weights(14);
    for (int i = 0; i < 13; ++i) {
      terms << isbn[i];
      weights[i] = (i % 2 == 0) ? 1 : 3;
    }
    terms << k;
    weights[13] = -10;
    linear(*this, weights, terms, IRT_EQ, 0, IPL_DOM);

    branch(*this, isbn, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("isbn", isbn);
  }

  Isbn(Isbn& s) : dcp::Space(s) {
    isbn.update(*this, s.isbn);
    k.update(*this, s.k);
  }
  Gecode::Space* copy() override { return new Isbn(*this); }
};

DCP_MODEL(Isbn)
