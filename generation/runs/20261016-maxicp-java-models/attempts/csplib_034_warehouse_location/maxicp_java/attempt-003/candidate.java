// Warehouse Location: choose which warehouses to open so that every store is
// supplied by exactly one open warehouse, within each warehouse's capacity,
// minimising the maintenance cost of opened warehouses plus the supply costs.
// Encoding: a Boolean per (store, warehouse) pair for the assignment and the
// capacity counts, and an element constraint per store for its supply cost,
// because element bounds the cost from the remaining supplier choices.
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int nWarehouses = inst.getInt("n_suppliers");
    int nStores = inst.getInt("n_stores");
    int buildingCost = inst.getInt("building_cost");
    int[] capacity = inst.getIntArray("capacity");
    int[][] costMatrix = inst.getIntMatrix("cost_matrix"); // costMatrix[store][warehouse]

    // open[w] = 1 if warehouse w is opened
    CPBoolVar[] open = m.boolVarArray(nWarehouses);
    // assign[s][w] = 1 if store s is supplied by warehouse w
    CPBoolVar[][] assign = new CPBoolVar[nStores][];
    for (int s = 0; s < nStores; s++) {
      assign[s] = m.boolVarArray(nWarehouses);
    }

    // every store is supplied by exactly one warehouse
    for (int s = 0; s < nStores; s++) {
      CPIntVar[] choices = new CPIntVar[nWarehouses];
      for (int w = 0; w < nWarehouses; w++) choices[w] = assign[s][w];
      m.cp().post(eq(sum(choices), 1));
    }

    // a store can only be supplied by a warehouse that is open
    for (int s = 0; s < nStores; s++) {
      for (int w = 0; w < nWarehouses; w++) {
        m.cp().post(implies(assign[s][w], open[w]));
      }
    }

    // the number of stores a warehouse supplies is at most its capacity,
    // and no stores are supplied by a warehouse that is not open
    for (int w = 0; w < nWarehouses; w++) {
      CPIntVar[] storesOfW = new CPIntVar[nStores];
      for (int s = 0; s < nStores; s++) storesOfW[s] = assign[s][w];
      m.cp().post(le(sum(storesOfW), mul(open[w], capacity[w])));
    }

    // all stores must be supplied, so the open warehouses must have enough capacity
    // in total for every store
    CPIntVar[] openCapacity = new CPIntVar[nWarehouses];
    for (int w = 0; w < nWarehouses; w++) openCapacity[w] = mul(open[w], capacity[w]);
    m.cp().post(ge(sum(openCapacity), nStores));

    // supplier index of each store: the warehouse it is assigned to (0-based)
    CPIntVar[] supplier = new CPIntVar[nStores];
    for (int s = 0; s < nStores; s++) {
      CPIntVar[] weighted = new CPIntVar[nWarehouses];
      for (int w = 0; w < nWarehouses; w++) weighted[w] = mul(assign[s][w], w);
      supplier[s] = sum(weighted);
    }

    // total cost = maintenance cost of opened warehouses + supply cost of each store
    CPIntVar[] terms = new CPIntVar[nWarehouses + nStores];
    for (int w = 0; w < nWarehouses; w++) {
      terms[w] = mul(open[w], buildingCost);
    }
    for (int s = 0; s < nStores; s++) {
      terms[nWarehouses + s] = element(costMatrix[s], supplier[s]);
    }
    CPIntVar totalCost = sum(terms);
    m.minimize(totalCost);

    out.put("open_warehouses", open);
    out.put("supplier_assignment", supplier);
    out.put("total_cost", totalCost);
  }
}
