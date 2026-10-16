// Wolf, goat and cabbage river crossing: the farmer moves the wolf, goat, cabbage and himself from the
// starting shore to the destination shore, one crossing per stage, carrying at most one item, and no item
// is left alone with one it would eat.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int stages = inst.getInt("stage");   // number of stages, one shore position per stage

    // shore positions per stage: 0 = starting shore, 1 = destination shore
    BoolVar[] wolf = m.boolVarArray("wolf_pos", stages);
    BoolVar[] goat = m.boolVarArray("goat_pos", stages);
    BoolVar[] cabbage = m.boolVarArray("cabbage_pos", stages);
    BoolVar[] boat = m.boolVarArray("boat_pos", stages);

    // everything starts on the starting shore
    m.arithm(wolf[0], "=", 0).post();
    m.arithm(goat[0], "=", 0).post();
    m.arithm(cabbage[0], "=", 0).post();
    m.arithm(boat[0], "=", 0).post();

    // everything ends on the destination shore
    m.arithm(wolf[stages - 1], "=", 1).post();
    m.arithm(goat[stages - 1], "=", 1).post();
    m.arithm(cabbage[stages - 1], "=", 1).post();
    m.arithm(boat[stages - 1], "=", 1).post();

    for (int t = 0; t + 1 < stages; t++) {
      // the farmer rows the boat across the river at every stage
      m.arithm(boat[t], "!=", boat[t + 1]).post();

      // the boat carries only the farmer and a single item, so at most one item changes shore
      BoolVar movedWolf = m.arithm(wolf[t], "!=", wolf[t + 1]).reify();
      BoolVar movedGoat = m.arithm(goat[t], "!=", goat[t + 1]).reify();
      BoolVar movedCabbage = m.arithm(cabbage[t], "!=", cabbage[t + 1]).reify();
      m.sum(new BoolVar[]{movedWolf, movedGoat, movedCabbage}, "<=", 1).post();

      // an item crosses only in the boat, so it is on the farmer's shore before the crossing
      m.ifThen(m.arithm(wolf[t], "!=", wolf[t + 1]), m.arithm(wolf[t], "=", boat[t]));
      m.ifThen(m.arithm(goat[t], "!=", goat[t + 1]), m.arithm(goat[t], "=", boat[t]));
      m.ifThen(m.arithm(cabbage[t], "!=", cabbage[t + 1]), m.arithm(cabbage[t], "=", boat[t]));
    }

    for (int t = 0; t < stages; t++) {
      // the wolf would eat the goat if the farmer is not on the same shore
      m.ifThen(m.arithm(wolf[t], "=", goat[t]), m.arithm(goat[t], "=", boat[t]));

      // the goat would eat the cabbage if the farmer is not on the same shore
      m.ifThen(m.arithm(goat[t], "=", cabbage[t]), m.arithm(goat[t], "=", boat[t]));
    }

    out.put("wolf_pos", wolf);
    out.put("goat_pos", goat);
    out.put("cabbage_pos", cabbage);
    out.put("boat_pos", boat);
  }
}
