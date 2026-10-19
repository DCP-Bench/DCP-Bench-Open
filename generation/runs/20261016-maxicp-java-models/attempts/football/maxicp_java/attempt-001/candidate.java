// Football squad selection: spend as much as possible on Premiership players
// without going over GBP 30 million, under the position minimums in the statement.
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {

  // Prices from the statement, in GBP thousands (the statement gives millions to three decimals).
  static final int[] GOALKEEPER_PRICE = {730, 1280, 3880};                            // g1..g3
  static final int[] DEFENDER_PRICE = {920, 1310, 1620, 2410, 2790, 3280, 3910, 4570}; // d1..d8
  static final int[] MIDFIELDER_PRICE = {1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130}; // m1..m10
  static final int[] STRIKER_PRICE = {4460, 6470, 7780, 8390, 9500};                  // s1..s5

  // Each listed player is bought at most once: one Boolean per player.
  // The price of a bought player is its price times its Boolean.
  static CPIntVar[] priced(CPBoolVar[] bought, int[] price) {
    CPIntVar[] cost = new CPIntVar[bought.length];
    for (int i = 0; i < bought.length; i++) cost[i] = mul(bought[i], price[i]);
    return cost;
  }

  public static void build(Instance inst, Model m, Outputs out) {
    CPBoolVar[] goalkeepers = m.boolVarArray(GOALKEEPER_PRICE.length);
    CPBoolVar[] defenders = m.boolVarArray(DEFENDER_PRICE.length);
    CPBoolVar[] midfielders = m.boolVarArray(MIDFIELDER_PRICE.length);
    CPBoolVar[] strikers = m.boolVarArray(STRIKER_PRICE.length);

    // must buy 1 goalkeeper exactly
    m.cp().post(eq(sum(goalkeepers), 1));
    // must buy 2 or more defenders
    m.cp().post(ge(sum(defenders), 2));
    // must buy 3 or more midfielders
    m.cp().post(ge(sum(midfielders), 3));
    // must buy 2 or more strikers
    m.cp().post(ge(sum(strikers), 2));

    // must buy at least eleven players in total
    int total = goalkeepers.length + defenders.length + midfielders.length + strikers.length;
    CPBoolVar[] everyone = new CPBoolVar[total];
    int k = 0;
    for (CPBoolVar b : goalkeepers) everyone[k++] = b;
    for (CPBoolVar b : defenders) everyone[k++] = b;
    for (CPBoolVar b : midfielders) everyone[k++] = b;
    for (CPBoolVar b : strikers) everyone[k++] = b;
    m.cp().post(ge(sum(everyone), 11));

    // total price of the purchases, in GBP thousands (the value z)
    CPIntVar[] costs = new CPIntVar[total];
    k = 0;
    for (CPIntVar c : priced(goalkeepers, GOALKEEPER_PRICE)) costs[k++] = c;
    for (CPIntVar c : priced(defenders, DEFENDER_PRICE)) costs[k++] = c;
    for (CPIntVar c : priced(midfielders, MIDFIELDER_PRICE)) costs[k++] = c;
    for (CPIntVar c : priced(strikers, STRIKER_PRICE)) costs[k++] = c;

    // the chairman's upper limit of GBP 30 million, i.e. 30000 thousand, is not exceeded
    m.cp().post(le(sum(costs), 30000));

    // z is the total price; maximise it
    CPIntVar z = m.intVar(0, 30000);
    m.cp().post(eq(z, sum(costs)));
    m.maximize(z);

    out.put("z", z);
  }
}
