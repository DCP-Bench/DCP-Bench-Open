// Birthday coins: Tommy was given 15 coins (half-crowns, shillings and sixpence).
// The coins add up to 1 pound 5 shillings and 6 pence, which is 306 pence.
// A half-crown is 30 pence, a shilling is 12 pence, a sixpence is 6 pence.
// How many half-crowns was he given?

import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;
import org.maxicp.cp.engine.core.CPIntVar;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // He was given half-crowns, shillings and sixpence, so each kind is at least one coin.
    CPIntVar halfCrowns = m.intVar(1, 15);
    CPIntVar shillings = m.intVar(1, 15);
    CPIntVar sixpence = m.intVar(1, 15);

    // Tommy was given 15 coins for his birthday.
    m.cp().post(eq(sum(new CPIntVar[] {halfCrowns, shillings, sixpence}), 15));

    // He found that he had 1 pound 5 shillings and 6 pence, which is 306 pence.
    m.cp().post(eq(sum(new CPIntVar[] {
        mul(halfCrowns, 30), mul(shillings, 12), mul(sixpence, 6)}), 306));

    out.put("half_crowns", halfCrowns);
  }
}
