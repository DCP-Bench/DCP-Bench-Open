import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.limits.FailCounter;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.BoolVar;
import dcp.Instance;
import dcp.Outputs;

// Ternary Steiner problem of order n: find n(n-1)/6 triples of distinct elements from
// 1..n such that any two triples have at most one common element. Rows are triples,
// columns are elements.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int b = n * (n - 1) / 6;

    // sets[i][j] = 1 if element j is part of triple i
    BoolVar[][] sets = m.boolVarMatrix("sets", b, n);

    // each triple has exactly three distinct elements
    for (int i = 0; i < b; i++) {
      m.sum(sets[i], "=", 3).post();
    }

    // any two triples share at most one element: no pair of elements lies in two triples.
    // pairTogether[j][l][i] = 1 if triple i contains both elements j and l
    BoolVar[][][] pairTogether = new BoolVar[n][n][];
    for (int j = 0; j < n; j++) {
      for (int l = j + 1; l < n; l++) {
        BoolVar[] together = new BoolVar[b];
        for (int i = 0; i < b; i++) {
          together[i] = m.boolVar("both_" + i + "_" + j + "_" + l);
          m.times(sets[i][j], sets[i][l], together[i]).post();
        }
        pairTogether[j][l] = together;
        m.sum(together, "<=", 1).post();
      }
    }

    // implied: b triples cover 3b = n(n-1)/2 pairs, which is every pair of elements,
    // and no pair is covered twice, so each pair lies in exactly one triple
    for (int j = 0; j < n; j++) {
      for (int l = j + 1; l < n; l++) {
        m.sum(pairTogether[j][l], "=", 1).post();
      }
    }

    // implied: element j is paired with each of the other n-1 elements once, and each
    // triple containing j pairs it with two others, so j lies in (n-1)/2 triples
    for (int j = 0; j < n; j++) {
      BoolVar[] column = new BoolVar[b];
      for (int i = 0; i < b; i++) column[i] = sets[i][j];
      m.sum(column, "=", (n - 1) / 2).post();
    }

    // search: dom/wdeg on the triple memberships, with Luby restarts
    BoolVar[] flat = new BoolVar[b * n];
    for (int i = 0; i < b; i++) for (int j = 0; j < n; j++) flat[i * n + j] = sets[i][j];
    m.getSolver().setSearch(Search.domOverWDegSearch(flat));
    m.getSolver().setLubyRestart(50, new FailCounter(m, 1), 10000);

    out.put("sets", sets);
  }
}
