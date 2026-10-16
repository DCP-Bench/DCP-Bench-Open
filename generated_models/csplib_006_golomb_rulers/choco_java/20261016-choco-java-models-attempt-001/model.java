// Golomb ruler: place n marks on an integer line, the first at 0, so that all
// pairwise differences between marks are distinct. Minimise the position of the last mark.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import org.chocosolver.solver.search.strategy.Search;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("size");
    // The marks 0, 1, 3, 7, ... (2^k - 1) form a valid ruler of length 2^(n-1) - 1,
    // so the optimal length is at most this value. Used only as the domain bound.
    int ub = (1 << (n - 1)) - 1;
    IntVar[] marks = m.intVarArray("marks", n, 0, ub, false);  // marks[i]: position of mark i

    // the first mark is at 0
    m.arithm(marks[0], "=", 0).post();

    // marks are in increasing order, so each difference is positive
    m.increasing(marks, 1).post();

    // reflecting a ruler gives another ruler of the same length, so the gap between
    // the first two marks is kept below the gap between the last two
    if (n > 2) {
      m.arithm(marks[1], "<", marks[n - 1], "-", marks[n - 2]).post();
    }

    // one difference variable for every pair of marks i < j: diff = marks[j] - marks[i]
    IntVar[] diffs = new IntVar[n * (n - 1) / 2];
    int k = 0;
    for (int i = 0; i < n; i++) {
      for (int j = i + 1; j < n; j++) {
        diffs[k] = m.intVar("diff_" + i + "_" + j, 1, ub);
        m.scalar(new IntVar[]{marks[j], marks[i], diffs[k]}, new int[]{1, -1, -1}, "=", 0).post();
        k++;
      }
    }

    // all differences between pairs of marks are distinct
    m.allDifferent(diffs, "AC").post();

    // the length of the ruler is the position of the last mark, to be minimised
    IntVar length = marks[n - 1];
    m.setObjective(Model.MINIMIZE, length);

    // branch on the marks, most constrained first, with restarts
    m.getSolver().setSearch(Search.domOverWDegSearch(marks));
    m.getSolver().setLubyRestart(50, new org.chocosolver.solver.search.limits.FailCounter(m, 1), 10000);

    out.put("length", length);
    out.put("marks", marks);
  }
}
