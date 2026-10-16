#include "dcp.h"

#include <map>
#include <string>

// General store (cryptarithm): each different letter stands for a different digit,
// and the words above the line add up to ALL WOOL.
class GeneralStore : public dcp::Space {
 protected:
  // letters in the order C H E S A B O W P L
  IntVarArray L;
  static int idx(char c) {
    static const std::string order = "CHESABOWPL";
    return static_cast<int>(order.find(c));
  }

 public:
  // The instance has no fields: the sum is fixed by the problem statement.
  explicit GeneralStore(const json& instance) : L(*this, 10, 0, 9) {
    (void)instance;

    // the letter-to-digit map is injective
    distinct(*this, L, IPL_DOM);

    // the words above the line: each word contributes its digit times its place value
    // (units 1, tens 10, ...) to the total for its letter; ALL WOOL is subtracted
    std::vector<std::string> addends = {
        "CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
        "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"};
    std::string total = "ALLWOOL";

    std::map<int, int> coef;  // letter index -> coefficient in the sum
    auto add_word = [&coef](const std::string& w, int sign) {
      int place = 1;
      for (auto it = w.rbegin(); it != w.rend(); ++it) {
        coef[idx(*it)] += sign * place;
        place *= 10;
      }
    };
    for (const auto& w : addends) add_word(w, 1);
    add_word(total, -1);

    IntArgs c(10);
    IntVarArgs x(10);
    for (int i = 0; i < 10; ++i) {
      c[i] = coef.count(i) ? coef[i] : 0;
      x[i] = L[i];
    }
    linear(*this, c, x, IRT_EQ, 0, IPL_DOM);

    branch(*this, L, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("C", L[idx('C')]);
    output("H", L[idx('H')]);
    output("E", L[idx('E')]);
    output("S", L[idx('S')]);
    output("A", L[idx('A')]);
    output("B", L[idx('B')]);
    output("O", L[idx('O')]);
    output("W", L[idx('W')]);
    output("P", L[idx('P')]);
    output("L", L[idx('L')]);
  }

  GeneralStore(GeneralStore& s) : dcp::Space(s) { L.update(*this, s.L); }
  Gecode::Space* copy() override { return new GeneralStore(*this); }
};

DCP_MODEL(GeneralStore)
