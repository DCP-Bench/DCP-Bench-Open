import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Baker, Cooper, Fletcher, Miller and Smith live on the first five floors of an
// apartment house (floors 1 to 5). Find the floor of each person.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the five people, each on one of the floors 1 to 5
    CPIntVar B = m.intVar(1, 5);
    CPIntVar C = m.intVar(1, 5);
    CPIntVar F = m.intVar(1, 5);
    CPIntVar M = m.intVar(1, 5);
    CPIntVar S = m.intVar(1, 5);

    // They all live on different floors.
    m.cp().post(allDifferent(new CPIntVar[]{B, C, F, M, S}));

    // Baker does not live on the fifth floor.
    m.cp().post(neq(B, 5));

    // Cooper does not live on the first floor.
    m.cp().post(neq(C, 1));

    // Fletcher does not live on either the fifth or the first floor.
    m.cp().post(neq(F, 5));
    m.cp().post(neq(F, 1));

    // Miller lives on a higher floor than does Cooper.
    m.cp().post(ge(M, plus(C, 1)));

    // Smith does not live on a floor adjacent to Fletcher's.
    m.cp().post(neq(S, plus(F, 1)));
    m.cp().post(neq(S, minus(F, 1)));

    // Fletcher does not live on a floor adjacent to Cooper's.
    m.cp().post(neq(F, plus(C, 1)));
    m.cp().post(neq(F, minus(C, 1)));

    // Print the floors where each person lives (B, C, F, M, S).
    out.put("B", B);
    out.put("C", C);
    out.put("F", F);
    out.put("M", M);
    out.put("S", S);
  }
}
