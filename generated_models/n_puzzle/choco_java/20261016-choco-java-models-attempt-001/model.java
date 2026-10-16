import org.chocosolver.solver.Model;
import org.chocosolver.solver.constraints.extension.Tuples;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// N-puzzle: trace a sliding-tile puzzle from the start state to the end state in
// exactly N_STEPS states, including the start and the end. Each step slides one tile
// into the empty square (the blank, value 0), so the state changes at every step.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int steps = inst.getInt("N_STEPS");
    int[][] start = inst.getIntMatrix("puzzle_start");
    int[][] end = inst.getIntMatrix("puzzle_end");
    int g = start.length;          // the board is g x g
    int cells = g * g;             // cells 0..cells-1, row-major; values 0..cells-1, blank = 0

    // G[s][c]: value (tile number, 0 for the blank) on cell c at step s
    // P[s][v]: cell holding value v at step s; the two are inverse permutations
    IntVar[][] G = new IntVar[steps][cells];
    IntVar[][] P = new IntVar[steps][cells];
    for (int s = 0; s < steps; s++) {
      G[s] = m.intVarArray("cell" + s, cells, 0, cells - 1);
      P[s] = m.intVarArray("where" + s, cells, 0, cells - 1);
      m.inverseChanneling(P[s], G[s]).post();
    }

    // the start state and the end state are given
    for (int r = 0; r < g; r++) {
      for (int c = 0; c < g; c++) {
        G[0][r * g + c].eq(start[r][c]).post();
        G[steps - 1][r * g + c].eq(end[r][c]).post();
      }
    }

    // two cells are neighbours when they share an edge
    Tuples adjacent = new Tuples(true);
    for (int a = 0; a < cells; a++) {
      for (int b = 0; b < cells; b++) {
        int dr = Math.abs(a / g - b / g), dc = Math.abs(a % g - b % g);
        if (dr + dc == 1) adjacent.add(a, b);
      }
    }

    for (int s = 0; s + 1 < steps; s++) {
      // the blank (value 0) moves to a neighbouring cell at each step
      m.table(new IntVar[]{P[s][0], P[s + 1][0]}, adjacent).post();

      // the tile that the blank moves onto goes to the cell the blank leaves;
      // every other tile stays where it is
      for (int t = 1; t < cells; t++) {
        m.ifThenElse(
            m.arithm(P[s][t], "=", P[s + 1][0]),
            m.arithm(P[s + 1][t], "=", P[s][0]),
            m.arithm(P[s + 1][t], "=", P[s][t]));
      }
    }

    // the state at each step, as a g x g board
    IntVar[][][] board = new IntVar[steps][g][g];
    for (int s = 0; s < steps; s++) {
      for (int r = 0; r < g; r++) {
        for (int c = 0; c < g; c++) board[s][r][c] = G[s][r * g + c];
      }
    }

    out.put("steps", board);
  }
}
