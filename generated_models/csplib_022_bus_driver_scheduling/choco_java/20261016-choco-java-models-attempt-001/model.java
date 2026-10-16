import java.util.ArrayList;
import java.util.List;
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Bus driver scheduling: choose a subset of shifts so that every piece of work is covered
// by exactly one chosen shift, minimising the number of shifts used.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int numWork = inst.getInt("num_work");
    int numShifts = inst.getInt("num_shifts");
    int[][] shifts = inst.getIntMatrix("shifts");  // shifts[j]: the pieces of work shift j covers (0-based)

    // x[j] = 1 if shift j is selected
    BoolVar[] x = m.boolVarArray("x", numShifts);

    // every piece of work is covered by exactly one selected shift
    for (int w = 0; w < numWork; w++) {
      List<BoolVar> covering = new ArrayList<>();
      for (int j = 0; j < numShifts; j++) {
        for (int task : shifts[j]) {
          if (task == w) { covering.add(x[j]); break; }
        }
      }
      m.sum(covering.toArray(new BoolVar[0]), "=", 1).post();
    }

    // minimise the total number of shifts used (every shift costs the same)
    IntVar total = m.sum("total", x);
    m.setObjective(Model.MINIMIZE, total);

    out.put("x", x);
  }
}
