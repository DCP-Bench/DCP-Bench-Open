// Kidney exchange: n people on a waiting list. compatible[i] is the set of people
// that person i can donate a kidney to. The data number people from 1, the arrays from 0.
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("num_people");
    int[][] compatible = inst.getIntMatrix("compatible");

    // transplants[i][j] is 1 when person i donates a kidney to person j
    CPBoolVar[][] transplants = new CPBoolVar[n][n];
    for (int i = 0; i < n; i++) {
      for (int j = 0; j < n; j++) {
        transplants[i][j] = m.boolVar();
      }
    }

    // a person can donate only to the people on their compatible list
    // (nobody donates to themselves)
    for (int i = 0; i < n; i++) {
      boolean[] listed = new boolean[n];
      for (int d : compatible[i]) {
        listed[d - 1] = true;
      }
      for (int j = 0; j < n; j++) {
        if (!listed[j] || j == i) {
          m.cp().post(eq(transplants[i][j], 0));
        }
      }
    }

    // no person receives more than one kidney
    for (int j = 0; j < n; j++) {
      CPBoolVar[] receives = new CPBoolVar[n];
      for (int i = 0; i < n; i++) {
        receives[i] = transplants[i][j];
      }
      m.cp().post(le(sum(receives), 1));
    }

    // anyone who gives a kidney must receive one: donations and receipts per person
    // match, so every donor gives once and receives once, in a cycle
    for (int i = 0; i < n; i++) {
      CPBoolVar[] gives = new CPBoolVar[n];
      CPBoolVar[] receives = new CPBoolVar[n];
      for (int j = 0; j < n; j++) {
        gives[j] = transplants[i][j];
        receives[j] = transplants[j][i];
      }
      m.cp().post(eq(sum(gives), sum(receives)));
    }

    // maximise the number of people who receive a kidney
    CPBoolVar[] all = new CPBoolVar[n * n];
    for (int i = 0; i < n; i++) {
      for (int j = 0; j < n; j++) {
        all[i * n + j] = transplants[i][j];
      }
    }
    CPIntVar obj = m.intVar(0, n * n);
    m.cp().post(eq(obj, sum(all)));
    m.maximize(obj);

    out.put("transplants", transplants);
  }
}
