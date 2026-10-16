#include "dcp.h"

// Warehouse location: choose which warehouses to open so that every store is
// supplied by exactly one open warehouse, within each warehouse's capacity,
// minimising the maintenance costs of the opened warehouses plus the supply
// costs of all stores.
class WarehouseLocation : public dcp::Space {
 protected:
  int warehouses;     // n_suppliers
  int stores;         // n_stores
  BoolVarArray open;  // open[w]: warehouse w is open
  BoolVarArray y;     // y[s * warehouses + w]: store s is supplied by warehouse w
  IntVarArray assign; // assign[s]: warehouse supplying store s
  IntVar fixedTotal;  // maintenance cost of the open warehouses
  IntVar supplyTotal; // supply cost of all stores
  IntVar total;       // total cost

 public:
  explicit WarehouseLocation(const json& instance) {
    warehouses = instance.at("n_suppliers").get<int>();
    stores = instance.at("n_stores").get<int>();
    int buildingCost = instance.at("building_cost").get<int>();
    std::vector<int> capacity = instance.at("capacity").get<std::vector<int>>();
    std::vector<std::vector<int>> cost =
        instance.at("cost_matrix").get<std::vector<std::vector<int>>>();

    open = BoolVarArray(*this, warehouses, 0, 1);
    y = BoolVarArray(*this, stores * warehouses, 0, 1);
    assign = IntVarArray(*this, stores, 0, warehouses - 1);

    // every store is supplied by exactly one warehouse: a one-hot link
    // between the store's supplier and its row of y
    for (int s = 0; s < stores; ++s) {
      BoolVarArgs row;
      for (int w = 0; w < warehouses; ++w) row << y[s * warehouses + w];
      channel(*this, row, assign[s]);
    }

    // a store is supplied only by an open warehouse
    for (int s = 0; s < stores; ++s)
      for (int w = 0; w < warehouses; ++w)
        rel(*this, y[s * warehouses + w], IRT_LQ, open[w]);

    // each warehouse supplies at most its capacity of stores
    for (int w = 0; w < warehouses; ++w) {
      BoolVarArgs column;
      for (int s = 0; s < stores; ++s) column << y[s * warehouses + w];
      linear(*this, column, IRT_LQ, capacity[w]);
    }

    // supply cost of each store depends on the store and the warehouse
    IntArgs supplyCosts(stores * warehouses);
    int maxSupply = 0;
    for (int s = 0; s < stores; ++s)
      for (int w = 0; w < warehouses; ++w) {
        supplyCosts[s * warehouses + w] = cost[s][w];
        maxSupply += cost[s][w];
      }
    supplyTotal = IntVar(*this, 0, maxSupply);
    linear(*this, supplyCosts, y, IRT_EQ, supplyTotal);

    // each opened warehouse costs the building cost
    fixedTotal = IntVar(*this, 0, warehouses * buildingCost);
    linear(*this, IntArgs::create(warehouses, buildingCost, 0), open, IRT_EQ, fixedTotal);

    // minimise the total cost: maintenance plus supply
    IntVarArgs parts;
    parts << fixedTotal << supplyTotal;
    total = IntVar(*this, 0, warehouses * buildingCost + maxSupply);
    linear(*this, parts, IRT_EQ, total);

    branch(*this, open, BOOL_VAR_NONE(), BOOL_VAL_MIN());
    branch(*this, assign, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    minimize(total);
    output("open_warehouses", open);
    output("supplier_assignment", assign);
    output("total_cost", total);
  }

  WarehouseLocation(WarehouseLocation& s) : dcp::Space(s) {
    warehouses = s.warehouses;
    stores = s.stores;
    open.update(*this, s.open);
    y.update(*this, s.y);
    assign.update(*this, s.assign);
    fixedTotal.update(*this, s.fixedTotal);
    supplyTotal.update(*this, s.supplyTotal);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new WarehouseLocation(*this); }
};

DCP_MODEL(WarehouseLocation)
