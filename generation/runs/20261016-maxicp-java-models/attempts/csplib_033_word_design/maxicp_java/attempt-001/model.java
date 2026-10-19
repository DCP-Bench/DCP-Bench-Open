// Word design: find num_words words of length n over the alphabet {A, C, G, T},
// coded 1 = A, 2 = C, 3 = G, 4 = T. Output "words" holds one row per word.
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int k = inst.getInt("num_words");

    CPIntVar[][] words = new CPIntVar[k][];
    for (int i = 0; i < k; i++) {
      words[i] = m.intVarArray(n, 1, 4);
    }

    // each word has 4 symbols from {C, G}
    for (int i = 0; i < k; i++) {
      CPIntVar[] cg = new CPIntVar[2 * n];
      for (int j = 0; j < n; j++) {
        cg[2 * j] = isEq(words[i][j], 2);
        cg[2 * j + 1] = isEq(words[i][j], 3);
      }
      m.cp().post(eq(sum(cg), 4));
    }

    for (int i = 0; i < k; i++) {
      for (int j = 0; j < k; j++) {
        // each pair of distinct words differ in at least 4 positions
        if (i < j) {
          CPIntVar[] same = new CPIntVar[n];
          for (int p = 0; p < n; p++) {
            same[p] = isEq(words[i][p], words[j][p]);
          }
          m.cp().post(le(sum(same), n - 4));
        }
        // x reversed and y complemented differ in at least 4 positions,
        // for every pair x, y including x = y.
        // The Watson-Crick complement maps 1 <-> 4 and 2 <-> 3, that is 5 - letter.
        CPIntVar[] same = new CPIntVar[n];
        for (int p = 0; p < n; p++) {
          same[p] = isEq(words[i][n - 1 - p], plus(minus(words[j][p]), 5));
        }
        m.cp().post(le(sum(same), n - 4));
      }
    }

    out.put("words", words);
  }
}
