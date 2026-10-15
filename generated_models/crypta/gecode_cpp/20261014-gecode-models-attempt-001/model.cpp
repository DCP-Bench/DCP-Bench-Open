#include "dcp.h"

// Cryptarithm: BAIJJAJIIAHFCFEBBJEA + DHFGABCDIDBIFFAGFEJE = GJEGACDDHFAFJBFIHEEF.
// Each letter A..J stands for a different digit, and the first letter of each of the
// three numbers is not zero. The puzzle is fixed by the description; the instance has
// no fields, so every word below is taken from the problem statement.
class Crypta : public dcp::Space {
 protected:
  IntVarArray letter;  // letter[k] is the digit of the letter 'A' + k
  IntVarArray carry;   // carry[i] is the carry out of column i (columns counted from the left)

 public:
  explicit Crypta(const json&) : letter(*this, 10, 0, 9), carry(*this, 21, 0, 1) {
    static const std::string first = "BAIJJAJIIAHFCFEBBJEA";
    static const std::string second = "DHFGABCDIDBIFFAGFEJE";
    static const std::string result = "GJEGACDDHFAFJBFIHEEF";
    const int width = 20;

    // the ten letters are ten different digits
    IntVarArgs digits;
    for (int k = 0; k < 10; ++k) digits << letter[k];
    distinct(*this, digits, IPL_DOM);

    // the first letter of each number cannot be zero (B, D and G)
    for (char c : {first[0], second[0], result[0]}) rel(*this, letter[c - 'A'], IRT_GQ, 1);

    // no carry enters the rightmost column and none leaves the leftmost one
    rel(*this, carry[0], IRT_EQ, 0);
    rel(*this, carry[width], IRT_EQ, 0);

    // column by column: first digit + second digit + carry in = result digit + 10 * carry out
    for (int i = 0; i < width; ++i) {
      IntVarArgs column;
      column << letter[first[i] - 'A'] << letter[second[i] - 'A'] << carry[i + 1]
             << letter[result[i] - 'A'] << carry[i];
      linear(*this, IntArgs({1, 1, 1, -1, -10}), column, IRT_EQ, 0, IPL_DOM);
    }

    // branch on the letters first; the carries follow from them
    branch(*this, letter, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, carry, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    // print the digit of each letter
    for (int k = 0; k < 10; ++k) output(std::string(1, static_cast<char>('A' + k)), letter[k]);
  }

  Crypta(Crypta& s) : dcp::Space(s) {
    letter.update(*this, s.letter);
    carry.update(*this, s.carry);
  }
  Gecode::Space* copy() override { return new Crypta(*this); }
};

DCP_MODEL(Crypta)
