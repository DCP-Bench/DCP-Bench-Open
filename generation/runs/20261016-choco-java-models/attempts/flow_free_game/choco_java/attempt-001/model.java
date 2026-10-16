import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Flow Free on a 5x5 board: colour every cell with one of the colours 1 to 5 so that each
// colour's two given endpoints are joined by a single pipe, the pipes cover the whole
// board and no two pipes cross or overlap.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] board = inst.getIntMatrix("board");
    int rows = board.length;
    int cols = board[0].length;
    int n = rows * cols;
    int colours = 0;
    for (int[] row : board) for (int v : row) colours = Math.max(colours, v);

    // flat[i]: colour of cell i = r * cols + c. Given cells are fixed to their colour.
    IntVar[] flat = new IntVar[n];
    for (int i = 0; i < n; i++) {
      int v = board[i / cols][i % cols];
      flat[i] = v == 0 ? m.intVar("cell" + i, 1, colours) : m.intVar(v);
    }

    // neighbours of each cell, horizontally and vertically
    int[][] nbr = new int[n][];
    for (int i = 0; i < n; i++) {
      int r = i / cols, c = i % cols;
      int[] tmp = new int[4];
      int k = 0;
      if (r > 0) tmp[k++] = i - cols;
      if (r < rows - 1) tmp[k++] = i + cols;
      if (c > 0) tmp[k++] = i - 1;
      if (c < cols - 1) tmp[k++] = i + 1;
      nbr[i] = java.util.Arrays.copyOf(tmp, k);
    }

    // start[k]: the first given endpoint of colour k, where the pipe is grown from
    int[] start = new int[colours + 1];
    java.util.Arrays.fill(start, -1);
    for (int i = 0; i < n; i++) {
      int v = board[i / cols][i % cols];
      if (v != 0 && start[v] < 0) start[v] = i;
    }

    for (int k = 1; k <= colours; k++) {
      // dist[i]: number of steps from the start endpoint of colour k along its pipe
      IntVar[] dist = new IntVar[n];
      for (int i = 0; i < n; i++) dist[i] = m.intVar("dist" + k + "_" + i, 0, n - 1);
      m.arithm(dist[start[k]], "=", 0).post();

      // same[i]: the cell i has colour k
      BoolVar[] same = new BoolVar[n];
      for (int i = 0; i < n; i++) same[i] = m.isEq(flat[i], k);

      for (int i = 0; i < n; i++) {
        // number of neighbours of cell i that have colour k
        BoolVar[] nb = new BoolVar[nbr[i].length];
        for (int t = 0; t < nb.length; t++) nb[t] = same[nbr[i][t]];

        if (board[i / cols][i % cols] == k) {
          // a given endpoint has exactly one neighbour in its pipe
          m.sum(nb, "=", 1).post();
        } else {
          // a cell inside a pipe has exactly two neighbours in its pipe
          m.ifThen(same[i], m.sum(nb, "=", 2));
        }

        if (i != start[k]) {
          // a cell of the pipe other than the start is at least one step from the start
          m.ifThen(same[i], m.arithm(dist[i], ">=", 1));

          // and has a neighbour of the same colour one step closer to the start
          BoolVar[] closer = new BoolVar[nbr[i].length];
          for (int t = 0; t < nbr[i].length; t++) {
            int j = nbr[i][t];
            BoolVar w = m.boolVar("w" + k + "_" + i + "_" + j);
            BoolVar step = m.boolVar("step" + k + "_" + i + "_" + j);
            m.reifyXeqYC(dist[j], dist[i], -1, step);
            m.ifThen(w, m.arithm(same[j], "=", 1));
            m.ifThen(w, m.arithm(step, "=", 1));
            m.ifThen(w, m.arithm(same[i], "=", 1));
            closer[t] = w;
          }
          m.ifThen(same[i], m.sum(closer, ">=", 1));
        }
      }
    }

    // the board, one colour per cell
    IntVar[][] B = new IntVar[rows][cols];
    for (int r = 0; r < rows; r++) for (int c = 0; c < cols; c++) B[r][c] = flat[r * cols + c];
    out.put("B", B);
  }
}
