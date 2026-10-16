import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Mario: Mario starts at his house and must end at Luigi's house, visiting houses on the
// way. He collects the gold of every house he visits, travel between houses uses fuel,
// and the total fuel must not exceed the limit. Maximise the gold collected. Output s,
// where s[i] is the house after house i (s[i] = i if house i is not on the route).
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("nHouses");
    int mario = inst.getInt("marioHouse");
    int luigi = inst.getInt("luigiHouse");
    int fuelLimit = inst.getInt("fuelLimit");
    int[][] arcFuel = inst.getIntMatrix("arc_fuel");
    int[] gold = inst.getIntArray("goldInHouse");

    // s[i]: the house succeeding house i on the route
    IntVar[] succ = m.intVarArray("s", n, 0, n - 1);

    // the succeeding house of Luigi's house is Mario's house, so the route closes into a cycle
    m.arithm(succ[luigi], "=", mario).post();

    // the houses on the route form one cycle (Mario and Luigi are always on it);
    // houses not on the route loop on themselves
    IntVar length = m.intVar("route length", 2, n, true);
    m.subCircuit(succ, 0, length).post();

    // a house is visited when it is not looping on itself
    BoolVar[] visited = new BoolVar[n];
    for (int i = 0; i < n; i++) visited[i] = succ[i].ne(i).boolVar();

    // fuel used on the arc leaving each house: arc_fuel[i][succ[i]] (0 for a house not on the route)
    IntVar[] fuel = new IntVar[n];
    for (int i = 0; i < n; i++) fuel[i] = m.element("fuel" + i, arcFuel[i], succ[i]);

    // the total fuel of the route must not exceed the fuel limit
    IntVar totalFuel = m.sum("total fuel", fuel);
    m.arithm(totalFuel, "<=", fuelLimit).post();

    // gold collected: the gold of every visited house
    int goldMax = 0;
    for (int g : gold) goldMax += g;
    IntVar collected = m.intVar("gold collected", 0, goldMax, true);
    m.scalar(visited, gold, "=", collected).post();

    // maximise the gold collected
    m.setObjective(Model.MAXIMIZE, collected);

    out.put("s", succ);
  }
}
