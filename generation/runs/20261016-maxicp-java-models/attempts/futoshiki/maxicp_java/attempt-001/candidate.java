// Futoshiki: fill an n x n grid with the digits 1..n so that every row and every
// column holds each digit once, some cells are given, and some pairs of
// neighbouring cells are marked "<" (the first cell is smaller than the second).

import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the grid size comes from the instance: the given-digits matrix is n x n
    int[][] values = inst.getIntMatrix("values");
    int n = values.length;

    // every cell holds a digit from 1 to n
    CPIntVar[][] grid = new CPIntVar[n][n];
    for (int i = 0; i < n; i++) {
      for (int j = 0; j < n; j++) {
        grid[i][j] = m.intVar(1, n);
      }
    }

    // the given digits are fixed in the grid (0 means empty)
    for (int i = 0; i < n; i++) {
      for (int j = 0; j < n; j++) {
        if (values[i][j] != 0) {
          m.cp().post(eq(grid[i][j], values[i][j]));
        }
      }
    }

    // each row contains each digit once
    for (int i = 0; i < n; i++) {
      m.cp().post(allDifferent(grid[i]));
    }

    // each column contains each digit once
    for (int j = 0; j < n; j++) {
      CPIntVar[] column = new CPIntVar[n];
      for (int i = 0; i < n; i++) {
        column[i] = grid[i][j];
      }
      m.cp().post(allDifferent(column));
    }

    // each inequality sign: the cell at (r1, c1) is lower than the cell at (r2, c2);
    // the file gives 1-based row and column numbers
    int[][] lt = inst.getIntMatrix("lt");
    for (int[] clue : lt) {
      CPIntVar smaller = grid[clue[0] - 1][clue[1] - 1];
      CPIntVar larger = grid[clue[2] - 1][clue[3] - 1];
      m.cp().post(ge(larger, plus(smaller, 1)));
    }

    // the output is the completed grid
    out.put("grid", grid);
  }
}
