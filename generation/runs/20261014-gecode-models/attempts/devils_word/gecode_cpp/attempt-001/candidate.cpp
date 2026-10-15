#include "dcp.h"

// Devil's word: insert '+' or '-' before each integer of the array so that the
// signed sum is 666. Output the array with the chosen signs.
class DevilsWord : public dcp::Space {
 protected:
  // no variables are kept as members: the outputs and the search are posted
  // in the constructor, and the copy constructor only passes the base space on
 public:
  explicit DevilsWord(const json& instance) {
    std::vector<int> arr = instance.at("arr").get<std::vector<int>>();
    int total = instance.at("total").get<int>();
    int n = static_cast<int>(arr.size());

    // each element is either +a or -a: its signed value has the two-value domain {-a, a}
    IntVarArgs result;
    for (int i = 0; i < n; ++i) {
      std::vector<int> choices = {-arr[i], arr[i]};
      if (arr[i] == 0) choices.pop_back();   // +0 and -0 are the same value
      result << IntVar(*this, IntSet(IntArgs(choices)));
    }

    // the signed values sum to the total
    linear(*this, result, IRT_EQ, total, IPL_BND);

    // branch on the signed values in array order
    branch(*this, result, INT_VAR_NONE(), INT_VAL_MIN());

    output("result", result);
  }

  DevilsWord(DevilsWord& s) : dcp::Space(s) {}
  Gecode::Space* copy() override { return new DevilsWord(*this); }
};

DCP_MODEL(DevilsWord)
