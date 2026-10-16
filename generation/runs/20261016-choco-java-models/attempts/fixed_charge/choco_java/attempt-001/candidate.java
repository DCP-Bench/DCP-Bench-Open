// Fixed-charge production: make shirts, shorts and pants under labor and cloth capacities,
// where each product can be made only on its own machine, which must be rented at a fixed cost.
// Maximise profit from the products minus the renting cost of the machines.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int np = inst.getInt("num_products");
    int nm = inst.getInt("num_machines");
    int nr = inst.getIntArray("resources").length;
    int maxProd = inst.getInt("max_production");
    int[] capacity = inst.getIntArray("capacity");
    int[] rentingCost = inst.getIntArray("renting_cost");
    int[][] productRows = inst.getIntMatrix("product");  // row p: [profit, product id]
    int[][] use = inst.getIntMatrix("use");              // use[p][r]: amount of resource r per unit of p

    int[] profit = new int[np];
    for (int p = 0; p < np; p++) profit[p] = productRows[p][0];

    // the machine each product needs
    int[] machineOf = new int[np];
    machineOf[inst.getInt("shirt")] = inst.getInt("shirtM");
    machineOf[inst.getInt("shorts")] = inst.getInt("shortM");
    machineOf[inst.getInt("pants")] = inst.getInt("pantM");

    IntVar[] make = m.intVarArray("make", np, 0, maxProd);   // units of each product
    BoolVar[] rent = m.boolVarArray("rent", nm);             // 1 if the machine is rented

    // a product can be manufactured only by renting its machine (big-M link)
    for (int p = 0; p < np; p++) {
      m.scalar(new IntVar[]{make[p], rent[machineOf[p]]}, new int[]{1, -maxProd}, "<=", 0).post();
    }

    // the company has limited labor and cloth capacity
    for (int r = 0; r < nr; r++) {
      int[] coef = new int[np];
      for (int p = 0; p < np; p++) coef[p] = use[p][r];
      m.scalar(make, coef, "<=", capacity[r]).post();
    }

    // profit from the products minus the renting cost of the machines
    int lb = 0, ub = 0;
    for (int c : rentingCost) lb -= c;
    for (int p = 0; p < np; p++) ub += profit[p] * maxProd;
    IntVar z = m.intVar("z", lb, ub, true);
    IntVar[] vars = new IntVar[np + nm];
    int[] coef = new int[np + nm];
    for (int p = 0; p < np; p++) { vars[p] = make[p]; coef[p] = profit[p]; }
    for (int k = 0; k < nm; k++) { vars[np + k] = rent[k]; coef[np + k] = -rentingCost[k]; }
    m.scalar(vars, coef, "=", z).post();
    m.setObjective(Model.MAXIMIZE, z);

    out.put("z", z);
  }
}
