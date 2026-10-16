import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Binary sequence of length n with bits in {-1, +1}. Minimise the sum of the squares
// of the periodic (cyclic) autocorrelations C_k, for k = 1..n-1.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");

    // S[i]: bit i of the sequence, +1 or -1
    IntVar[] S = new IntVar[n];
    for (int i = 0; i < n; i++) S[i] = m.intVar("S" + i, new int[]{-1, 1});

    // C[k]: periodic autocorrelation at shift k
    // Q[k]: C[k] squared
    IntVar[] C = new IntVar[n];
    IntVar[] Q = new IntVar[n];
    for (int k = 1; k < n; k++) {
      // products S_i * S_{(i+k) mod n} over all i, summing to C[k]
      IntVar[] prod = new IntVar[n];
      for (int i = 0; i < n; i++) {
        prod[i] = m.intVar("P" + k + "_" + i, new int[]{-1, 1});
        m.times(S[i], S[(i + k) % n], prod[i]).post();
      }
      C[k] = m.intVar("C" + k, -n, n, true);
      m.sum(prod, "=", C[k]).post();

      // square of the autocorrelation
      Q[k] = m.intVar("Q" + k, 0, n * n, true);
      m.square(Q[k], C[k]).post();
    }

    // energy: sum of C_k^2 over k = 1..n-1, to be minimised
    IntVar[] squares = new IntVar[n - 1];
    for (int k = 1; k < n; k++) squares[k - 1] = Q[k];
    IntVar energy = m.intVar("energy", 0, n * n * (n - 1), true);
    m.sum(squares, "=", energy).post();
    m.setObjective(Model.MINIMIZE, energy);

    out.put("sequence", S);
  }
}
