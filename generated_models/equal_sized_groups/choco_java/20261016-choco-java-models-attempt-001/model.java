// Divide a sorted list of N elements into K groups, using K-1 split points, so that every
// group has as close to round(N/K) elements as possible. Equal values must stay in the same
// group, so a split may only sit between two different values. Minimise the total error.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;
import java.util.ArrayList;
import java.util.List;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] a = inst.getIntArray("a");
    int k = inst.getInt("k");
    int n = a.length;
    int ideal = (int) Math.round((double) n / k);

    // split points: cut[i] = number of elements in groups 0..i, i.e. the 1-based index of the
    // last element of group i. A split may only sit where the value changes (a[c-1] != a[c]).
    List<Integer> valid = new ArrayList<>();
    for (int c = 1; c < n; c++) if (a[c - 1] != a[c]) valid.add(c);
    int[] validCuts = valid.stream().mapToInt(Integer::intValue).toArray();
    IntVar[] cut = new IntVar[k - 1];
    for (int i = 0; i < k - 1; i++) cut[i] = m.intVar("cut" + i, validCuts);

    // the K groups follow one another, and none is empty
    m.increasing(cut, 1).post();

    // prefix[j] = number of elements before group j, with prefix[0] = 0 and prefix[k] = n
    IntVar[] prefix = new IntVar[k + 1];
    prefix[0] = m.intVar(0);
    prefix[k] = m.intVar(n);
    for (int i = 0; i < k - 1; i++) prefix[i + 1] = cut[i];

    // error of each group: its size differs from round(N/K) by this much
    IntVar[] error = new IntVar[k];
    for (int j = 0; j < k; j++) {
      IntVar size = prefix[j + 1].sub(prefix[j]).intVar();      // number of elements in group j
      error[j] = m.intVar("error" + j, 0, n, true);
      m.absolute(error[j], size.sub(ideal).intVar()).post();    // |size - round(N/K)|
    }

    // total error over all groups, to minimise
    IntVar total = m.sum("total", error);
    m.setObjective(Model.MINIMIZE, total);

    // search: split points in order, smallest first
    m.getSolver().setSearch(Search.inputOrderLBSearch(cut));

    out.put("x", cut);
  }
}
