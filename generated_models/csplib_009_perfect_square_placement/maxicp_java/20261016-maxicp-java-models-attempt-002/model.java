// Perfect square placement: pack the squares with the given integer sides into a
// bigger square of side `base`, so that no two squares overlap, all square borders
// are parallel to the border of the big square, and there is no spare capacity.
// Print the lower-left corner of each square (x_coords, y_coords), starting from 0.
import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.constraints.scheduling.CPCumulFunction;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPIntervalVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int base = inst.getInt("base");
    int[] sides = inst.getIntArray("sides");
    int n = sides.length;

    // each square lies inside the big square: its corner runs from 0 to base - side
    CPIntVar[] x = new CPIntVar[n];
    CPIntVar[] y = new CPIntVar[n];
    for (int i = 0; i < n; i++) {
      x[i] = m.intVar(0, base - sides[i]);
      y[i] = m.intVar(0, base - sides[i]);
    }

    // no two squares overlap: for every pair, one lies left of, right of,
    // below or above the other
    for (int i = 0; i < n; i++) {
      for (int j = i + 1; j < n; j++) {
        CPBoolVar iLeftOfJ = isLe(plus(x[i], sides[i]), x[j]);
        CPBoolVar jLeftOfI = isLe(plus(x[j], sides[j]), x[i]);
        CPBoolVar iBelowJ = isLe(plus(y[i], sides[i]), y[j]);
        CPBoolVar jBelowI = isLe(plus(y[j], sides[j]), y[i]);
        m.cp().post(or(new CPBoolVar[] {iLeftOfJ, jLeftOfI, iBelowJ, jBelowI}));
      }
    }

    // the squares that cross a vertical line are stacked one above the other inside
    // the big square, so their sides add up to at most base (redundant, cumulative
    // over the horizontal position with the side as the height)
    CPCumulFunction[] crossingVertical = new CPCumulFunction[n];
    // and the same for a horizontal line (redundant, cumulative over the vertical position)
    CPCumulFunction[] crossingHorizontal = new CPCumulFunction[n];
    for (int i = 0; i < n; i++) {
      CPIntervalVar tx = CPFactory.makeIntervalVar(m.cp(), false, sides[i]);
      m.cp().post(eq(start(tx), x[i]));
      crossingVertical[i] = pulse(tx, sides[i]);

      CPIntervalVar ty = CPFactory.makeIntervalVar(m.cp(), false, sides[i]);
      m.cp().post(eq(start(ty), y[i]));
      crossingHorizontal[i] = pulse(ty, sides[i]);
    }
    m.cp().post(le(sum(crossingVertical), base));
    m.cp().post(le(sum(crossingHorizontal), base));

    out.put("x_coords", x);
    out.put("y_coords", y);
  }
}
