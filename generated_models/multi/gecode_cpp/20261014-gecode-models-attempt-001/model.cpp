#include "dcp.h"

// Multi-commodity transportation: ship every product from the origins to the
// destinations at minimum total shipping cost.
class Multi : public dcp::Space {
 protected:
  IntVarArray x;     // x[(i*J + j)*P + p]: units of product p shipped from origin i to destination j
  IntVar total_cost; // total shipping cost of all shipments

  static int idx(int i, int j, int p, int J, int P) { return (i * J + j) * P + p; }

 public:
  explicit Multi(const json& instance) {
    std::vector<std::vector<int>> supply = instance.at("supply").get<std::vector<std::vector<int>>>();
    std::vector<std::vector<int>> demand = instance.at("demand").get<std::vector<std::vector<int>>>();
    std::vector<std::vector<int>> limit = instance.at("limit").get<std::vector<std::vector<int>>>();
    std::vector<std::vector<std::vector<int>>> cost =
        instance.at("cost").get<std::vector<std::vector<std::vector<int>>>>();

    int I = static_cast<int>(supply.size());      // origins
    int J = static_cast<int>(demand.size());      // destinations
    int P = static_cast<int>(supply[0].size());   // products
    int n = I * J * P;

    // one variable per (origin, destination, product), bounded by what the
    // origin can send, what the destination can take and the lane limit
    IntVarArgs xs;
    for (int i = 0; i < I; ++i)
      for (int j = 0; j < J; ++j)
        for (int p = 0; p < P; ++p) {
          int ub = std::min({supply[i][p], demand[j][p], limit[i][j]});
          xs << IntVar(*this, 0, ub);
        }
    x = IntVarArray(*this, xs);

    // an origin cannot ship more of a product than its supply of that product
    for (int i = 0; i < I; ++i)
      for (int p = 0; p < P; ++p) {
        IntVarArgs out;
        for (int j = 0; j < J; ++j) out << x[idx(i, j, p, J, P)];
        linear(*this, out, IRT_LQ, supply[i][p]);
      }

    // a destination receives exactly its demand of each product
    for (int j = 0; j < J; ++j)
      for (int p = 0; p < P; ++p) {
        IntVarArgs in;
        for (int i = 0; i < I; ++i) in << x[idx(i, j, p, J, P)];
        linear(*this, in, IRT_EQ, demand[j][p]);
      }

    // the lane from an origin to a destination carries at most its limit, all products together
    for (int i = 0; i < I; ++i)
      for (int j = 0; j < J; ++j) {
        IntVarArgs lane;
        for (int p = 0; p < P; ++p) lane << x[idx(i, j, p, J, P)];
        linear(*this, lane, IRT_LQ, limit[i][j]);
      }

    // total cost: each unit shipped costs ShippingCost[i][j][p]
    IntArgs unit_cost(n);
    IntVarArgs all;
    for (int i = 0; i < I; ++i)
      for (int j = 0; j < J; ++j)
        for (int p = 0; p < P; ++p) {
          int k = idx(i, j, p, J, P);
          unit_cost[k] = cost[i][j][p];
          all << x[k];
        }
    total_cost = expr(*this, sum(unit_cost, all));

    branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    minimize(total_cost);
    output("total_cost", total_cost);
  }

  Multi(Multi& s) : dcp::Space(s) {
    x.update(*this, s.x);
    total_cost.update(*this, s.total_cost);
  }
  Gecode::Space* copy() override { return new Multi(*this); }
};

DCP_MODEL(Multi)
