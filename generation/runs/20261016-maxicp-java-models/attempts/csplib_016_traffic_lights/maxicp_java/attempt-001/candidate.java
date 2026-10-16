// Traffic lights at a four-way junction: eight lights, four for vehicles (V1..V4)
// and four for pedestrians (P1..P4). Each pair (V_i, P_i, V_i+1, P_i+1) must be one
// of the listed safe combinations, with V_5 = V_1 and P_5 = P_1.
// Vehicle states: 0=red, 1=red-yellow, 2=green, 3=yellow. Pedestrian states: 0=red, 1=green.
// Output lights = [V1, V2, V3, V4, P1, P2, P3, P4].
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the safe combinations, one row per allowed (V_i, P_i, V_i+1, P_i+1)
    int[][] allowed = inst.getIntMatrix("allowed_tuples");

    // vehicle light states, 0..3
    CPIntVar[] v = m.intVarArray(4, 0, 3);
    // pedestrian light states, 0..1
    CPIntVar[] p = m.intVarArray(4, 0, 1);

    // for i = 1..4 the combination (V_i, P_i, V_i+1, P_i+1) is one of the safe combinations;
    // every other combination is disallowed to prevent accidents (index 4 wraps to 0)
    for (int i = 0; i < 4; i++) {
      int j = (i + 1) % 4;
      m.cp().post(table(new CPIntVar[] {v[i], p[i], v[j], p[j]}, allowed));
    }

    // the lights are reported as [V1, V2, V3, V4, P1, P2, P3, P4]
    out.put("lights", new CPIntVar[] {v[0], v[1], v[2], v[3], p[0], p[1], p[2], p[3]});
  }
}
