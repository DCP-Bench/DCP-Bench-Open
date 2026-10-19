import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Colour the countries Belgium, Denmark, France, Germany, Netherlands and Luxembourg
// (numbered 1 to 6 in this order) so that two neighbouring countries never share a colour,
// using as few colours as possible. Colours are integers starting from 1.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // there are six countries, and each colour is an integer from 1 to 6
    int n = 6;
    CPIntVar[] colors = m.intVarArray(n, 1, n);

    // two neighbouring countries cannot have the same colour
    // (the graph lists neighbouring pairs as 1-based country numbers)
    int[][] graph = inst.getIntMatrix("graph");
    for (int[] pair : graph) {
      m.cp().post(neq(colors[pair[0] - 1], colors[pair[1] - 1]));
    }

    // minimise the number of colours used, which is the largest colour number
    // (the objective is a plain variable, see the runner's offset-view note)
    CPIntVar numColors = m.intVar(1, n);
    m.cp().post(eq(numColors, max(colors)));
    m.minimize(numColors);

    out.put("colors", colors);
  }
}
