// Warehouse Location: choose which warehouses to open so that every store is
// supplied by exactly one open warehouse, within each warehouse's capacity,
// minimising the maintenance cost of opened warehouses plus the supply costs.
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
    // supplier[s] = warehouse that supplies store s
    CPIntVar[] supplier = m.intVarArray(nStores, 0, nWarehouses - 1);

    // every store is supplied by exactly one warehouse, and that warehouse is open:
    // store s is supplied by warehouse w only if warehouse w is open
    CPBoolVar[][] suppliedBy = new CPBoolVar[nStores][nWarehouses];
    for (int s = 0; s < nStores; s++) {
      for (int w = 0; w < nWarehouses; w++) {
        suppliedBy[s][w] = isEq(supplier[s], w);
        m.cp().post(implies(suppliedBy[s][w], open[w]));
      }
    }

    // the number of stores a warehouse supplies is at most its capacity
    for (int w = 0; w < nWarehouses; w++) {
      CPIntVar[] storesOfW = new CPIntVar[nStores];
      for (int s = 0; s < nStores; s++) storesOfW[s] = suppliedBy[s][w];
      m.cp().post(le(sum(storesOfW), capacity[w]));
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
