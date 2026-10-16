import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// A bank van carried several kinds of coin bags, each kind holding a fixed number of coins.
// Some bags were stolen; the stolen bags held a given total number of coins.
// Find how many bags were stolen of each kind.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] coins = inst.getIntArray("coin_numbers");
    int total = inst.getInt("total_coins_lost");
    int kinds = coins.length;

    CPIntVar[] bags = new CPIntVar[kinds];
    CPIntVar[] stolenCoins = new CPIntVar[kinds];
    // the number of stolen bags of each kind is at most the number of such bags that fit in the total
    for (int i = 0; i < kinds; i++) {
      bags[i] = m.intVar(0, total / coins[i]);
      stolenCoins[i] = mul(bags[i], coins[i]);
    }
    // the stolen bags hold exactly the total number of coins lost
    m.cp().post(eq(sum(stolenCoins), total));

    out.put("bags", bags);
  }
}
