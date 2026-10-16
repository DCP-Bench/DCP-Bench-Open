import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Five Spanish brigands (Alfonso, Benito, Carlos, Diego, Esteban) hold exactly 200 doubloons
// in total. With Alfonso's share times 12, Benito's times 3, Carlos's unchanged, Diego's
// halved and Esteban's divided by 3, the total would still be 200. Each brigand has at
// least one doubloon. Find the amount each one has.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // A, B, C, D, E: doubloons of Alfonso, Benito, Carlos, Diego, Esteban
    IntVar A = m.intVar("A", 1, 200);
    IntVar B = m.intVar("B", 1, 200);
    IntVar C = m.intVar("C", 1, 200);
    IntVar D = m.intVar("D", 1, 200);
    IntVar E = m.intVar("E", 1, 200);
    IntVar[] x = {A, B, C, D, E};

    // they captured altogether exactly 200 doubloons
    m.sum(x, "=", 200).post();

    // with the multipliers 12, 3, 1, 1/2 and 1/3, the total is still 200.
    // Multiplied by 6 to keep integer coefficients: 72A + 18B + 6C + 3D + 2E = 1200
    m.scalar(x, new int[]{72, 18, 6, 3, 2}, "=", 1200).post();

    out.put("A", A);
    out.put("B", B);
    out.put("C", C);
    out.put("D", D);
    out.put("E", E);
  }
}
