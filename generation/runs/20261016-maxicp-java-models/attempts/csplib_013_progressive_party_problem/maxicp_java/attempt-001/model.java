import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Progressive party: a yacht club party. Some boats are hosts and stay where they are; the
// crews of the other boats visit one host in each period. Minimise the number of host boats.
// visits[p][b] = v means boat b is at boat v in period p (a host is at itself).
// is_host[b] = 1 when boat b is a host.
public class Submission {

  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n_boats");
    int periods = inst.getInt("n_periods");
    int[] capacity = inst.getIntArray("capacity");
    int[] crew = inst.getIntArray("crew_size");

    // whether each boat is a host
    CPBoolVar[] isHost = m.boolVarArray(n);

    // where each boat is in each period, one of the n boats
    CPIntVar[][] visits = new CPIntVar[periods][n];
    for (int p = 0; p < periods; p++)
      for (int b = 0; b < n; b++)
        visits[p][b] = m.intVar(0, n - 1);

    // a host boat stays at itself in every period
    for (int p = 0; p < periods; p++)
      for (int b = 0; b < n; b++)
        m.cp().post(implies(isHost[b], isEq(visits[p][b], b)));

    // a boat is visited only if it is a host, so every guest visits a host
    for (int p = 0; p < periods; p++)
      for (int b = 0; b < n; b++)
        for (int v = 0; v < n; v++)
          m.cp().post(implies(isEq(visits[p][b], v), isHost[v]));

    // the people aboard a host boat, its host crew and the guest crews, do not exceed its capacity
    for (int p = 0; p < periods; p++)
      for (int h = 0; h < n; h++) {
        CPIntVar[] aboard = new CPIntVar[n];
        for (int b = 0; b < n; b++)
          aboard[b] = mul(isEq(visits[p][b], h), crew[b]);
        m.cp().post(le(sum(aboard), capacity[h]));
      }

    // a guest boat does not visit the same host twice
    for (int b = 0; b < n; b++)
      for (int v = 0; v < n; v++) {
        if (v == b) continue;
        CPBoolVar[] visitsToV = new CPBoolVar[periods];
        for (int p = 0; p < periods; p++)
          visitsToV[p] = isEq(visits[p][b], v);
        m.cp().post(le(sum(visitsToV), 1));
      }

    // two crews meet at most once: they are at the same boat in at most one period
    for (int i = 0; i < n; i++)
      for (int j = i + 1; j < n; j++) {
        CPBoolVar[] meet = new CPBoolVar[periods];
        for (int p = 0; p < periods; p++) {
          meet[p] = m.boolVar();
          // meet is 1 exactly when the two crews are at the same boat in period p
          int[][] sameBoat = new int[n * n][];
          for (int a = 0; a < n; a++)
            for (int c = 0; c < n; c++)
              sameBoat[a * n + c] = new int[]{a, c, a == c ? 1 : 0};
          m.cp().post(table(new CPIntVar[]{visits[p][i], visits[p][j], meet[p]}, sameBoat));
        }
        m.cp().post(le(sum(meet), 1));
      }

    // minimise the number of host boats
    m.minimize(sum(isHost));

    out.put("visits", visits);
    out.put("is_host", isHost);
  }
}
