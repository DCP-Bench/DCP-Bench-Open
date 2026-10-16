import java.util.ArrayList;
import java.util.List;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// A weight of M pounds broke into N pieces, each a whole number of pounds, and the pieces
// can weigh every whole number of pounds from 1 to M on a balance scale: a piece can go
// on the same pan as the object (counted as -1), on the other pan (+1), or be left off (0).
// The model reads M and N from the instance.
public class Submission {

  public static void build(Instance inst, Model m, Outputs out) {
    int total = inst.getInt("m");
    int pieces = inst.getInt("n");

    // weights[i] is the weight of piece i, in pounds
    CPIntVar[] weights = m.intVarArray(pieces, 1, total);

    // the pieces together make up the whole weight
    m.cp().post(eq(sum(weights), total));

    // every placement of the pieces on the two pans gives a difference in pounds.
    // There are 3^N placements, one for each choice of -1, 0 or +1 for every piece.
    int placements = (int) Math.pow(3, pieces);
    List<CPIntVar> differences = new ArrayList<>();
    for (int code = 0; code < placements; code++) {
      CPIntVar difference = difference(weights, code);
      if (difference != null) differences.add(difference);
    }
    CPIntVar[] all = differences.toArray(new CPIntVar[0]);

    // every whole number of pounds from 1 to the total is the difference of some placement
    for (int target = 1; target <= total; target++) {
      CPBoolVar[] reached = new CPBoolVar[all.length];
      for (int k = 0; k < all.length; k++) reached[k] = isEq(all[k], target);
      m.cp().post(or(reached));
    }

    out.put("weights", weights);
  }

  // The difference in pounds for one placement: the pieces on the object's pan count
  // negative, the pieces on the other pan positive. Returns null for an empty placement.
  static CPIntVar difference(CPIntVar[] weights, int code) {
    List<CPIntVar> terms = new ArrayList<>();
    int rest = code;
    for (CPIntVar weight : weights) {
      int digit = rest % 3 - 1;
      rest /= 3;
      if (digit == 1) terms.add(weight);
      else if (digit == -1) terms.add(minus(weight));
    }
    if (terms.isEmpty()) return null;
    return sum(terms.toArray(new CPIntVar[0]));
  }
}
