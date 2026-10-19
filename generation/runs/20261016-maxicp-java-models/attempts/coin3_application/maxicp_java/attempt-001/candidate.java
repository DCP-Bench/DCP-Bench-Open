// Coin application: find the minimum number of coins that allows one to pay exactly
// any amount smaller than a given maximum amount, using a given set of denominations.
// x[i] is the number of coins of denomination i used; minimize the total number of coins.
import java.util.ArrayList;
import java.util.List;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] denominations = inst.getIntArray("denominations");
    int maxAmount = inst.getInt("max_amount_to_pay");
    int n = denominations.length;

    // number of coins of each denomination used
    // any amount up to maxAmount - 1 uses at most (maxAmount - 1) / d coins of denomination d,
    // so an optimal solution never needs more
    CPIntVar[] x = new CPIntVar[n];
    for (int i = 0; i < n; i++) {
      x[i] = m.intVar(0, (maxAmount - 1) / denominations[i]);
    }

    // payable[i][a] is true when the amount a can be paid exactly with the first i
    // denominations, using at most x[j] coins of each denomination j < i
    // amount 0 is always payable with no coins
    CPBoolVar[][] payable = new CPBoolVar[n + 1][maxAmount];
    for (int a = 0; a < maxAmount; a++) {
      payable[0][a] = m.boolVar();
      m.cp().post(eq(payable[0][a], a == 0 ? 1 : 0));
    }

    for (int i = 1; i <= n; i++) {
      int d = denominations[i - 1];
      int maxCoins = (maxAmount - 1) / d;
      // coinAtLeast[k] is true when at least k coins of this denomination are available, k >= 1
      CPBoolVar[] coinAtLeast = new CPBoolVar[maxCoins + 1];
      for (int k = 1; k <= maxCoins; k++) {
        coinAtLeast[k] = not(isLe(x[i - 1], k - 1));
      }

      for (int a = 0; a < maxAmount; a++) {
        // the amount a is paid with k coins of this denomination and the rest with the earlier ones
        // one way to pay a is a term that is true when that way is available
        CPBoolVar result = m.boolVar();
        payable[i][a] = result;
        List<CPBoolVar> ways = new ArrayList<>();

        // no coin of this denomination: the earlier denominations pay a alone
        ways.add(payable[i - 1][a]);
        m.cp().post(implies(payable[i - 1][a], result));

        for (int k = 1; k * d <= a; k++) {
          int rest = a - k * d;
          // the earlier denominations pay the rest, and at least k coins are available
          CPBoolVar way = m.boolVar();
          m.cp().post(implies(way, payable[i - 1][rest]));
          m.cp().post(implies(way, coinAtLeast[k]));
          m.cp().post(or(new CPBoolVar[] {way, not(payable[i - 1][rest]), not(coinAtLeast[k])}));
          ways.add(way);
          m.cp().post(implies(way, result));
        }

        // an amount that is payable has at least one way to pay it
        List<CPBoolVar> need = new ArrayList<>(ways);
        need.add(not(result));
        m.cp().post(or(need.toArray(new CPBoolVar[0])));
      }
    }

    // every amount smaller than the maximum amount must be payable exactly
    // amounts are 1 .. maxAmount - 1
    for (int a = 1; a < maxAmount; a++) {
      m.cp().post(eq(payable[n][a], 1));
    }

    // minimize the total number of coins used
    m.minimize(sum(x));

    out.put("x", x);
  }
}
