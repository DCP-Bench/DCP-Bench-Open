// Binary sequence of length n with entries +1 or -1 that minimises the sum of the squares
// of its periodic (cyclic) autocorrelations: E = sum over k = 1..n-1 of C_k^2, where
// C_k = sum over i = 0..n-1 of S_i * S_((i + k) mod n).
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");

    // each bit is a Boolean b_i: b_i = 1 means the bit is +1, b_i = 0 means -1
    CPBoolVar[] b = m.boolVarArray(n);
    // the bit S_i in {-1, +1}, as the view 2 * b_i - 1
    CPIntVar[] s = new CPIntVar[n];
    for (int i = 0; i < n; i++) s[i] = minus(mul(b[i], 2), 1);

    // the autocorrelation sum for each shift k = 1..n-1, with periodic boundaries
    CPIntVar[] squares = new CPIntVar[n - 1];
    for (int k = 1; k < n; k++) {
      // C_k = sum of S_i * S_((i + k) mod n) over all positions i
      CPIntVar[] products = new CPIntVar[n];
      for (int i = 0; i < n; i++) {
        products[i] = mul(s[i], s[(i + k) % n]);
      }
      CPIntVar c = sum(products);
      // C_k squared, added to the energy
      squares[k - 1] = mul(c, c);
    }

    // the energy E = sum of C_k^2, to be minimised
    CPIntVar energy = sum(squares);
    m.minimize(energy);

    // print the bits as the integers -1 and +1
    out.put("sequence", s);
  }
}
