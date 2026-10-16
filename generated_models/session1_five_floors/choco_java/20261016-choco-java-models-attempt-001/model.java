import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Five floors: Baker, Cooper, Fletcher, Miller and Smith each live on a different one of the
// first five floors (1 = first floor, 5 = fifth floor), under the constraints of the puzzle.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // floor of each person
    IntVar B = m.intVar("Baker", 1, 5);
    IntVar C = m.intVar("Cooper", 1, 5);
    IntVar F = m.intVar("Fletcher", 1, 5);
    IntVar M = m.intVar("Miller", 1, 5);
    IntVar S = m.intVar("Smith", 1, 5);

    // they all live on different floors
    m.allDifferent(new IntVar[]{B, C, F, M, S}, "AC").post();

    // Baker does not live on the fifth floor
    m.arithm(B, "!=", 5).post();

    // Cooper does not live on the first floor
    m.arithm(C, "!=", 1).post();

    // Fletcher does not live on either the fifth or the first floor
    m.arithm(F, "!=", 5).post();
    m.arithm(F, "!=", 1).post();

    // Miller lives on a higher floor than does Cooper
    m.arithm(M, ">", C).post();

    // Smith does not live on a floor adjacent to Fletcher's
    m.distance(S, F, "!=", 1).post();

    // Fletcher does not live on a floor adjacent to Cooper's
    m.distance(F, C, "!=", 1).post();

    out.put("B", B);
    out.put("C", C);
    out.put("F", F);
    out.put("M", M);
    out.put("S", S);
  }
}
