#include "dcp.h"

// Aircraft assignment: assign the aircraft of each type to the routes so that every
// route's passenger demand is met, each type stays within its availability, and the
// total operational cost is minimised. allocation[i][j] = number of aircraft of
// type i assigned to route j.
class AircraftAssignment : public dcp::Space {
 protected:
  IntVarArray alloc;  // alloc[i * m + j]: aircraft of type i assigned to route j
  IntVar total;       // total operational cost

 public:
  explicit AircraftAssignment(const json& instance) {
    std::vector<int> availability = instance.at("availability").get<std::vector<int>>();
    std::vector<int> demand = instance.at("demand").get<std::vector<int>>();
    const json& capabilities = instance.at("capabilities");
    const json& costs = instance.at("costs");

    int n = static_cast<int>(availability.size());  // aircraft types
    int m = static_cast<int>(demand.size());        // routes

    // The number of aircraft of one type on one route cannot exceed that type's
    // availability; the per-type row sums below enforce the tighter bound.
    int max_avail = 0;
    for (int a : availability)
      if (a > max_avail) max_avail = a;
    alloc = IntVarArray(*this, n * m, 0, max_avail);

    // each aircraft type has a limited number of available units
    for (int i = 0; i < n; ++i) {
      IntVarArgs row;
      for (int j = 0; j < m; ++j) row << alloc[i * m + j];
      linear(*this, row, IRT_LQ, availability[i], IPL_BND);
    }

    // each route's passenger demand must be satisfied by the seats of the aircraft
    // assigned to it (capacity of type i on route j times the number of aircraft)
    for (int j = 0; j < m; ++j) {
      IntArgs seats(n);
      IntVarArgs assigned;
      for (int i = 0; i < n; ++i) {
        seats[i] = capabilities[i][j].get<int>();
        assigned << alloc[i * m + j];
      }
      linear(*this, seats, assigned, IRT_GQ, demand[j], IPL_BND);
    }

    // total operational cost: cost of each type on each route times the aircraft used
    IntArgs cost_coeffs(n * m);
    long long ub = 0;
    for (int i = 0; i < n; ++i) {
      for (int j = 0; j < m; ++j) {
        int c = costs[i][j].get<int>();
        cost_coeffs[i * m + j] = c;
        ub += static_cast<long long>(c) * availability[i];
      }
    }
    total = IntVar(*this, 0, static_cast<int>(ub));
    IntVarArgs all;
    for (int k = 0; k < n * m; ++k) all << alloc[k];
    linear(*this, cost_coeffs, all, IRT_EQ, total, IPL_BND);

    branch(*this, alloc, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    minimize(total);

    // allocation: one list per aircraft type, each holding one entry per route
    std::vector<IntVarArgs> allocation(n);
    for (int i = 0; i < n; ++i)
      for (int j = 0; j < m; ++j) allocation[i] << alloc[i * m + j];
    output("allocation", allocation);
  }

  AircraftAssignment(AircraftAssignment& s) : dcp::Space(s) {
    alloc.update(*this, s.alloc);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new AircraftAssignment(*this); }
};

DCP_MODEL(AircraftAssignment)
