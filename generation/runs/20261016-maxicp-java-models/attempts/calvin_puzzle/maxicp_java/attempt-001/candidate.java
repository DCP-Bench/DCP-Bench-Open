// Calvin puzzle: fill an n by n grid with the numbers 1..n^2, each used once, so that
// the numbers form a sequence 1, 2, ..., n^2. Consecutive numbers are placed either
// three squares apart horizontally or vertically, or two squares apart diagonally.
// The output x is the grid, one row of integers per line.

import java.util.ArrayList;
import java.util.List;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int size = n * n;

    // the grid: the number written on each square, 1..n^2
    CPIntVar[][] x = new CPIntVar[n][n];
    CPIntVar[] flat = new CPIntVar[size];
    for (int i = 0; i < n; i++) {
      for (int j = 0; j < n; j++) {
        x[i][j] = m.intVar(1, size);
        flat[i * n + j] = x[i][j];
      }
    }

    // fill every square with a different number, each of 1..n^2 used once
    m.cp().post(allDifferent(flat));

    // the square where each number sits, as an index i*n+j: pos[k-1] for number k
    CPIntVar[] pos = m.intVarArray(size, 0, size - 1);
    // each number sits on one square, and each square holds one number
    m.cp().post(allDifferent(pos));

    // pos and the grid say the same thing: number k is on square p exactly when pos[k-1] = p
    for (int k = 1; k <= size; k++) {
      for (int p = 0; p < size; p++) {
        m.cp().post(eq(isEq(pos[k - 1], p), isEq(x[p / n][p % n], k)));
      }
    }

    // the moves from a square to the square of the next number:
    // three squares away horizontally or vertically, or two squares away diagonally
    List<int[]> moves = new ArrayList<>();
    int[][] steps = {{0, 3}, {0, -3}, {3, 0}, {-3, 0}, {2, 2}, {2, -2}, {-2, 2}, {-2, -2}};
    for (int i = 0; i < n; i++) {
      for (int j = 0; j < n; j++) {
        for (int[] s : steps) {
          int a = i + s[0];
          int b = j + s[1];
          if (a >= 0 && a < n && b >= 0 && b < n) {
            moves.add(new int[] {i * n + j, a * n + b});
          }
        }
      }
    }
    int[][] allowed = moves.toArray(new int[0][]);

    // the next number is placed by one of those moves from the square of the previous number
    for (int k = 1; k < size; k++) {
      m.cp().post(table(new CPIntVar[] {pos[k - 1], pos[k]}, allowed));
    }

    out.put("x", x);
  }
}
