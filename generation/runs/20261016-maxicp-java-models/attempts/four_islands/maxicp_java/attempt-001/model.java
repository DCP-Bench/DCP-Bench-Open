// Four islands (Pwana, Quero, Rayou, Skern) in a South Pacific nation, joined by bridges
// in a square. Each island has a different export and a different tourist attraction.
// Map positions: A=0 (north-west), B=1 (north-east), C=2 (south-west), D=3 (south-east).
// Bridges: A-B, A-C, B-D, C-D. Islands A-D and B-C are not connected.
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {

  // position pairs (x, y) where x is due south of y, due west of y, and so on
  static final int[][] DUE_SOUTH = {{2, 0}, {3, 1}};
  static final int[][] DUE_WEST = {{0, 1}, {2, 3}};
  static final int[][] DUE_EAST = {{1, 0}, {3, 2}};
  // pairs connected by a north-south bridge (A-C, B-D) and by an east-west bridge (A-B, C-D)
  static final int[][] NORTH_SOUTH_BRIDGE = {{0, 2}, {2, 0}, {1, 3}, {3, 1}};
  static final int[][] EAST_WEST_BRIDGE = {{0, 1}, {1, 0}, {2, 3}, {3, 2}};
  // pairs not connected by any bridge (the diagonals A-D and B-C)
  static final int[][] NOT_BRIDGED = {{0, 3}, {3, 0}, {1, 2}, {2, 1}};

  public static void build(Instance inst, Model m, Outputs out) {
    // island[i] = map position of island i: 0 Pwana, 1 Quero, 2 Rayou, 3 Skern
    CPIntVar[] island = m.intVarArray(4, 0, 3);
    // export[j] = map position of export j: 0 alabaster, 1 bananas, 2 coconuts, 3 durian fruit
    CPIntVar[] export = m.intVarArray(4, 0, 3);
    // attraction[k] = map position of attraction k: 0 resort hotel, 1 ice skating rink,
    // 2 jai alai stadium, 3 koala preserve
    CPIntVar[] attraction = m.intVarArray(4, 0, 3);

    final int PWANA = 0, QUERO = 1, RAYOU = 2, SKERN = 3;
    final int ALABASTER = 0, BANANAS = 1, DURIAN = 3;
    final int HOTEL = 0, RINK = 1, JAI_ALAI = 2, KOALA = 3;

    // each island, export and attraction sits on a different place on the map
    m.cp().post(allDifferent(island));
    m.cp().post(allDifferent(export));
    m.cp().post(allDifferent(attraction));

    // the island noted for its koala preserve is due south of Pwana
    m.cp().post(table(new CPIntVar[] {attraction[KOALA], island[PWANA]}, DUE_SOUTH));

    // the island with the largest alabaster quarry is due west of Quero
    m.cp().post(table(new CPIntVar[] {export[ALABASTER], island[QUERO]}, DUE_WEST));

    // the island with the resort hotel is due east of the one that exports durian fruit
    m.cp().post(table(new CPIntVar[] {attraction[HOTEL], export[DURIAN]}, DUE_EAST));

    // Skern and the island with the jai alai stadium are connected by a north-south bridge
    m.cp().post(table(new CPIntVar[] {island[SKERN], attraction[JAI_ALAI]}, NORTH_SOUTH_BRIDGE));

    // Rayou and the island that exports bananas are connected by an east-west bridge
    m.cp().post(table(new CPIntVar[] {island[RAYOU], export[BANANAS]}, EAST_WEST_BRIDGE));

    // the islands noted for the largest ice skating rink and for the jai alai stadium
    // are not connected by a bridge
    m.cp().post(table(new CPIntVar[] {attraction[RINK], attraction[JAI_ALAI]}, NOT_BRIDGED));

    out.put("island", island);
    out.put("export", export);
    out.put("attraction", attraction);
  }
}
