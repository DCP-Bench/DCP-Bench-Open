#include "dcp.h"

// Project assignment (network assignment): assign hours from people to projects
// so that each person i supplies exactly Supply_i hours, each project j receives
// exactly Demand_j hours, no pair (i, j) exceeds Limit_ij hours, and the total
// cost sum Cost_ij * hours_ij is minimised.
class NetAssign : public dcp::Space {
 protected:
  int np;                 // number of people
  int nq;                 // number of projects
  IntVarArray x;          // x[i * nq + j]: hours assigned from person i to project j
  IntVar total;           // total cost of the assignment

 public:
  explicit NetAssign(const json& instance) {
    std::vector<int> supply = instance.at("supply").get<std::vector<int>>();
    std::vector<int> demand = instance.at("demand").get<std::vector<int>>();
    np = static_cast<int>(supply.size());
    nq = static_cast<int>(demand.size());

    std::vector<std::vector<int>> cost(np, std::vector<int>(nq));
    std::vector<std::vector<int>> limit(np, std::vector<int>(nq));
    for (int i = 0; i < np; ++i)
      for (int j = 0; j < nq; ++j) {
        cost[i][j] = instance.at("cost")[i][j].get<int>();
        limit[i][j] = instance.at("limit")[i][j].get<int>();
      }

    int max_limit = 0;
    for (int i = 0; i < np; ++i)
      for (int j = 0; j < nq; ++j) max_limit = std::max(max_limit, limit[i][j]);

    // hours are non-negative, and person i contributes at most Limit_ij to project j
    x = IntVarArray(*this, np * nq, 0, max_limit);
    for (int i = 0; i < np; ++i)
      for (int j = 0; j < nq; ++j) rel(*this, x[i * nq + j] <= limit[i][j]);

    // person i supplies exactly its supply
    for (int i = 0; i < np; ++i) {
      IntVarArgs row;
      for (int j = 0; j < nq; ++j) row << x[i * nq + j];
      linear(*this, row, IRT_EQ, supply[i]);
    }

    // project j receives exactly its demand
    for (int j = 0; j < nq; ++j) {
      IntVarArgs col;
      for (int i = 0; i < np; ++i) col << x[i * nq + j];
      linear(*this, col, IRT_EQ, demand[j]);
    }

    // total cost of the assignment
    IntArgs weights(np * nq);
    for (int i = 0; i < np; ++i)
      for (int j = 0; j < nq; ++j) weights[i * nq + j] = cost[i][j];
    total = expr(*this, sum(weights, x));

    // decide every assignment, smallest domain first
    branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    minimize(total);

    // outputs: assign[i][j] per person row, and the total cost
    std::vector<IntVarArgs> rows(np);
    for (int i = 0; i < np; ++i)
      for (int j = 0; j < nq; ++j) rows[i] << x[i * nq + j];
    output("assign", rows);
    output("total_cost", total);
  }

  NetAssign(NetAssign& s) : dcp::Space(s), np(s.np), nq(s.nq) {
    x.update(*this, s.x);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new NetAssign(*this); }
};

DCP_MODEL(NetAssign)
