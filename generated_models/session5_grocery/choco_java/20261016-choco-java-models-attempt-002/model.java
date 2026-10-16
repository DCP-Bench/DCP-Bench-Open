// Grocery prices: find the prices (in cents) of n items so that adding them gives the
// total price, and multiplying them (with each product scaled from cents to dollars)
// gives the same total. The cashier multiplied the cents instead of adding them.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {

  public static void build(Instance inst, Model m, Outputs out) {
    int total = inst.getInt("total_price");   // the total price, in cents
    int n = inst.getInt("num_items");         // number of items bought

    // 100^(n-1): the product of n prices in cents is 100^(n-1) times the total in cents
    int scale = 1;
    for (int k = 1; k < n; k++) scale *= 100;
    int target = total * scale;               // product of the prices, in cents^n / 100^(n-1)

    // price of each item in cents; a price is at least 1 cent and at most the total
    IntVar[] price = m.intVarArray("price", n, 1, total);

    // adding the items gives the total price
    m.sum(price, "=", total).post();

    // multiplying the items gives the same total, once scaled: the product of all prices
    // equals total * 100^(n-1). Partial products are at most the final product, since
    // every price is at least 1, so each one is bounded by the target.
    IntVar partial = price[0];
    for (int k = 1; k < n; k++) {
      IntVar next = m.intVar("product_" + (k + 1), 1, target, true);
      m.times(partial, price[k], next).post();
      partial = next;
    }
    m.arithm(partial, "=", target).post();

    // branch on the prices directly, cheapest first
    IntVar[] head = java.util.Arrays.copyOf(price, n - 1);
    m.getSolver().setSearch(Search.inputOrderLBSearch(head), Search.inputOrderLBSearch(price));

    out.put("prices", price);
  }
}
