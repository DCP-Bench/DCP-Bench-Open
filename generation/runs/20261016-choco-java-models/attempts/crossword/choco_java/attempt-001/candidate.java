import org.chocosolver.solver.Model;
import org.chocosolver.solver.constraints.extension.Tuples;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Crossword: fill the 8 entries of the grid with 8 different words from the list of 15,
// so that the letters agree wherever two entries cross.
public class Submission {
  static final String[] WORDS = {
    "HOSES", "LASER", "SAILS", "SHEET", "STEER",      // length 5, sorted
    "HEEL", "HIKE", "KEEL", "KNOT", "LINE",            // length 4, sorted
    "AFT", "ALE", "EEL", "LEE", "TIE"                  // length 3, sorted
  };

  // entries in clue-number order: each is a list of grid cells {row, column} (1-based)
  static final int[][][] ENTRIES = {
    {{1,1},{1,2},{1,3},{1,4},{1,5}},   // 1 across
    {{1,3},{2,3},{3,3},{4,3},{5,3}},   // 2 down
    {{1,5},{2,5},{3,5},{4,5},{5,5}},   // 3 down
    {{3,2},{3,3},{3,4},{3,5}},         // 4 across
    {{3,4},{4,4},{5,4},{6,4}},         // 5 down
    {{4,1},{5,1},{6,1}},               // 6 down
    {{4,3},{4,4},{4,5}},               // 7 across
    {{5,1},{5,2},{5,3},{5,4},{5,5}}    // 8 across
  };

  public static void build(Instance inst, Model m, Outputs out) {
    // one letter variable (0..25 for A..Z) per open grid cell, shared by the entries through it
    IntVar[][] cell = new IntVar[7][6];
    // w[e]: index in WORDS of the word that fills entry e
    IntVar[] w = m.intVarArray("w", ENTRIES.length, 0, WORDS.length - 1);
    m.allDifferent(w, "AC").post();

    for (int e = 0; e < ENTRIES.length; e++) {
      int[][] cells = ENTRIES[e];
      int len = cells.length;
      IntVar[] vars = new IntVar[len + 1];
      vars[0] = w[e];
      for (int k = 0; k < len; k++) {
        int r = cells[k][0], c = cells[k][1];
        if (cell[r][c] == null) cell[r][c] = m.intVar("L" + r + c, 0, 25);
        vars[k + 1] = cell[r][c];
      }
      // the entry takes a word of its own length, and its letters are that word's letters
      Tuples t = new Tuples(true);
      for (int j = 0; j < WORDS.length; j++) {
        if (WORDS[j].length() != len) continue;
        int[] row = new int[len + 1];
        row[0] = j;
        for (int k = 0; k < len; k++) row[k + 1] = WORDS[j].charAt(k) - 'A';
        t.add(row);
      }
      m.table(vars, t).post();
    }

    out.put("E", w);
  }
}
