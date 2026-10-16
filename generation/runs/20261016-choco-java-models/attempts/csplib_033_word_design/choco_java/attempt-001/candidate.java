// Word design (CSPLib 033): find num_words words of length n over the DNA alphabet
// {A,C,G,T}, each with exactly 4 letters from {C,G}, where distinct words differ in at
// least 4 positions and for every pair x,y (x = y allowed) the reverse of x and the
// Watson-Crick complement of y differ in at least 4 positions.
// Letters are coded A=1, C=2, G=3, T=4, so the complement of letter l is 5 - l.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");                  // length of each word
    int numWords = inst.getInt("num_words");   // number of words in the set

    // words[k][p]: letter at position p of word k (1=A, 2=C, 3=G, 4=T)
    IntVar[][] words = m.intVarMatrix("word", numWords, n, 1, 4);

    // each word has exactly 4 symbols from {C, G}
    for (int k = 0; k < numWords; k++) {
      m.among(m.intVar(4), words[k], new int[]{2, 3}).post();
    }

    // each pair of distinct words differs in at least 4 positions
    for (int i = 0; i < numWords; i++) {
      for (int j = i + 1; j < numWords; j++) {
        BoolVar[] differ = new BoolVar[n];
        for (int p = 0; p < n; p++) {
          differ[p] = m.arithm(words[i][p], "!=", words[j][p]).reify();
        }
        m.sum(differ, ">=", 4).post();
      }
    }

    // for each pair x, y (identical allowed): reverse(x) and complement(y) differ in at least 4 positions.
    // position p of reverse(x) is x[n-1-p], position p of complement(y) is 5 - y[p],
    // so they differ exactly when x[n-1-p] + y[p] != 5
    for (int i = 0; i < numWords; i++) {
      for (int j = 0; j < numWords; j++) {
        BoolVar[] differ = new BoolVar[n];
        for (int p = 0; p < n; p++) {
          differ[p] = m.arithm(words[i][n - 1 - p], "+", words[j][p], "!=", 5).reify();
        }
        m.sum(differ, ">=", 4).post();
      }
    }

    out.put("words", words);
  }
}
