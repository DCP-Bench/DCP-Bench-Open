import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;
import java.util.ArrayList;
import java.util.List;

// Flow Free: connect the two cells of every colour with a pipe. Each colour is one
// pipe between its two given endpoints, pipes do not overlap or cross, and the pipes
// cover the whole board. Output B gives the colour of every cell.
public class Submission {

    static int cellIndex(int r, int c, int cols) {
        return r * cols + c;
    }

    // the cells next to cell (r, c), as indices
    static List<Integer> neighbours(int r, int c, int rows, int cols) {
        List<Integer> out = new ArrayList<>();
        int[][] d = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}};
        for (int[] dd : d) {
            int nr = r + dd[0], nc = c + dd[1];
            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols) out.add(cellIndex(nr, nc, cols));
        }
        return out;
    }

    public static void build(Instance inst, Model m, Outputs out) {
        int[][] board = inst.getIntMatrix("board");
        int rows = board.length;
        int cols = board[0].length;
        int cells = rows * cols;

        // the colours are 1..K, where K is the largest given colour
        int colours = 0;
        for (int[] row : board) for (int v : row) colours = Math.max(colours, v);

        // the given cells are the endpoints; each colour has exactly two
        List<List<Integer>> endpoints = new ArrayList<>();
        for (int k = 0; k <= colours; k++) endpoints.add(new ArrayList<>());
        for (int r = 0; r < rows; r++)
            for (int c = 0; c < cols; c++)
                if (board[r][c] != 0) endpoints.get(board[r][c]).add(cellIndex(r, c, cols));
        for (int k = 1; k <= colours; k++)
            if (endpoints.get(k).size() != 2)
                throw new IllegalArgumentException("colour " + k + " needs exactly two endpoints");

        // the colour of every cell, 1..K; the given cells keep their colour
        CPIntVar[] B = new CPIntVar[cells];
        for (int r = 0; r < rows; r++)
            for (int c = 0; c < cols; c++) {
                int v = board[r][c];
                int p = cellIndex(r, c, cols);
                B[p] = (v == 0) ? m.intVar(1, colours) : m.intVar(v, v);
            }

        // x[k][p] = 1 if cell p has colour k
        CPIntVar[][] x = new CPIntVar[colours + 1][cells];
        for (int k = 1; k <= colours; k++) {
            for (int p = 0; p < cells; p++) {
                x[k][p] = m.boolVar();
                // the colour of a cell is k exactly when x is 1
                int[][] rows2 = new int[colours][2];
                for (int v = 1; v <= colours; v++) rows2[v - 1] = new int[]{v, v == k ? 1 : 0};
                m.cp().post(table(new CPIntVar[]{B[p], x[k][p]}, rows2));
            }
        }

        // pos[k][p] = position of cell p along the pipe of colour k, counted from its
        // first endpoint (1); 0 when the cell has no colour k
        CPIntVar[][] pos = new CPIntVar[colours + 1][cells];
        for (int k = 1; k <= colours; k++) {
            int start = endpoints.get(k).get(0);
            for (int p = 0; p < cells; p++) {
                pos[k][p] = m.intVar(0, cells);
                if (p == start) {
                    // the first endpoint starts the pipe
                    m.cp().post(eq(pos[k][p], 1));
                } else {
                    // a cell with colour k has a position of at least 2 and links to
                    // a predecessor; a cell without colour k has position 0
                    int[][] rows2 = new int[1 + (cells - 1)][2];
                    rows2[0] = new int[]{0, 0};
                    for (int v = 2; v <= cells; v++) rows2[v - 1] = new int[]{1, v};
                    m.cp().post(table(new CPIntVar[]{x[k][p], pos[k][p]}, rows2));
                }
            }
        }

        // each pipe is connected: every cell of colour k except the first endpoint has
        // a neighbour of colour k one step earlier along the pipe
        for (int k = 1; k <= colours; k++) {
            int start = endpoints.get(k).get(0);
            for (int r = 0; r < rows; r++)
                for (int c = 0; c < cols; c++) {
                    int p = cellIndex(r, c, cols);
                    if (p == start) continue;
                    List<Integer> nb = neighbours(r, c, rows, cols);
                    CPIntVar[] link = new CPIntVar[nb.size()];
                    for (int i = 0; i < nb.size(); i++) {
                        int q = nb.get(i);
                        CPIntVar pr = m.boolVar();
                        link[i] = pr;
                        // link is 1 only when the neighbour is one step earlier on the pipe
                        int[][] rows2 = new int[(cells + 1) * (cells + 1) + (cells - 1)][3];
                        int idx = 0;
                        for (int a = 0; a <= cells; a++)
                            for (int b = 0; b <= cells; b++) rows2[idx++] = new int[]{0, a, b};
                        for (int v = 2; v <= cells; v++) rows2[idx++] = new int[]{1, v, v - 1};
                        m.cp().post(table(new CPIntVar[]{pr, pos[k][p], pos[k][q]}, rows2));
                    }
                    // a cell of colour k has a predecessor
                    m.cp().post(ge(sum(link), x[k][p]));
                }
        }

        // each colour is one pipe: an endpoint has one neighbour of its colour, and
        // every other cell of that colour has two
        for (int k = 1; k <= colours; k++) {
            for (int r = 0; r < rows; r++)
                for (int c = 0; c < cols; c++) {
                    int p = cellIndex(r, c, cols);
                    List<Integer> nb = neighbours(r, c, rows, cols);
                    CPIntVar[] same = new CPIntVar[nb.size()];
                    for (int i = 0; i < nb.size(); i++) same[i] = x[k][nb.get(i)];
                    if (board[r][c] == k) {
                        // an endpoint has exactly one neighbour of its colour
                        m.cp().post(eq(sum(same), 1));
                    } else {
                        // a cell of colour k has exactly two neighbours of its colour
                        CPIntVar[] withSelf = new CPIntVar[same.length + 1];
                        System.arraycopy(same, 0, withSelf, 0, same.length);
                        withSelf[same.length] = mul(x[k][p], 2);
                        m.cp().post(le(sum(withSelf), 4));
                        m.cp().post(ge(sum(same), mul(x[k][p], 2)));
                    }
                }
        }

        out.put("B", reshape(B, rows, cols));
    }

    static CPIntVar[][] reshape(CPIntVar[] flat, int rows, int cols) {
        CPIntVar[][] grid = new CPIntVar[rows][cols];
        for (int r = 0; r < rows; r++)
            for (int c = 0; c < cols; c++) grid[r][c] = flat[cellIndex(r, c, cols)];
        return grid;
    }
}
