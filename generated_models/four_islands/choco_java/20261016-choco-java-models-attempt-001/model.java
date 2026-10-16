import org.chocosolver.solver.Model;
import org.chocosolver.solver.constraints.extension.Tuples;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Four islands: find the name, export and tourist attraction of each island on the map.
// Map positions: A=0 (north-west), B=1 (north-east), C=2 (south-west), D=3 (south-east).
// Bridges: A-B, A-C, B-D, C-D. The positions and clues are fixed by the problem statement.
public class Submission {
  // position pairs (x, y) for the given relation, as a table constraint
  static Tuples pairs(int[][] allowed) {
    Tuples t = new Tuples(true);
    for (int[] p : allowed) t.add(p);
    return t;
  }

  public static void build(Instance inst, Model m, Outputs out) {
    // position of each island: Pwana, Quero, Rayou, Skern
    IntVar[] island = m.intVarArray("island", 4, 0, 3);
    // position of each export: alabaster, bananas, coconuts, durian fruit
    IntVar[] export = m.intVarArray("export", 4, 0, 3);
    // position of each attraction: resort hotel, ice skating rink, jai alai stadium, koala preserve
    IntVar[] attraction = m.intVarArray("attraction", 4, 0, 3);

    final int PWANA = 0, QUERO = 1, RAYOU = 2, SKERN = 3;
    final int ALABASTER = 0, BANANAS = 1, DURIAN = 3;
    final int HOTEL = 0, ICE = 1, JAI_ALAI = 2, KOALA = 3;

    // each island, export and attraction is a different position
    m.allDifferent(island, "AC").post();
    m.allDifferent(export, "AC").post();
    m.allDifferent(attraction, "AC").post();

    // clue 1: the koala preserve is due south of Pwana (A is north of C, B is north of D)
    m.table(new IntVar[]{island[PWANA], attraction[KOALA]},
        pairs(new int[][]{{0, 2}, {1, 3}})).post();

    // clue 2: the alabaster island is due west of Quero (A is west of B, C is west of D)
    m.table(new IntVar[]{export[ALABASTER], island[QUERO]},
        pairs(new int[][]{{0, 1}, {2, 3}})).post();

    // clue 3: the resort hotel is due east of the durian island
    m.table(new IntVar[]{export[DURIAN], attraction[HOTEL]},
        pairs(new int[][]{{0, 1}, {2, 3}})).post();

    // clue 4: Skern and the jai alai stadium are connected by a north-south bridge
    m.table(new IntVar[]{island[SKERN], attraction[JAI_ALAI]},
        pairs(new int[][]{{0, 2}, {2, 0}, {1, 3}, {3, 1}})).post();

    // clue 5: Rayou and the banana island are connected by an east-west bridge
    m.table(new IntVar[]{island[RAYOU], export[BANANAS]},
        pairs(new int[][]{{0, 1}, {1, 0}, {2, 3}, {3, 2}})).post();

    // clue 6: the ice skating rink and the jai alai stadium are not connected by a bridge
    m.table(new IntVar[]{attraction[ICE], attraction[JAI_ALAI]},
        pairs(new int[][]{{0, 3}, {3, 0}, {1, 2}, {2, 1}})).post();

    out.put("island", island);
    out.put("export", export);
    out.put("attraction", attraction);
  }
}
