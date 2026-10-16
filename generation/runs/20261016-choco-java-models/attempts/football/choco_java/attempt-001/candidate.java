import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Football: choose players from groups (goalkeepers, defenders, midfielders, strikers) with
// their prices, spending as much as possible without going over GBP 30 million, subject to
// the minimum numbers per group and at least eleven players in total. Prices are in GBP
// thousands (the problem's GBP millions times 1000, which is exact to three decimals).
// The prices and group minimums are fixed by the problem statement, not by the instance.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] gkPrice = {730, 1280, 3880};
    int[] defPrice = {920, 1310, 1620, 2410, 2790, 3280, 3910, 4570};
    int[] midPrice = {1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130};
    int[] strPrice = {4460, 6470, 7780, 8390, 9500};
    int budget = 30000; // GBP 30 million, in thousands

    // one Boolean per player: 1 if bought
    BoolVar[] gk = m.boolVarArray("gk", gkPrice.length);
    BoolVar[] def = m.boolVarArray("def", defPrice.length);
    BoolVar[] mid = m.boolVarArray("mid", midPrice.length);
    BoolVar[] str = m.boolVarArray("str", strPrice.length);
    BoolVar[] all = new BoolVar[gk.length + def.length + mid.length + str.length];
    int[] allPrice = new int[all.length];
    int k = 0;
    for (int i = 0; i < gk.length; i++, k++) { all[k] = gk[i]; allPrice[k] = gkPrice[i]; }
    for (int i = 0; i < def.length; i++, k++) { all[k] = def[i]; allPrice[k] = defPrice[i]; }
    for (int i = 0; i < mid.length; i++, k++) { all[k] = mid[i]; allPrice[k] = midPrice[i]; }
    for (int i = 0; i < str.length; i++, k++) { all[k] = str[i]; allPrice[k] = strPrice[i]; }

    // must buy 1 goalkeeper exactly
    m.sum(gk, "=", 1).post();

    // must buy 2 or more defenders
    m.sum(def, ">=", 2).post();

    // must buy 3 or more midfielders
    m.sum(mid, ">=", 3).post();

    // must buy 2 or more strikers
    m.sum(str, ">=", 2).post();

    // must buy at least eleven players in total
    m.sum(all, ">=", 11).post();

    // the purchases add up to no more than the chairman's limit of GBP 30 million
    m.scalar(all, allPrice, "<=", budget).post();

    // z: total price of the selected players, in GBP thousands
    IntVar z = m.intVar("z", 0, budget, true);
    m.scalar(all, allPrice, "=", z).post();
    m.setObjective(Model.MAXIMIZE, z);

    out.put("z", z);
  }
}
