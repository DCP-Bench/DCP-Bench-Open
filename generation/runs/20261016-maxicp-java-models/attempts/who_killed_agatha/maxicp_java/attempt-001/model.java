// Who killed Aunt Agatha? Three residents of Dreadsbury Mansion (Agatha, the butler, Charles)
// are the only people there. The killer is one of them. Wealth is not given, so it is a
// decision variable: each resident gets a wealth level, and "richer" means a higher level.
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {

  // position of the resident whose name contains the given word
  static int indexOf(String[] names, String word) {
    for (int i = 0; i < names.length; i++) {
      if (names[i].contains(word)) return i;
    }
    throw new IllegalArgumentException("no resident named like " + word);
  }

  public static void build(Instance inst, Model m, Outputs out) {
    String[] names = inst.getStringArray("names");
    int n = names.length;
    int agatha = indexOf(names, "Agatha");
    int butler = indexOf(names, "butler");
    int charles = indexOf(names, "Charles");

    // wealth levels: any ordering of n people fits in n levels, so 0..n-1 loses no case
    CPIntVar[] wealth = m.intVarArray(n, 0, n - 1);

    // hates[i][j] = 1 if resident i hates resident j
    CPBoolVar[][] hates = new CPBoolVar[n][n];
    for (int i = 0; i < n; i++)
      for (int j = 0; j < n; j++)
        hates[i][j] = m.boolVar();

    // the killer is one of the residents
    CPIntVar killer = m.intVar(0, n - 1);

    // Agatha hates everybody except the butler
    for (int j = 0; j < n; j++) {
      if (j == butler) m.cp().post(eq(hates[agatha][j], 0));
      else m.cp().post(eq(hates[agatha][j], 1));
    }

    // Charles hates no one that Agatha hates
    for (int j = 0; j < n; j++)
      m.cp().post(implies(hates[agatha][j], not(hates[charles][j])));

    // the butler hates everyone not richer than Agatha
    for (int j = 0; j < n; j++)
      m.cp().post(implies(isLe(wealth[j], wealth[agatha]), hates[butler][j]));

    // the butler hates everyone whom Agatha hates
    for (int j = 0; j < n; j++)
      m.cp().post(implies(hates[agatha][j], hates[butler][j]));

    // noone hates everyone: every resident hates at least one person
    for (int i = 0; i < n; i++) {
      CPBoolVar[] notHated = new CPBoolVar[n];
      for (int j = 0; j < n; j++) notHated[j] = not(hates[i][j]);
      m.cp().post(or(notHated));
    }

    // a killer always hates his victim (Agatha), and is no richer than her
    for (int k = 0; k < n; k++) {
      CPBoolVar isKiller = isEq(killer, k);
      m.cp().post(implies(isKiller, hates[k][agatha]));
      m.cp().post(implies(isKiller, isLe(wealth[k], wealth[agatha])));
    }

    out.put("killer", killer);
  }
}
