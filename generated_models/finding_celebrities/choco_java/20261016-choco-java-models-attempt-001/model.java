import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import dcp.Instance;
import dcp.Outputs;

// Finding celebrities: among n guests, a celebrity is known by every other guest and
// knows only other celebrities. Output celebrities[i] = 1 for each celebrity i.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] knows = inst.getIntMatrix("graph");   // knows[i][j] = 1 if guest i knows guest j
    int n = knows.length;

    BoolVar[] celebrity = m.boolVarArray("celebrity", n);

    // At least one celebrity is present at the party
    m.sum(celebrity, ">=", 1).post();

    for (int i = 0; i < n; i++) {
      // Everybody at the party knows a celebrity: if some other guest does not know
      // guest i, then guest i is not a celebrity (a fact of the data, so fixed here)
      boolean knownByAll = true;
      for (int j = 0; j < n; j++) if (j != i && knows[j][i] == 0) knownByAll = false;
      if (!knownByAll) {
        m.arithm(celebrity[i], "=", 0).post();
        continue;
      }

      // A celebrity knows only other celebrities: collect the other guests that i knows
      int known = 0;
      for (int j = 0; j < n; j++) if (j != i && knows[i][j] == 1) known++;
      BoolVar[] notCelebrityKnown = new BoolVar[known];
      int k = 0;
      for (int j = 0; j < n; j++) {
        if (j != i && knows[i][j] == 1) notCelebrityKnown[k++] = celebrity[j].not();
      }

      // Guest i is a celebrity exactly when no guest i knows is outside the celebrities
      if (known == 0) {
        m.arithm(celebrity[i], "=", 1).post();
      } else {
        m.sum(notCelebrityKnown, "=", 0).reifyWith(celebrity[i]);
      }
    }

    out.put("celebrities", celebrity);
  }
}
