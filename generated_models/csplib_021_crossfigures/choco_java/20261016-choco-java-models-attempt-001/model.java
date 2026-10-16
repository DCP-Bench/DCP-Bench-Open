// Crossfigures: fill the 9x9 grid so that each across and down entry is the number its clue
// describes. The puzzle is fixed by the description (grid and clues), so it is written out
// here; the instance carries no data.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {

  public static void build(Instance inst, Model m, Outputs out) {
    // digit variables for every cell that lies in some entry (1-based rows and columns)
    IntVar[][] cell = new IntVar[10][10];

    // 4-digit squares, 2-digit primes, 2-digit squares (problem's clue types)
    int[] squares4 = new int[68];
    for (int s = 32; s <= 99; s++) squares4[s - 32] = s * s;
    int[] primes2 = {11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97};
    int[] squares2 = {16, 25, 36, 49, 64, 81};

    // across entries
    IntVar A1 = entry(m, cell, "A1", 1, 1, 4, true, null);
    IntVar A4 = entry(m, cell, "A4", 1, 6, 4, true, null);
    IntVar A7 = entry(m, cell, "A7", 2, 1, 2, true, null);
    IntVar A8 = entry(m, cell, "A8", 2, 4, 3, true, null);
    IntVar A9 = entry(m, cell, "A9", 2, 8, 2, true, null);
    IntVar A10 = entry(m, cell, "A10", 3, 3, 2, true, new int[]{72});
    IntVar A11 = entry(m, cell, "A11", 3, 6, 2, true, null);
    IntVar A13 = entry(m, cell, "A13", 4, 1, 4, true, null);
    IntVar A15 = entry(m, cell, "A15", 4, 6, 4, true, null);
    IntVar A17 = entry(m, cell, "A17", 6, 1, 4, true, null);
    IntVar A20 = entry(m, cell, "A20", 6, 6, 4, true, squares4);
    IntVar A23 = entry(m, cell, "A23", 7, 3, 2, true, primes2);
    IntVar A24 = entry(m, cell, "A24", 7, 6, 2, true, squares2);
    IntVar A25 = entry(m, cell, "A25", 8, 1, 2, true, null);
    IntVar A27 = entry(m, cell, "A27", 8, 4, 3, true, null);
    IntVar A28 = entry(m, cell, "A28", 8, 8, 2, true, new int[]{48});
    IntVar A29 = entry(m, cell, "A29", 9, 1, 4, true, new int[]{1008});
    IntVar A30 = entry(m, cell, "A30", 9, 6, 4, true, null);

    // down entries
    IntVar D1 = entry(m, cell, "D1", 1, 1, 4, false, null);
    IntVar D2 = entry(m, cell, "D2", 1, 2, 2, false, new int[]{60});
    IntVar D3 = entry(m, cell, "D3", 1, 4, 4, false, null);
    IntVar D4 = entry(m, cell, "D4", 1, 6, 4, false, null);
    IntVar D5 = entry(m, cell, "D5", 1, 8, 2, false, null);
    IntVar D6 = entry(m, cell, "D6", 1, 9, 4, false, null);
    IntVar D10 = entry(m, cell, "D10", 3, 3, 2, false, null);
    IntVar D12 = entry(m, cell, "D12", 3, 7, 2, false, null);
    IntVar D14 = entry(m, cell, "D14", 4, 2, 3, false, null);
    IntVar D16 = entry(m, cell, "D16", 4, 8, 3, false, null);
    IntVar D17 = entry(m, cell, "D17", 6, 1, 4, false, null);
    IntVar D18 = entry(m, cell, "D18", 6, 3, 2, false, null);
    IntVar D19 = entry(m, cell, "D19", 6, 4, 4, false, null);
    IntVar D20 = entry(m, cell, "D20", 6, 6, 4, false, null);
    IntVar D21 = entry(m, cell, "D21", 6, 7, 2, false, null);
    IntVar D22 = entry(m, cell, "D22", 6, 9, 4, false, null);
    IntVar D26 = entry(m, cell, "D26", 8, 2, 2, false, null);
    IntVar D28 = entry(m, cell, "D28", 8, 8, 2, false, null);

    // across clues
    // 1 across: 27 across times two
    lin(m, new IntVar[]{A1, A27}, new int[]{1, -2}, 0);
    // 4 across: 4 down plus seventy-one
    lin(m, new IntVar[]{A4, D4}, new int[]{1, -1}, 71);
    // 7 across: 18 down plus four
    lin(m, new IntVar[]{A7, D18}, new int[]{1, -1}, 4);
    // 8 across: 6 down divided by sixteen
    lin(m, new IntVar[]{A8, D6}, new int[]{16, -1}, 0);
    // 9 across: 2 down minus eighteen
    lin(m, new IntVar[]{A9, D2}, new int[]{1, -1}, -18);
    // 11 across: 5 down minus seventy
    lin(m, new IntVar[]{A11, D5}, new int[]{1, -1}, -70);
    // 13 across: 26 down times 23 across
    m.times(D26, A23, A13).post();
    // 15 across: 6 down minus 350
    lin(m, new IntVar[]{A15, D6}, new int[]{1, -1}, -350);
    // 17 across: 25 across times 23 across
    m.times(A25, A23, A17).post();
    // 25 across: 20 across divided by seventeen
    lin(m, new IntVar[]{A25, A20}, new int[]{17, -1}, 0);
    // 27 across: 6 down divided by four
    lin(m, new IntVar[]{A27, D6}, new int[]{4, -1}, 0);
    // 30 across: 22 down plus 450
    lin(m, new IntVar[]{A30, D22}, new int[]{1, -1}, 450);

    // down clues
    // 1 down: 1 across plus twenty-seven
    lin(m, new IntVar[]{D1, A1}, new int[]{1, -1}, 27);
    // 3 down: 30 across plus 888
    lin(m, new IntVar[]{D3, A30}, new int[]{1, -1}, 888);
    // 4 down: two times 17 across
    lin(m, new IntVar[]{D4, A17}, new int[]{1, -2}, 0);
    // 5 down: 29 across divided by twelve
    lin(m, new IntVar[]{D5, A29}, new int[]{12, -1}, 0);
    // 6 down: 28 across times 23 across
    m.times(A28, A23, D6).post();
    // 10 down: 10 across plus four
    lin(m, new IntVar[]{D10, A10}, new int[]{1, -1}, 4);
    // 12 down: three times 24 across
    lin(m, new IntVar[]{D12, A24}, new int[]{1, -3}, 0);
    // 14 down: 13 across divided by sixteen
    lin(m, new IntVar[]{D14, A13}, new int[]{16, -1}, 0);
    // 16 down: 28 down times fifteen
    lin(m, new IntVar[]{D16, D28}, new int[]{1, -15}, 0);
    // 17 down: 13 across minus 399
    lin(m, new IntVar[]{D17, A13}, new int[]{1, -1}, -399);
    // 18 down: 29 across divided by eighteen
    lin(m, new IntVar[]{D18, A29}, new int[]{18, -1}, 0);
    // 19 down: 22 down minus ninety-four
    lin(m, new IntVar[]{D19, D22}, new int[]{1, -1}, -94);
    // 20 down: 20 across minus nine
    lin(m, new IntVar[]{D20, A20}, new int[]{1, -1}, -9);
    // 21 down: 25 across minus fifty-two
    lin(m, new IntVar[]{D21, A25}, new int[]{1, -1}, -52);
    // 22 down: 20 down times six
    lin(m, new IntVar[]{D22, D20}, new int[]{1, -6}, 0);
    // 26 down: five times 24 across
    lin(m, new IntVar[]{D26, A24}, new int[]{1, -5}, 0);
    // 28 down: 21 down plus twenty-seven
    lin(m, new IntVar[]{D28, D21}, new int[]{1, -1}, 27);

    // the solved grid; cells outside every entry are 0
    IntVar[][] grid = new IntVar[9][9];
    for (int r = 1; r <= 9; r++) {
      for (int c = 1; c <= 9; c++) {
        grid[r - 1][c - 1] = cell[r][c] == null ? m.intVar(0) : cell[r][c];
      }
    }
    out.put("M", grid);
  }

  // Creates the entry starting at (r, c) with the given length, across or down, and returns its value.
  // The digits are read from the top-left, so the first digit is the most significant.
  // allowed: the listed values for a constant or a prime/square clue; null for any number of that length.
  static IntVar entry(Model m, IntVar[][] cell, String name, int r, int c, int len, boolean across, int[] allowed) {
    IntVar[] digits = new IntVar[len];
    for (int i = 0; i < len; i++) {
      int rr = across ? r : r + i;
      int cc = across ? c + i : c;
      if (cell[rr][cc] == null) cell[rr][cc] = m.intVar("cell_" + rr + "_" + cc, 0, 9);
      digits[i] = cell[rr][cc];
    }
    // a number has no leading zero
    m.arithm(digits[0], ">=", 1).post();
    int[] weights = new int[len];
    for (int i = 0; i < len; i++) weights[i] = pow10(len - 1 - i);
    IntVar value = allowed == null
        ? m.intVar(name, pow10(len - 1), pow10(len) - 1, true)
        : m.intVar(name, allowed);
    m.scalar(digits, weights, "=", value).post();
    return value;
  }

  // sum of coefficients times variables equals the constant
  static void lin(Model m, IntVar[] vars, int[] coeffs, int constant) {
    m.scalar(vars, coeffs, "=", constant).post();
  }

  static int pow10(int k) {
    int p = 1;
    for (int i = 0; i < k; i++) p *= 10;
    return p;
  }
}
