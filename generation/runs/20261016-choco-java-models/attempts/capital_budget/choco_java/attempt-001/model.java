import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Capital budget: choose which investments to make so that the total cash outflow
// stays within the budget, and the total net present value (NPV) is as large as possible.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int budget = inst.getInt("budget");
    int[] cashFlow = inst.getIntArray("cash_flow");
    int[] npv = inst.getIntArray("npv");
    int n = npv.length;

    // x[i] = 1 if investment i is chosen
    BoolVar[] x = m.boolVarArray("x", n);

    // the cash outflow of the chosen investments fits within the budget
    m.scalar(x, cashFlow, "<=", budget).post();

    // z is the total NPV of the chosen investments
    int totalNpv = 0;
    for (int v : npv) totalNpv += v;
    IntVar z = m.intVar("z", 0, totalNpv, true);
    m.scalar(x, npv, "=", z).post();

    // maximise the total NPV
    m.setObjective(Model.MAXIMIZE, z);

    out.put("x", x);
    out.put("z", z);
  }
}
