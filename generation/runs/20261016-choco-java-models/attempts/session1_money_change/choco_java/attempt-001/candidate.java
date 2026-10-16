import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Change making with limited coins: give the amount with the fewest coins,
// using at most the available number of coins of each type.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int amount = inst.getInt("amount");
    int[] values = inst.getIntArray("types_of_coins");
    int[] available = inst.getIntArray("available_coins");
    int n = values.length;

    // coin_counts[i]: number of coins of type i given to Bob
    // (bounded by the number of coins of that type Alice has available)
    IntVar[] coins = new IntVar[n];
    for (int i = 0; i < n; i++) {
      coins[i] = m.intVar("coins_" + values[i], 0, available[i]);
    }

    // the change given must add up to the amount
    m.scalar(coins, values, "=", amount).post();

    // the objective: minimise the total number of coins used
    IntVar total = m.sum("total", coins);
    m.setObjective(Model.MINIMIZE, total);

    out.put("coin_counts", coins);
  }
}
