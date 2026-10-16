#include "dcp.h"

#include <algorithm>
#include <stdexcept>

// Facility location: decide which candidate warehouses to open and how many
// units each opened warehouse ships to each region, so that the total of the
// fixed opening costs and the shipping costs is minimal.
class FacilityLocation : public dcp::Space {
 protected:
  BoolVarArray opened;  // opened[i]: warehouse i is opened
  IntVarArray ships;    // ships[i * R + j]: units shipped from warehouse i to region j
  IntVar total;         // total cost

 public:
  explicit FacilityLocation(const json& instance) {
    std::vector<std::string> names = instance.at("warehouse_s").get<std::vector<std::string>>();
    std::vector<int> fixed = instance.at("fixed_costs").get<std::vector<int>>();
    std::vector<int> demands = instance.at("demands").get<std::vector<int>>();
    std::vector<std::vector<int>> cost =
        instance.at("shipping_costs").get<std::vector<std::vector<int>>>();
    int max_shipping = instance.at("max_shipping").get<int>();

    const int W = static_cast<int>(fixed.size());    // candidate warehouses
    const int R = static_cast<int>(demands.size());  // regions

    // index of a city in the instance's warehouse list
    auto city = [&names](const std::string& name) {
      auto it = std::find(names.begin(), names.end(), name);
      if (it == names.end()) throw std::invalid_argument("unknown warehouse " + name);
      return static_cast<int>(it - names.begin());
    };
    const int ny = city("New York");
    const int la = city("Los Angeles");
    const int atl = city("Atlanta");

    opened = BoolVarArray(*this, W, 0, 1);
    ships = IntVarArray(*this, W * R, 0, max_shipping);

    // the same warehouse decisions as 0/1 integers, for the sums below
    IntVarArray o(*this, W, 0, 1);
    for (int i = 0; i < W; ++i) channel(*this, opened[i], o[i]);

    // if the New York warehouse is opened, the Los Angeles warehouse must also be opened
    rel(*this, opened[ny], IRT_LQ, opened[la]);

    // no more than three warehouses can be operational in any given week
    BoolVarArgs operational;
    for (int i = 0; i < W; ++i) operational << opened[i];
    linear(*this, operational, IRT_LQ, 3);

    // either the Atlanta or the Los Angeles warehouse must be opened
    rel(*this, opened[la], BOT_OR, opened[atl], 1);

    // an opened warehouse ships at most max_shipping units in total,
    // a closed warehouse ships nothing
    for (int i = 0; i < W; ++i) {
      IntVarArgs x;
      IntArgs c;
      for (int j = 0; j < R; ++j) {
        x << ships[i * R + j];
        c << 1;
      }
      x << o[i];
      c << -max_shipping;
      linear(*this, c, x, IRT_LQ, 0);
    }

    // the demand of every region is met exactly
    for (int j = 0; j < R; ++j) {
      IntVarArgs x;
      for (int i = 0; i < W; ++i) x << ships[i * R + j];
      linear(*this, x, IRT_EQ, demands[j]);
    }

    // total cost: fixed costs of the opened warehouses plus units times shipping cost
    int upper = 0;
    for (int i = 0; i < W; ++i) upper += fixed[i];
    for (int j = 0; j < R; ++j) {
      int worst = 0;
      for (int i = 0; i < W; ++i) worst = std::max(worst, cost[i][j]);
      upper += demands[j] * worst;
    }
    IntVarArgs x;
    IntArgs c;
    for (int i = 0; i < W; ++i) {
      x << o[i];
      c << fixed[i];
    }
    for (int i = 0; i < W; ++i) {
      for (int j = 0; j < R; ++j) {
        x << ships[i * R + j];
        c << cost[i][j];
      }
    }
    total = IntVar(*this, 0, upper);
    linear(*this, c, x, IRT_EQ, total);

    branch(*this, opened, BOOL_VAR_NONE(), BOOL_VAL_MIN());
    branch(*this, ships, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    minimize(total);

    output("open_warehouse", opened);
    output("ships", Matrix<IntVarArray>(ships, R, W));
    output("total_cost", total);
  }

  FacilityLocation(FacilityLocation& s) : dcp::Space(s) {
    opened.update(*this, s.opened);
    ships.update(*this, s.ships);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new FacilityLocation(*this); }
};

DCP_MODEL(FacilityLocation)
