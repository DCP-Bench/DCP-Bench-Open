import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Order m quasigroup existence (QG3.m): a Latin square of size m, with values 0..m-1,
// in which (a*b)*(b*a) = a for every pair a, b.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int size = inst.getInt("m");

    // q[a][b] = a*b
    IntVar[][] q = m.intVarMatrix("q", size, size, 0, size - 1);

    // every element occurs once in every row
    for (int a = 0; a < size; a++) {
      m.allDifferent(q[a], "AC").post();
    }

    // every element occurs once in every column
    for (int b = 0; b < size; b++) {
      IntVar[] col = new IntVar[size];
      for (int a = 0; a < size; a++) col[a] = q[a][b];
      m.allDifferent(col, "AC").post();
    }

    // flattened table, so that the table can be indexed by a variable: flat[i*size + j] = q[i][j]
    IntVar[] flat = new IntVar[size * size];
    for (int i = 0; i < size; i++)
      for (int j = 0; j < size; j++) flat[i * size + j] = q[i][j];

    // (a*b)*(b*a) = a for all a, b
    for (int a = 0; a < size; a++) {
      for (int b = 0; b < size; b++) {
        // index of (b*a) in the flattened table row given by a*b
        IntVar index = q[a][b].mul(size).add(q[b][a]).intVar();
        // the table value at (a*b, b*a) equals a
        m.element(m.intVar(a), flat, index, 0).post();
      }
    }

    out.put("quasigroup", q);
  }
}
