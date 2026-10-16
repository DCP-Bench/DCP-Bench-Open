import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Hanging weights: find integer weights A..M, each between 1 and 13, so that the bars balance as drawn.
// Distances are counted in units of three characters ("+--") from the pivot of each bar.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the weights, each an integer from 1 to 13
    IntVar A = m.intVar("A", 1, 13);
    IntVar B = m.intVar("B", 1, 13);
    IntVar C = m.intVar("C", 1, 13);
    IntVar D = m.intVar("D", 1, 13);
    IntVar E = m.intVar("E", 1, 13);
    IntVar F = m.intVar("F", 1, 13);
    IntVar G = m.intVar("G", 1, 13);
    IntVar H = m.intVar("H", 1, 13);
    IntVar I = m.intVar("I", 1, 13);
    IntVar J = m.intVar("J", 1, 13);
    IntVar K = m.intVar("K", 1, 13);
    IntVar L = m.intVar("L", 1, 13);
    IntVar M = m.intVar("M", 1, 13);

    // bottom right bar: C hangs 5 units from the pivot and D hangs 1 unit: 5*C = D
    m.scalar(new IntVar[]{C, D}, new int[]{5, -1}, "=", 0).post();
    IntVar CD = m.sum("C+D", new IntVar[]{C, D});

    // bar above it: G hangs 3 units from the pivot and the bar C+D hangs 2 units: 3*G = 2*(C+D)
    m.scalar(new IntVar[]{G, CD}, new int[]{3, -2}, "=", 0).post();
    IntVar GCD = m.sum("G+C+D", new IntVar[]{G, CD});

    // bar with A and B: A hangs 1 unit from the pivot and B hangs 4 units: B = 4*A
    m.scalar(new IntVar[]{A, B}, new int[]{4, -1}, "=", 0).post();
    IntVar AB = m.sum("A+B", new IntVar[]{A, B});

    // bar with E and F: 3*E = 2*F
    m.scalar(new IntVar[]{E, F}, new int[]{3, -2}, "=", 0).post();
    IntVar EF = m.sum("E+F", new IntVar[]{E, F});

    // bar with H and I, which hangs from the bar with E and F: 3*H = 3*I + 2*(E+F)
    m.scalar(new IntVar[]{H, I, EF}, new int[]{3, -3, -2}, "=", 0).post();
    IntVar HIEF = m.sum("H+I+E+F", new IntVar[]{H, I, EF});

    // bar with L and M: the weight on the left (H+I+E+F) equals L + 4*M
    m.scalar(new IntVar[]{HIEF, L, M}, new int[]{1, -1, -4}, "=", 0).post();
    IntVar LM = m.sum("L+M", new IntVar[]{L, M});
    IntVar left = m.sum("left bar: H+I+E+F+L+M", new IntVar[]{HIEF, L, M});

    // bar under the top bar on the right: 3*(A+B) + 2*J = K + 2*(G+C+D)
    m.scalar(new IntVar[]{AB, J, K, GCD}, new int[]{3, 2, -1, -2}, "=", 0).post();
    IntVar right = m.sum("right bar: A+B+J+K+G+C+D", new IntVar[]{AB, J, K, GCD});

    // top bar: the left bar weighs 4 units and the right bar 3 units, so 4*left = 3*right
    m.scalar(new IntVar[]{left, right}, new int[]{4, -3}, "=", 0).post();

    out.put("a", A);
    out.put("b", B);
    out.put("c", C);
    out.put("d", D);
    out.put("e", E);
    out.put("f", F);
    out.put("g", G);
    out.put("h", H);
    out.put("i", I);
    out.put("j", J);
    out.put("k", K);
    out.put("l", L);
    out.put("m", M);
  }
}
