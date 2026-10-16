// Handshaking problem: Hilary and Jocelyn are married and invite num_couples couples
// (friends). Everybody shakes hands with others, but never with self or spouse.
// Jocelyn asks everyone except herself how many hands they shook; all answers differ.
// Output: the number of hands Hilary shook (hil).
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.search.limits.FailCounter;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int couples = inst.getInt("num_couples");
    // persons 0 = Hilary, 1 = Jocelyn (the married host couple), persons 2k and 2k+1
    // are the spouses of the k-th invited couple.
    int n = 2 * (couples + 1);

    // Handshake variables for each unordered pair of persons, skipping spouses.
    // shake[i][j] for i < j, mirrored with shake[j][i] (symmetric handshake).
    BoolVar[][] shake = new BoolVar[n][n];
    for (int i = 0; i < n; i++) {
      for (int j = i + 1; j < n; j++) {
        if (j == (i ^ 1)) continue; // nobody shakes hands with his or her spouse
        shake[i][j] = m.boolVar("shake_" + i + "_" + j);
        shake[j][i] = shake[i][j];
      }
    }

    // hands[i]: number of hands person i has shaken, over all others except self and spouse
    IntVar[] hands = new IntVar[n];
    for (int i = 0; i < n; i++) {
      BoolVar[] with = new BoolVar[n - 2];
      int k = 0;
      for (int j = 0; j < n; j++) {
        if (j == i || j == (i ^ 1)) continue; // nobody shakes hands with self or spouse
        with[k++] = shake[i][j];
      }
      hands[i] = m.sum("hands_" + i, with);
    }

    // all answers are different: Jocelyn asks everyone except herself
    IntVar[] answers = new IntVar[n - 1];
    int k = 0;
    for (int i = 0; i < n; i++) {
      if (i == 1) continue; // Jocelyn does not ask herself
      answers[k++] = hands[i];
    }
    m.allDifferent(answers, "AC").post();
    // implied: n-1 distinct answers in 0..n-2 form a permutation of 0..n-2, so they sum to (n-2)(n-1)/2
    m.sum(answers, "=", (n - 2) * (n - 1) / 2).post();

    // symmetry breaking: invited couples are interchangeable and so are the two spouses of a
    // couple. Order the couples by their first member's hands and each couple's members too.
    // The answers are all different, so these orders never tie.
    for (int c = 1; c <= couples; c++) {
      m.arithm(hands[2 * c], "<", hands[2 * c + 1]).post();
      if (c < couples) m.arithm(hands[2 * c], "<", hands[2 * c + 2]).post();
    }

    // search: branch on the handshake variables with domain-over-weighted-degree and restarts
    java.util.List<BoolVar> edges = new java.util.ArrayList<>();
    for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) if (shake[i][j] != null) edges.add(shake[i][j]);
    m.getSolver().setSearch(Search.domOverWDegSearch(edges.toArray(new BoolVar[0])));
    m.getSolver().setLubyRestart(50, new FailCounter(m, 1), 10000);

    out.put("hil", hands[0]);
  }
}
