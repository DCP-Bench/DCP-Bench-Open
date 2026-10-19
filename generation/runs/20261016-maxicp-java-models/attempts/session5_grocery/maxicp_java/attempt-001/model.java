import java.util.ArrayList;
import java.util.List;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// A kid buys a number of items. The cashier charges a total price, in cents.
// The cashier multiplied the items instead of adding them, and the total comes to the
// same price. Find the prices of the items, in cents.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("num_items");
    int total = inst.getInt("total_price");
    if (n < 2) throw new IllegalArgumentException("at least two items");

    // the prices of the items, in cents, each at least one cent and at most the total
    CPIntVar[] prices = m.intVarArray(n, 1, total);

    // the cashier added the items: the prices add up to the total price
    m.cp().post(eq(sum(prices), total));

    // the cashier multiplied the items as dollar amounts: the product of the prices in
    // cents, divided by 100 for each item after the first, comes to the total price.
    // So the product of the prices in cents is total * 100^(n-1)
    long target = total;
    for (int i = 1; i < n; i++) target *= 100;

    // split the items in two groups; each group's product is kept small enough for an int
    int kA = n / 2;
    CPIntVar a = prices[0];
    for (int i = 1; i < kA; i++) a = mul(a, prices[i]);
    CPIntVar b = prices[kA];
    for (int i = kA + 1; i < n; i++) b = mul(b, prices[i]);

    // the two group products multiply to the target: list the pairs of values
    // within the range each group product can take that multiply to the target
    long maxA = 1;
    for (int i = 0; i < kA; i++) maxA *= total;
    long maxB = 1;
    for (int i = kA; i < n; i++) maxB *= total;
    List<int[]> rows = new ArrayList<>();
    for (long x = 1; x <= Math.min(maxA, target); x++) {
      if (target % x == 0 && target / x <= maxB) {
        rows.add(new int[] { (int) x, (int) (target / x) });
      }
    }
    m.cp().post(table(new CPIntVar[] { a, b }, rows.toArray(new int[0][])));

    out.put("prices", prices);
  }
}
