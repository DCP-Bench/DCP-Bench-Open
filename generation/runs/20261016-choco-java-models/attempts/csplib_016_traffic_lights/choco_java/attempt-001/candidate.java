import org.chocosolver.solver.Model;
import org.chocosolver.solver.constraints.extension.Tuples;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Traffic lights at a four-way junction: choose a state for each of four vehicle lights
// and four pedestrian lights so that every pair of intersecting roads is in a safe combination.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] allowed = inst.getIntMatrix("allowed_tuples"); // safe (V_i, P_i, V_i+1, P_i+1) combinations
    int n = 4;

    // V[i]: state of vehicle light i (0=red, 1=red-yellow, 2=green, 3=yellow)
    // P[i]: state of pedestrian light i (0=red, 1=green)
    IntVar[] V = m.intVarArray("V", n, 0, 3);
    IntVar[] P = m.intVarArray("P", n, 0, 1);

    // the safe combinations, one table per pair of neighbouring roads i and i+1 (V_5 = V_1, P_5 = P_1)
    for (int i = 0; i < n; i++) {
      int j = (i + 1) % n;
      Tuples safe = new Tuples(true);
      for (int[] row : allowed) safe.add(row);
      // (V_i, P_i, V_i+1, P_i+1) must be one of the safe combinations; every other one is disallowed
      m.table(new IntVar[]{V[i], P[i], V[j], P[j]}, safe).post();
    }

    // the lights in the order V1..V4, P1..P4
    IntVar[] lights = new IntVar[2 * n];
    for (int i = 0; i < n; i++) {
      lights[i] = V[i];
      lights[n + i] = P[i];
    }
    out.put("lights", lights);
  }
}
