import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;
import java.util.ArrayList;
import java.util.List;

// Mario collects gold by visiting houses, starting at Mario's house and ending at Luigi's house.
// Each travel between houses consumes fuel, and the total fuel must not exceed the fuel limit.
// s[i] is the house succeeding house i on the route, or i itself when house i is not on the route.
// Luigi's house is followed by Mario's house.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("nHouses");
    int mh = inst.getInt("marioHouse");
    int lh = inst.getInt("luigiHouse");
    int fuelLimit = inst.getInt("fuelLimit");
    int[] gold = inst.getIntArray("goldInHouse");
    int[][] fuel = inst.getIntMatrix("arc_fuel");
    int maxN = 15;

    // the successor array has the declared shape of 15 houses
    CPIntVar[] succ = new CPIntVar[maxN];
    for (int i = 0; i < maxN; i++) {
      succ[i] = i < n ? m.intVar(0, n - 1) : m.intVar(i, i);
    }

    // every house is succeeded by a different house, so the successors form a permutation
    m.cp().post(allDifferent(succ));

    // Mario's house starts the route, so it is not left alone
    m.cp().post(neq(succ[mh], mh));
    // Luigi's house is followed by Mario's house
    m.cp().post(eq(succ[lh], mh));

    // a house off the route is succeeded by itself
    CPBoolVar[] selfLoop = new CPBoolVar[n];
    CPBoolVar[] visited = new CPBoolVar[n];
    for (int i = 0; i < n; i++) {
      selfLoop[i] = isEq(succ[i], i);
      visited[i] = not(selfLoop[i]);
    }

    // the route is a single path from Mario's house to Luigi's house, with no separate loops
    // each route step moves to a later position, positions are distinct and Mario's house is first
    // a house off the route takes the position equal to its own number, so unused houses do not permute
    CPIntVar[] pos = new CPIntVar[n];
    for (int i = 0; i < n; i++) pos[i] = m.intVar(0, n - 1);
    m.cp().post(eq(pos[mh], 0));
    m.cp().post(allDifferent(pos));
    for (int i = 0; i < n; i++) {
      if (i == mh) continue;
      m.cp().post(implies(selfLoop[i], isEq(pos[i], i)));
    }
    for (int i = 0; i < n; i++) {
      if (i == mh) continue;
      for (int j = 0; j < n; j++) {
        if (j == i || j == mh) continue;
        m.cp().post(implies(isEq(succ[i], j), isLe(pos[i], pos[j])));
      }
    }

    // the fuel used by the travel from each house to its succeeding house, within the fuel limit
    // a house off the route uses no fuel, so its own entry is zero
    CPIntVar[] legFuel = new CPIntVar[n];
    for (int i = 0; i < n; i++) {
      int[] row = new int[n];
      for (int j = 0; j < n; j++) row[j] = (j == i) ? 0 : fuel[i][j];
      legFuel[i] = element(row, succ[i]);
    }
    m.cp().post(le(sum(legFuel), fuelLimit));

    // the gold collected is the gold of every visited house
    int totalGold = 0;
    for (int g : gold) totalGold += g;
    CPIntVar obj = m.intVar(0, totalGold);
    List<CPIntVar> goldTerms = new ArrayList<>();
    for (int i = 0; i < n; i++) {
      if (gold[i] == 0) continue;
      goldTerms.add(mul(visited[i], gold[i]));
    }
    m.cp().post(sum(goldTerms.toArray(new CPIntVar[0]), obj));
    m.maximize(obj);

    out.put("s", succ);
  }
}
