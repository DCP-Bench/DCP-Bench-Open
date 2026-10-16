import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Alice gives Bob change with coins of several types. Each type has a value and a
// limited number of available coins. Choose how many coins of each type to give so
// that the coins add up to the amount, using as few coins as possible.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int amount = inst.getInt("amount");
    int[] values = inst.getIntArray("types_of_coins");
    int[] available = inst.getIntArray("available_coins");
    int n = values.length;

    int totalAvailable = 0;
    for (int a : available) totalAvailable += a;

    // the number of coins of each type given to Bob, at most the number available of that type
    CPIntVar[] counts = new CPIntVar[n];
    for (int i = 0; i < n; i++) counts[i] = m.intVar(0, available[i]);

    // the coins given add up to the amount
    CPIntVar[] worth = new CPIntVar[n];
    for (int i = 0; i < n; i++) worth[i] = mul(counts[i], values[i]);
    m.cp().post(eq(sum(worth), amount));

    // the number of coins used is minimised
    CPIntVar coins = m.intVar(0, totalAvailable);
    m.cp().post(eq(coins, sum(counts)));
    m.minimize(coins);

    out.put("coin_counts", counts);
  }
}
