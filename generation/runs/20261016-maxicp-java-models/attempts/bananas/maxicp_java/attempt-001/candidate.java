// Fruit purchase: buy bananas, oranges, mangoes and apples so that exactly
// 100 fruits are bought for exactly 100 dollars. All types of fruit must be
// bought, and the quantities of bananas and apples must be as small as possible.
// Prices per fruit: 5 bananas cost 3 dollars (0.6 each), 7 oranges cost 5 dollars,
// 9 mangoes cost 7 dollars, 3 apples cost 9 dollars.
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // quantities of each fruit, a whole number of fruits, at least one of each type
    // since all types of fruit need to be purchased
    CPIntVar bananas = m.intVar(1, 100);
    CPIntVar oranges = m.intVar(1, 100);
    CPIntVar mangoes = m.intVar(1, 100);
    CPIntVar apples = m.intVar(1, 100);

    // I need to purchase 100 fruits in total
    m.cp().post(eq(sum(bananas, oranges, mangoes, apples), 100));

    // the fruits cost 100 dollars in total. Prices per fruit are 3/5, 5/7, 7/9 and 9/3
    // dollars. Multiplying every price by 315 (the lcm of 5, 7, 9 and 3) gives whole
    // coefficients: 189, 225, 245 and 945, and the budget becomes 100 * 315 = 31500.
    m.cp().post(eq(sum(mul(bananas, 189), mul(oranges, 225), mul(mangoes, 245), mul(apples, 945)), 31500));

    // minimize the number of bananas and apples bought
    m.minimize(sum(bananas, apples));

    out.put("apples", apples);
    out.put("bananas", bananas);
    out.put("mangoes", mangoes);
    out.put("oranges", oranges);
  }
}
