import java.util.ArrayList;
import java.util.List;

import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Nonogram: shade squares in a grid of rows x cols so that the shaded runs of every row
// and of every column are the block sequence given for that row or column.
// board[r][c] = 1 when square (r, c) is shaded, 0 otherwise.
public class Submission {

  public static void build(Instance inst, Model m, Outputs out) {
    int rows = inst.getInt("rows");
    int cols = inst.getInt("cols");
    int[][] rowRules = inst.getIntMatrix("row_rules");
    int[][] colRules = inst.getIntMatrix("col_rules");

    // one 0/1 variable per square
    CPBoolVar[][] board = new CPBoolVar[rows][cols];
    for (int r = 0; r < rows; r++)
      for (int c = 0; c < cols; c++)
        board[r][c] = m.boolVar();

    // the blocks of each row, read from left to right, are the row's constraint
    for (int r = 0; r < rows; r++)
      addBlocks(m, board[r], blocksOf(rowRules[r]));

    // the blocks of each column, read from top to bottom, are the column's constraint
    for (int c = 0; c < cols; c++) {
      CPBoolVar[] column = new CPBoolVar[rows];
      for (int r = 0; r < rows; r++) column[r] = board[r][c];
      addBlocks(m, column, blocksOf(colRules[c]));
    }

    out.put("board", board);
  }

  // The block lengths in a rule, in order. Zeros pad the rule on the left and are dropped.
  static int[] blocksOf(int[] rule) {
    int n = 0;
    for (int v : rule) if (v != 0) n++;
    int[] blocks = new int[n];
    int i = 0;
    for (int v : rule) if (v != 0) blocks[i++] = v;
    return blocks;
  }

  // The cells read as exactly these blocks, in order: a shaded run of each length, separated
  // by at least one unshaded square. The line is checked by a deterministic automaton. A state
  // {j, r} means j blocks have begun and r squares of the current block are shaded so far
  // (r = 0 between blocks). Each cell gives one table row per legal (state, value, next state).
  static void addBlocks(Model m, CPIntVar[] cells, int[] blocks) {
    List<int[]> states = reachableStates(blocks);
    int S = states.size();
    int n = cells.length;

    // st[c] is the automaton state before cell c; st[0] is the start state
    CPIntVar[] st = m.intVarArray(n + 1, 0, S - 1);
    m.cp().post(eq(st[0], 0));

    for (int c = 0; c < n; c++) {
      List<int[]> legal = new ArrayList<>();
      for (int from = 0; from < S; from++)
        for (int value = 0; value <= 1; value++) {
          int[] next = step(states.get(from), value, blocks);
          if (next == null) continue;
          int to = indexOf(states, next);
          // the last cell must leave the line in an accepting state
          if (c == n - 1 && !accepts(next, blocks)) continue;
          legal.add(new int[]{from, value, to});
        }
      CPIntVar[] xs = new CPIntVar[]{st[c], cells[c], st[c + 1]};
      m.cp().post(table(xs, legal.toArray(new int[0][])));
    }
  }

  // every state reachable from the start state {0, 0} by reading 0s and 1s
  static List<int[]> reachableStates(int[] blocks) {
    List<int[]> states = new ArrayList<>();
    states.add(new int[]{0, 0});
    for (int i = 0; i < states.size(); i++)
      for (int value = 0; value <= 1; value++) {
        int[] next = step(states.get(i), value, blocks);
        if (next != null && indexOf(states, next) < 0) states.add(next);
      }
    return states;
  }

  // the state after reading one square with this value, or null when the blocks break
  static int[] step(int[] s, int value, int[] blocks) {
    int j = s[0];
    int r = s[1];
    int k = blocks.length;
    if (value == 0) {
      if (r == 0) return s;                              // a gap continues
      if (r == blocks[j - 1]) return new int[]{j, 0};    // the current block ends here
      return null;                                       // the current block is too short
    }
    if (r == 0) return j < k ? new int[]{j + 1, 1} : null;  // the next block begins
    return r < blocks[j - 1] ? new int[]{j, r + 1} : null;  // the current block grows
  }

  // the line may end here: every block has begun and the last one is complete or ended by a gap
  static boolean accepts(int[] s, int[] blocks) {
    int k = blocks.length;
    return s[0] == k && (s[1] == 0 || s[1] == blocks[k - 1]);
  }

  static int indexOf(List<int[]> states, int[] s) {
    for (int i = 0; i < states.size(); i++)
      if (states.get(i)[0] == s[0] && states.get(i)[1] == s[1]) return i;
    return -1;
  }
}
