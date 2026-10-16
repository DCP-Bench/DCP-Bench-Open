// Finding celebrities at a party of n guests. graph[i][j] = 1 when guest i knows guest j.
// A celebrity is a guest that everybody at the party knows and who knows only other celebrities.
// At least one celebrity is present at the party.
// The output celebrities[i] is 1 when guest i is a celebrity.
import org.maxicp.cp.engine.core.CPBoolVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] knows = inst.getIntMatrix("graph");
    int n = knows.length;
    CPBoolVar[] celebrity = m.boolVarArray(n);

    // at least one celebrity is present at the party
    m.cp().post(or(celebrity));

    for (int i = 0; i < n; i++) {
      // everybody at the party knows a celebrity: a guest who is not known by someone else is not a celebrity
      for (int j = 0; j < n; j++) {
        if (j != i && knows[j][i] == 0) {
          m.cp().post(not(celebrity[i]));
        }
      }
      // a celebrity knows only other celebrities: if i is a celebrity and knows j, then j is a celebrity
      for (int j = 0; j < n; j++) {
        if (j != i && knows[i][j] == 1) {
          m.cp().post(implies(celebrity[i], celebrity[j]));
        }
      }
    }

    out.put("celebrities", celebrity);
  }
}
