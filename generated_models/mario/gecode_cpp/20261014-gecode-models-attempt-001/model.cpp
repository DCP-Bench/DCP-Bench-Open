#include "dcp.h"

// Mario: Mario starts at his house and drives to Luigi's house, visiting other houses
// on the way to collect their gold. Every drive costs fuel, and the total fuel of the
// route must not exceed the fuel limit. Maximise the gold collected. Output s[i] is the
// house after house i on the route (s[i] = i if house i is not on the route); s[Luigi]
// is Mario's house, which closes the route into a cycle.
class Mario : public dcp::Space {
 protected:
  IntVarArray succ;  // succ[i]: house after house i (succ[i] = i: not on the route)
  IntVarArray ord;   // ord[i]: position of house i on the route, counted from Mario's house
  IntVarArray t;     // t[i] = ord[succ[i]], the position of the successor of house i
  IntVar gold;       // total gold collected on the route

 public:
  explicit Mario(const json& instance) {
    int n = instance.at("nHouses");
    int mario = instance.at("marioHouse");
    int luigi = instance.at("luigiHouse");
    int fuel_limit = instance.at("fuelLimit");
    std::vector<std::vector<int>> arc_fuel = instance.at("arc_fuel").get<std::vector<std::vector<int>>>();
    std::vector<int> gold_in = instance.at("goldInHouse");

    succ = IntVarArray(*this, n, 0, n - 1);
    ord = IntVarArray(*this, n, 0, n - 1);
    t = IntVarArray(*this, n, 0, n - 1);

    // the successors form a permutation: each house is the successor of exactly one house
    distinct(*this, succ, IPL_DOM);

    // Mario's house is on the route and leads somewhere else
    rel(*this, succ[mario] != mario);
    // the route ends at Luigi's house, which goes back to Mario's house
    rel(*this, succ[luigi] == mario);

    // the route is one path from Mario's house, so it cannot close without him:
    // positions along the route increase by one from each house to the next
    rel(*this, ord[mario] == 0);
    for (int i = 0; i < n; ++i) {
      element(*this, ord, succ[i], t[i]);
      // a house off the route has position 0; a house on it has position one more than its predecessor
      rel(*this, (succ[i] == i) >> (ord[i] == 0));
      rel(*this, (succ[i] == i) || (succ[i] == mario) || (t[i] == ord[i] + 1));
    }

    // fuel of each drive; a house off the route drives nowhere, so its cost is 0
    IntVarArgs fuel;
    for (int i = 0; i < n; ++i) {
      std::vector<int> row = arc_fuel[i];
      row[i] = 0;  // self-loop: house not on the route, no fuel
      int row_max = 0;
      for (int c : row) row_max = std::max(row_max, c);
      IntVar f(*this, 0, row_max);
      element(*this, IntArgs(row), succ[i], f);
      fuel << f;
    }
    // the total fuel of the route stays within the limit
    linear(*this, fuel, IRT_LQ, fuel_limit);

    // a house is visited when it is on the route; gold is collected at each visited house
    BoolVarArgs visited;
    int gold_max = 0;
    for (int i = 0; i < n; ++i) {
      visited << expr(*this, succ[i] != i);
      gold_max += gold_in[i];
    }
    gold = IntVar(*this, 0, gold_max);
    linear(*this, IntArgs(gold_in), visited, IRT_EQ, gold);

    // branch on the successors, which decide the whole route; positions follow from them
    branch(*this, succ, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, ord, INT_VAR_NONE(), INT_VAL_MIN());
    branch(*this, t, INT_VAR_NONE(), INT_VAL_MIN());

    maximize(gold);
    output("s", succ);
  }

  Mario(Mario& s) : dcp::Space(s) {
    succ.update(*this, s.succ);
    ord.update(*this, s.ord);
    t.update(*this, s.t);
    gold.update(*this, s.gold);
  }
  Gecode::Space* copy() override { return new Mario(*this); }
};

DCP_MODEL(Mario)
