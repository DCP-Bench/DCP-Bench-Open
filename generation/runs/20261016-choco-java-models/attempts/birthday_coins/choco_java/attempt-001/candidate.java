import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Birthday coins: Tommy got 15 coins of half-crowns, shillings and sixpence worth
// 1 pound 5 shillings 6 pence; find the number of half-crowns.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // number of half-crowns (30 pence each), shillings (12 pence), sixpence (6 pence)
    IntVar halfCrowns = m.intVar("half_crowns", 1, 15);
    IntVar shillings = m.intVar("shillings", 1, 15);
    IntVar sixpence = m.intVar("sixpence", 1, 15);

    // he was given 15 coins in all
    m.sum(new IntVar[]{halfCrowns, shillings, sixpence}, "=", 15).post();

    // the coins add up to 1 pound 5 shillings 6 pence = 306 pence
    m.scalar(new IntVar[]{halfCrowns, shillings, sixpence}, new int[]{30, 12, 6}, "=", 306).post();

    out.put("half_crowns", halfCrowns);
  }
}
