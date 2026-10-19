// Shift roster read from JSON: give every worker a shift (0 off, 1 day, 2 night) on
// every day so that each day's demand is met, no one works a day shift right after a
// night, nights come in runs of at most two, nobody works on their days off, and the
// total cost of the roster is minimal.
// Usage: ./model [data.json]   (default data.json)
// Shows nlohmann/json input, Matrix, gcc (count with cardinality sets), a regular
// expression (DFA), element over a cost table, and BAB.
#include <gecode/int.hh>
#include <gecode/minimodel.hh>
#include <gecode/search.hh>
#include <nlohmann/json.hpp>
#include <fstream>
#include <iostream>
#include <vector>
using namespace Gecode;
using nlohmann::json;

class Roster : public IntMinimizeSpace {
 protected:
  int workers, days;
  IntVarArray shift;  // workers x days, row-major: shift[w * days + d]
  IntVar total;

 public:
  explicit Roster(const json& data) {
    // every size comes from the data; keys the model does not use are ignored
    workers = data.at("workers").get<int>();
    days = data.at("demand").size();
    int max_nights = data.at("max_nights").get<int>();
    shift = IntVarArray(*this, workers * days, 0, 2);
    Matrix<IntVarArray> m(shift, days, workers);  // m(day, worker): column first

    // each day needs exactly demand[d] = [day shifts, night shifts]; the rest are off
    for (int d = 0; d < days; ++d) {
      int day = data.at("demand")[d][0].get<int>(), night = data.at("demand")[d][1].get<int>();
      count(*this, m.col(d), IntSetArgs({IntSet(0, workers), IntSet(day, day), IntSet(night, night)}),
            IntArgs({0, 1, 2}));
    }

    // no day shift right after a night, and at most two nights in a row
    REG off(0), early(1), night(2);
    DFA rules(*(off | early | night(1, 2) + off) + night(0, 2));
    for (int w = 0; w < workers; ++w) extensional(*this, m.row(w), rules);

    // a worker has at most max_nights nights in the period
    for (int w = 0; w < workers; ++w) count(*this, m.row(w), 2, IRT_LQ, max_nights);

    // days_off[w] lists the days worker w cannot work (a ragged list)
    const json& days_off = data.at("days_off");
    for (int w = 0; w < workers; ++w)
      for (const auto& d : days_off[w]) rel(*this, m(d.get<int>(), w) == 0);

    // cost[w] = [day shift cost, night shift cost]; minimise the total
    IntVarArgs costs;
    for (int w = 0; w < workers; ++w) {
      IntArgs price({0, data.at("cost")[w][0].get<int>(), data.at("cost")[w][1].get<int>()});
      for (int d = 0; d < days; ++d) costs << expr(*this, element(price, m(d, w)));
    }
    total = expr(*this, sum(costs));

    branch(*this, shift, INT_VAR_AFC_SIZE_MAX(0.99), INT_VAL_MIN());
  }
  Roster(Roster& s) : IntMinimizeSpace(s), workers(s.workers), days(s.days) {
    shift.update(*this, s.shift);
    total.update(*this, s.total);
  }
  Space* copy() override { return new Roster(*this); }
  IntVar cost() const override { return total; }
  void print() const {
    std::cout << "Total cost: " << total.val() << "\n";
    for (int w = 0; w < workers; ++w) {
      std::cout << "  worker " << w << ":";
      for (int d = 0; d < days; ++d) std::cout << " " << ".DN"[shift[w * days + d].val()];
      std::cout << "\n";
    }
  }
};

int main(int argc, char* argv[]) {
  const char* path = argc > 1 ? argv[1] : "data.json";
  std::ifstream in(path);
  if (!in) {
    std::cerr << "cannot open " << path << "\n";
    return 1;
  }
  json data = json::parse(in);  // throws json::parse_error on malformed input

  Roster* root = new Roster(data);
  BAB<Roster> engine(root);
  delete root;
  Roster* best = nullptr;
  while (Roster* s = engine.next()) {
    delete best;
    best = s;
  }
  if (best == nullptr) {
    std::cout << (engine.stopped() ? "Stopped, no roster" : "No roster exists") << "\n";
    return 0;
  }
  best->print();
  if (engine.stopped()) std::cout << "(not proven optimal)\n";
  delete best;
  return 0;
}
