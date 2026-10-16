// Wolf, goat and cabbage river crossing. A farmer ferries a wolf, a goat and a cabbage across a river.
// The boat carries the farmer and at most one item. Left on a shore without the farmer, the wolf eats the goat,
// or the goat eats the cabbage. Each stage is one state of the four positions: shore 0 is the starting shore,
// shore 1 the destination. Stage 0 is the start and the last stage is the destination.
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;
import java.util.ArrayList;
import java.util.List;

public class Submission {

  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("stage");

    CPBoolVar[] wolf = m.boolVarArray(n);
    CPBoolVar[] goat = m.boolVarArray(n);
    CPBoolVar[] cabbage = m.boolVarArray(n);
    CPBoolVar[] boat = m.boolVarArray(n);

    // the farmer crosses the river at every stage, so the boat alternates shores, starting on shore 0
    for (int i = 0; i < n; i++) {
      m.cp().post(eq(boat[i], i % 2));
    }

    // at the start, the farmer, the wolf, the goat and the cabbage are all on the starting shore
    m.cp().post(eq(wolf[0], 0));
    m.cp().post(eq(goat[0], 0));
    m.cp().post(eq(cabbage[0], 0));

    // at the end, the wolf, the goat and the cabbage are all on the destination shore
    m.cp().post(eq(wolf[n - 1], 1));
    m.cp().post(eq(goat[n - 1], 1));
    m.cp().post(eq(cabbage[n - 1], 1));

    // at every stage, the wolf and the goat are not left alone together without the farmer
    // and the goat and the cabbage are not left alone together without the farmer
    int[][] safe = safeRows();
    for (int i = 0; i < n; i++) {
      m.cp().post(table(new CPIntVar[] {wolf[i], goat[i], boat[i]}, safe));
      m.cp().post(table(new CPIntVar[] {goat[i], cabbage[i], boat[i]}, safe));
    }

    // between two stages, the farmer crosses with at most one item, and an item can only cross
    // from the shore the boat is on
    int[][] cross = crossRows();
    for (int i = 0; i + 1 < n; i++) {
      m.cp().post(table(new CPIntVar[] {
          boat[i], wolf[i], goat[i], cabbage[i],
          boat[i + 1], wolf[i + 1], goat[i + 1], cabbage[i + 1]}, cross));
    }

    out.put("wolf_pos", wolf);
    out.put("goat_pos", goat);
    out.put("cabbage_pos", cabbage);
    out.put("boat_pos", boat);
  }

  // allowed (first, second, farmer) shore triples: the pair is not on the same shore away from the farmer
  static int[][] safeRows() {
    List<int[]> rows = new ArrayList<>();
    for (int a = 0; a <= 1; a++) {
      for (int b = 0; b <= 1; b++) {
        for (int farmer = 0; farmer <= 1; farmer++) {
          boolean eaten = a == b && a != farmer;
          if (!eaten) rows.add(new int[] {a, b, farmer});
        }
      }
    }
    return rows.toArray(new int[0][]);
  }

  // allowed (farmer, wolf, goat, cabbage) before and after one crossing: the farmer changes shore,
  // at most one item changes shore, and it must be on the farmer's shore before it changes
  // variable order: boat, wolf, goat, cabbage at stage i, then the same at stage i+1
  static int[][] crossRows() {
    List<int[]> rows = new ArrayList<>();
    for (int code = 0; code < (1 << 8); code++) {
      int[] v = new int[8];
      for (int k = 0; k < 8; k++) v[k] = (code >> k) & 1;
      if (v[4] != 1 - v[0]) continue;
      int moved = 0;
      boolean ok = true;
      for (int item = 1; item <= 3; item++) {
        if (v[item] != v[item + 4]) {
          moved++;
          if (v[item] != v[0]) ok = false;
        }
      }
      if (ok && moved <= 1) rows.add(v);
    }
    return rows.toArray(new int[0][]);
  }
}
