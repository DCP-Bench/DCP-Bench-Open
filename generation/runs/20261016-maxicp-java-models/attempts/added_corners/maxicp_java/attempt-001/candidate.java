import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Enter the digits 1 through 8 in the circles and squares such that the number
// in each square is equal to the sum of the numbers in the adjoining circles.
// Layout, positions in reading order (left to right, top to bottom):
//   p0 (circle)  p1 (square)  p2 (circle)
//   p3 (square)               p4 (square)
//   p5 (circle)  p6 (square)  p7 (circle)
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the digits 1 through 8, each used once
    CPIntVar[] p = m.intVarArray(8, 1, 8);
    m.cp().post(allDifferent(p));

    // the top square is the sum of the two top circles
    m.cp().post(eq(sum(p[0], p[2]), p[1]));
    // the left square is the sum of the two left circles
    m.cp().post(eq(sum(p[0], p[5]), p[3]));
    // the right square is the sum of the two right circles
    m.cp().post(eq(sum(p[2], p[7]), p[4]));
    // the bottom square is the sum of the two bottom circles
    m.cp().post(eq(sum(p[5], p[7]), p[6]));

    out.put("positions", p);
  }
}
