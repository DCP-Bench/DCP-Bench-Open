// Capital budget: a company considers a number of investments. Each investment i yields
// a net present value npv[i] and needs a cash outflow cash_flow[i] now. The total budget
// is budget. Choose investments to maximize the total NPV obtained.
// Outputs: x[i] is true when investment i is chosen; z is the total NPV.
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] npv = inst.getIntArray("npv");
    int[] cashFlow = inst.getIntArray("cash_flow");
    int budget = inst.getInt("budget");
    int n = npv.length;

    // x[i] = 1 if investment i is chosen
    CPBoolVar[] x = m.boolVarArray(n);

    // total NPV of the chosen investments, bounded by the NPVs of the instance
    int lo = 0;
    int hi = 0;
    for (int i = 0; i < n; i++) {
      lo += Math.min(0, npv[i]);
      hi += Math.max(0, npv[i]);
    }
    CPIntVar z = m.intVar(lo, hi);

    // the sum of all chosen investments' cash flows must not exceed the budget
    CPIntVar[] outflow = new CPIntVar[n];
    for (int i = 0; i < n; i++) outflow[i] = mul(x[i], cashFlow[i]);
    m.cp().post(le(sum(outflow), budget));

    // z is the sum of the NPVs of the chosen investments
    CPIntVar[] payoff = new CPIntVar[n];
    for (int i = 0; i < n; i++) payoff[i] = mul(x[i], npv[i]);
    m.cp().post(eq(sum(payoff), z));

    // maximize the total NPV
    m.maximize(z);

    out.put("x", x);
    out.put("z", z);
  }
}
