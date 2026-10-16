import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Buy 100 fruits (bananas, oranges, mangoes, apples) for exactly 100 dollars, every
// type at least once. Bananas and apples should be bought in the smallest quantity.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // Prices from the statement, as dollars per fruit: banana 3/5, orange 5/7, mango 7/9,
    // apple 9/3 = 3. The common denominator is 315, so prices are scaled by 315 to be
    // integers, and the 100-dollar budget becomes 100 * 315 = 31500.
    final int SCALE = 315;
    final int[] price = {3 * SCALE / 5, 5 * SCALE / 7, 7 * SCALE / 9, 9 * SCALE / 3}; // banana, orange, mango, apple
    final int TOTAL_FRUITS = 100;
    final int TOTAL_DOLLARS = 100 * SCALE;

    IntVar bananas = m.intVar("bananas", 1, TOTAL_FRUITS);
    IntVar oranges = m.intVar("oranges", 1, TOTAL_FRUITS);
    IntVar mangoes = m.intVar("mangoes", 1, TOTAL_FRUITS);
    IntVar apples = m.intVar("apples", 1, TOTAL_FRUITS);
    IntVar[] fruits = {bananas, oranges, mangoes, apples};

    // 100 fruits in total
    m.sum(fruits, "=", TOTAL_FRUITS).post();

    // spend exactly 100 dollars (scaled)
    m.scalar(fruits, price, "=", TOTAL_DOLLARS).post();

    // all types of fruits need to be purchased: each quantity is at least 1 (domains above)

    // minimise the quantity of bananas and apples
    IntVar bananasAndApples = m.sum("bananasAndApples", new IntVar[]{bananas, apples});
    m.setObjective(Model.MINIMIZE, bananasAndApples);

    out.put("bananas", bananas);
    out.put("oranges", oranges);
    out.put("mangoes", mangoes);
    out.put("apples", apples);
  }
}
