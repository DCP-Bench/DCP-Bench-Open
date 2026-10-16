// Fill a 4x4 Sudoku: every row, every column and every 2x2 box holds 1 to 4 once each,
// and the given digits stay. Shows: satisfy with find-one, allDifferent over rows,
// columns and boxes, fixed cells with arithm.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;

public class Sudoku {
    public static void main(String[] args) {
        // 0 is an empty cell
        int[][] given = {
            {1, 0, 0, 4},
            {0, 4, 1, 0},
            {0, 1, 0, 3},
            {4, 0, 2, 0}};
        Model m = new Model("sudoku");
        IntVar[][] cell = m.intVarMatrix("cell", 4, 4, 1, 4);

        // the given digits stay where they are
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                if (given[r][c] != 0) m.arithm(cell[r][c], "=", given[r][c]).post();

        // each row holds 1 to 4 once each
        for (int r = 0; r < 4; r++) m.allDifferent(cell[r], "AC").post();

        // each column holds 1 to 4 once each
        for (int c = 0; c < 4; c++) {
            IntVar[] column = new IntVar[4];
            for (int r = 0; r < 4; r++) column[r] = cell[r][c];
            m.allDifferent(column, "AC").post();
        }

        // each 2x2 box holds 1 to 4 once each
        for (int br = 0; br < 4; br += 2)
            for (int bc = 0; bc < 4; bc += 2) {
                IntVar[] box = new IntVar[4];
                for (int i = 0; i < 4; i++) box[i] = cell[br + i / 2][bc + i % 2];
                m.allDifferent(box, "AC").post();
            }

        if (m.getSolver().solve()) {
            for (int r = 0; r < 4; r++) {
                StringBuilder row = new StringBuilder("Row " + r + ":");
                for (int c = 0; c < 4; c++) row.append(' ').append(cell[r][c].getValue());
                System.out.println(row);
            }
        } else {
            System.out.println("no solution");
        }
    }
}
