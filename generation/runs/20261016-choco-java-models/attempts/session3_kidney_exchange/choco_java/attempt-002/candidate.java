import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.limits.FailCounter;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Kidney exchange: choose donations between people so that every donor receives a kidney,
// no person receives more than one, and the number of people receiving a kidney is maximal.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("num_people");
    int[][] compatible = inst.getIntMatrix("compatible");  // compatible[i]: 1-based people i can donate to
    IntVar[][] donates = m.intVarMatrix("donates", n, n, 0, 1);  // donates[i][j] = 1 if i gives to j

    // only compatible pairs can be a transplant; nobody donates to themselves
    boolean[][] allowed = new boolean[n][n];
    for (int i = 0; i < n; i++)
      for (int j : compatible[i]) allowed[i][j - 1] = true;
    for (int i = 0; i < n; i++)
      for (int j = 0; j < n; j++)
        if (!allowed[i][j] || i == j) m.arithm(donates[i][j], "=", 0).post();

    // received[j] = 1 if person j receives a kidney; nobody receives more than one
    IntVar[] received = m.intVarArray("received", n, 0, 1);
    for (int j = 0; j < n; j++) {
      IntVar[] column = new IntVar[n];
      for (int i = 0; i < n; i++) column[i] = donates[i][j];
      m.sum(column, "=", received[j]).post();
    }

    // given[i] = 1 if person i gives a kidney; anyone who gives must receive one
    IntVar[] given = m.intVarArray("given", n, 0, 1);
    for (int i = 0; i < n; i++) {
      m.sum(donates[i], "=", given[i]).post();
      m.arithm(given[i], "<=", received[i]).post();
    }

    // maximise the number of people receiving a kidney
    IntVar total = m.intVar("total", 0, n, true);
    m.sum(received, "=", total).post();
    m.setObjective(Model.MAXIMIZE, total);

    // search: the most constrained transplant cell first, dom/wdeg, with Luby restarts
    IntVar[] cells = new IntVar[n * n];
    for (int i = 0; i < n; i++)
      for (int j = 0; j < n; j++) cells[i * n + j] = donates[i][j];
    m.getSolver().setSearch(Search.domOverWDegSearch(cells));
    m.getSolver().setLubyRestart(50, new FailCounter(m, 1), 10000);

    out.put("transplants", donates);
  }
}
