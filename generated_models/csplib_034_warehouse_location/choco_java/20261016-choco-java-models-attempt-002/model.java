import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.limits.FailCounter;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Warehouse location: choose which warehouses to open and assign each store to one open
// warehouse, within each warehouse's capacity, minimising the maintenance costs of the open
// warehouses plus the supply costs of the stores.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int stores = inst.getInt("n_stores");
    int warehouses = inst.getInt("n_suppliers");
    int buildingCost = inst.getInt("building_cost");
    int[] capacity = inst.getIntArray("capacity");
    int[][] costMatrix = inst.getIntMatrix("cost_matrix");

    // assign[s] is the warehouse that supplies store s
    IntVar[] assign = m.intVarArray("assign", stores, 0, warehouses - 1);

    // load[w] is the number of stores supplied by warehouse w, at most its capacity
    IntVar[] load = new IntVar[warehouses];
    for (int w = 0; w < warehouses; w++) {
      load[w] = m.intVar("load" + w, 0, capacity[w]);
    }

    // each store is supplied by exactly one warehouse, and every warehouse stays within capacity
    int[] values = new int[warehouses];
    for (int w = 0; w < warehouses; w++) values[w] = w;
    m.globalCardinality(assign, values, load, true).post();

    // a warehouse is open when it supplies at least one store
    BoolVar[] open = new BoolVar[warehouses];
    for (int w = 0; w < warehouses; w++) {
      open[w] = load[w].gt(0).boolVar();
    }

    // a store is supplied only by an open warehouse: open[assign[s]] = 1
    IntVar one = m.intVar(1);
    for (int s = 0; s < stores; s++) {
      m.element(one, open, assign[s], 0).post();
    }

    // supply cost of each store from its assigned warehouse
    IntVar[] supply = new IntVar[stores];
    int lowerBound = 0;
    for (int s = 0; s < stores; s++) {
      supply[s] = m.intVar("supply" + s, 0, 100, true);
      m.element(supply[s], costMatrix[s], assign[s], 0).post();
      int cheapest = Integer.MAX_VALUE;
      for (int c : costMatrix[s]) cheapest = Math.min(cheapest, c);
      lowerBound += cheapest;
    }

    // total cost: maintenance cost of each open warehouse plus supply cost of all stores
    int[] weights = new int[warehouses + stores];
    IntVar[] terms = new IntVar[warehouses + stores];
    for (int w = 0; w < warehouses; w++) {
      terms[w] = open[w];
      weights[w] = buildingCost;
    }
    for (int s = 0; s < stores; s++) {
      terms[warehouses + s] = supply[s];
      weights[warehouses + s] = 1;
    }
    IntVar total = m.intVar("total_cost", 0, 100000, true);
    m.scalar(terms, weights, "=", total).post();

    // implied bound: the total is at least the cheapest supply cost of every store
    m.arithm(total, ">=", lowerBound).post();
    m.setObjective(Model.MINIMIZE, total);

    // branch on the store assignments first, with conflict history and Luby restarts
    m.getSolver().setSearch(Search.lastConflict(Search.domOverWDegSearch(assign)));
    m.getSolver().setLubyRestart(50, new FailCounter(m, 1), 10000);

    out.put("open_warehouses", open);
    out.put("supplier_assignment", assign);
    out.put("total_cost", total);
  }
}
