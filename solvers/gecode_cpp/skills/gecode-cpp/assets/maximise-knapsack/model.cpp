// 0/1 knapsack (maximise): choose items of maximum total value whose total weight
// fits the capacity. BAB with a time limit; stopped() tells proven from unproven.
#include <gecode/int.hh>
#include <gecode/minimodel.hh>
#include <gecode/search.hh>
#include <iostream>
#include <vector>
using namespace Gecode;

const std::vector<int> kValue = {10, 13, 18, 31, 7, 15};
const std::vector<int> kWeight = {11, 15, 20, 35, 10, 33};
const int kCapacity = 47;

class Knapsack : public IntMaximizeSpace {
 protected:
  BoolVarArray take;
  IntVar value;

 public:
  Knapsack() : take(*this, kValue.size(), 0, 1) {
    // the chosen items fit
    linear(*this, IntArgs(kWeight), take, IRT_LQ, kCapacity);
    // value = sum of the chosen values; expr takes its bounds from the expression
    value = expr(*this, sum(IntArgs(kValue), take));
    branch(*this, take, BOOL_VAR_NONE(), BOOL_VAL_MAX());
  }
  Knapsack(Knapsack& s) : IntMaximizeSpace(s) {
    take.update(*this, s.take);
    value.update(*this, s.value);
  }
  Space* copy() override { return new Knapsack(*this); }
  IntVar cost() const override { return value; }  // maximised by BAB
  void print() const {
    std::cout << "Maximum value: " << value.val() << "\nItems:";
    for (int i = 0; i < take.size(); ++i)
      if (take[i].val()) std::cout << " " << i;
    std::cout << "\n";
  }
};

int main() {
  Search::Options opts;
  opts.threads = 1;
  opts.stop = Search::Stop::time(10000);  // milliseconds
  Knapsack* root = new Knapsack;
  BAB<Knapsack> engine(root, opts);
  delete root;
  Knapsack* best = nullptr;
  while (Knapsack* s = engine.next()) {
    delete best;
    best = s;
  }
  if (best == nullptr)
    std::cout << (engine.stopped() ? "Limit reached before a selection was found\n" : "No selection fits the capacity\n");
  else {
    best->print();
    if (engine.stopped()) std::cout << "(not proven optimal)\n";
  }
  delete best;
  return 0;
}
