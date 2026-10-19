import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Progressive party: a yacht club party. Some boats are hosts and stay where they are; the
// crews of the other boats visit one host in each period. Minimise the number of host boats.
// at[p][b][h] = 1 when boat b is at boat h in period p (a host is at itself).
// visits[p][b] is the boat that boat b is at in period p.
// is_host[b] = 1 when boat b is a host.
public class Submission {

  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n_boats");
    int periods = inst.getInt("n_periods");
    int[] capacity = inst.getIntArray("capacity");
    int[] crew = inst.getIntArray("crew_size");

    // whether each boat is a host
    CPBoolVar[] isHost = m.boolVarArray(n);

    // one 0/1 variable for each (period, boat, boat) triple
    CPBoolVar[][][] at = new CPBoolVar[periods][n][n];
    for (int p = 0; p < periods; p++)
      for (int b = 0; b < n; b++)
        for (int h = 0; h < n; h++)
          at[p][b][h] = m.boolVar();

    // every boat is at exactly one boat in each period
    for (int p = 0; p < periods; p++)
      for (int b = 0; b < n; b++)
        m.cp().post(eq(sum(at[p][b]), 1));

    // a host boat stays at itself in every period, and a guest boat is not at itself
    for (int p = 0; p < periods; p++)
      for (int b = 0; b < n; b++)
        m.cp().post(eq(at[p][b][b], isHost[b]));

    // a guest boat visits only host boats
    for (int p = 0; p < periods; p++)
      for (int b = 0; b < n; b++)
        for (int h = 0; h < n; h++)
          if (h != b) m.cp().post(implies(at[p][b][h], isHost[h]));

    // the people aboard a host boat, its host crew and the guest crews, do not exceed its capacity
    for (int p = 0; p < periods; p++)
      for (int h = 0; h < n; h++) {
        CPIntVar[] aboard = new CPIntVar[n];
        for (int b = 0; b < n; b++)
          aboard[b] = mul(at[p][b][h], crew[b]);
        m.cp().post(le(sum(aboard), capacity[h]));
      }

    // a guest boat does not visit the same host twice
    for (int b = 0; b < n; b++)
      for (int h = 0; h < n; h++) {
        if (h == b) continue;
        CPBoolVar[] visitsToH = new CPBoolVar[periods];
        for (int p = 0; p < periods; p++)
          visitsToH[p] = at[p][b][h];
        m.cp().post(le(sum(visitsToH), 1));
      }

    // two crews meet at most once: they are at the same boat in at most one period
    for (int i = 0; i < n; i++)
      for (int j = i + 1; j < n; j++) {
        CPBoolVar[] same = new CPBoolVar[periods];
        for (int p = 0; p < periods; p++) {
          // same[p] is forced to 1 when the two crews are at a common boat h in period p
          same[p] = m.boolVar();
          for (int h = 0; h < n; h++)
            m.cp().post(le(sum(new CPIntVar[]{at[p][i][h], at[p][j][h], minus(same[p])}), 1));
        }
        m.cp().post(le(sum(same), 1));
      }

    // the visit schedule: the boat each boat is at in each period
    CPIntVar[][] visits = new CPIntVar[periods][n];
    for (int p = 0; p < periods; p++)
      for (int b = 0; b < n; b++) {
        CPIntVar[] boatIndex = new CPIntVar[n];
        for (int h = 0; h < n; h++)
          boatIndex[h] = mul(at[p][b][h], h);
        visits[p][b] = sum(boatIndex);
      }

    // minimise the number of host boats
    m.minimize(sum(isHost));

    out.put("visits", visits);
    out.put("is_host", isHost);
  }
}
