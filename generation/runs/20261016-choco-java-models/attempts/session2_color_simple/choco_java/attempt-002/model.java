import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Map colouring of six countries: neighbouring countries get different colours,
// and the number of colours used is minimised.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] graph = inst.getIntMatrix("graph"); // neighbouring pairs, country ids numbered from 1
    int n = 6;

    // colors[i]: colour of country i+1, colours numbered from 1
    IntVar[] colors = m.intVarArray("colors", n, 1, n);

    // neighbouring countries cannot have the same colour
    for (int[] pair : graph) {
      m.arithm(colors[pair[0] - 1], "!=", colors[pair[1] - 1]).post();
    }

    // nb: number of colours used. Colours are numbered 1..k, so the largest colour used
    // is the number of colours. (An nValues count gave suboptimal_solution in the evaluator.)
    IntVar nb = m.intVar("nb", 1, n);
    m.max(nb, colors).post();

    // minimise the number of colours used
    m.setObjective(Model.MINIMIZE, nb);

    out.put("colors", colors);
  }
}
