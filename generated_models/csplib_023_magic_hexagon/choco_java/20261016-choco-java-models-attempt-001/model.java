import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Magic hexagon: place the numbers 1 to NUM_CELLS in the 19 cells A..S of a
// hexagon so that every one of its 15 lines (rows and both diagonal directions)
// sums to the magic constant MAGIC_SUM.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int numCells = inst.getInt("NUM_CELLS");
    int magic = inst.getInt("MAGIC_SUM");

    // the cells are A, B, ..., S in reading order, row by row
    IntVar[] cell = m.intVarArray("cell", numCells, 1, numCells);
    IntVar A = cell[0], B = cell[1], C = cell[2], D = cell[3], E = cell[4], F = cell[5], G = cell[6],
        H = cell[7], I = cell[8], J = cell[9], K = cell[10], L = cell[11], M = cell[12], N = cell[13],
        O = cell[14], P = cell[15], Q = cell[16], R = cell[17], S = cell[18];

    // each of the numbers 1 to NUM_CELLS is used in exactly one cell
    m.allDifferent(cell, "AC").post();

    // the rows of the hexagon: top, upper middle, middle, lower middle, bottom
    m.sum(new IntVar[]{A, B, C}, "=", magic).post();
    m.sum(new IntVar[]{D, E, F, G}, "=", magic).post();
    m.sum(new IntVar[]{H, I, J, K, L}, "=", magic).post();
    m.sum(new IntVar[]{M, N, O, P}, "=", magic).post();
    m.sum(new IntVar[]{Q, R, S}, "=", magic).post();

    // the diagonals running down to the right
    m.sum(new IntVar[]{H, M, Q}, "=", magic).post();
    m.sum(new IntVar[]{D, I, N, R}, "=", magic).post();
    m.sum(new IntVar[]{A, E, J, O, S}, "=", magic).post();
    m.sum(new IntVar[]{B, F, K, P}, "=", magic).post();
    m.sum(new IntVar[]{C, G, L}, "=", magic).post();

    // the diagonals running down to the left
    m.sum(new IntVar[]{A, D, H}, "=", magic).post();
    m.sum(new IntVar[]{B, E, I, M}, "=", magic).post();
    m.sum(new IntVar[]{C, F, J, N, Q}, "=", magic).post();
    m.sum(new IntVar[]{G, K, O, R}, "=", magic).post();
    m.sum(new IntVar[]{L, P, S}, "=", magic).post();

    out.put("LD", cell);
  }
}
