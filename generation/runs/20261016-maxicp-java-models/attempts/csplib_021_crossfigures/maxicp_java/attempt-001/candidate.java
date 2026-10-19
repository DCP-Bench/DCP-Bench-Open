// Crossfigure: a 9x9 grid. X cells are black; every other cell holds one digit.
// Each run of two or more white cells across or down is an entry: its digits read as a
// number with no leading zero. The numbers in the grid are the clue numbers.
// Every clue below relates the entries named in the problem's clue list.
import java.util.ArrayList;
import java.util.List;

import static org.maxicp.cp.CPFactory.*;

import org.maxicp.cp.engine.core.CPIntVar;

import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {

    static final String[] GRID = {
        "1 2 _ 3 X 4 _ 5 6",
        "7 _ X 8 _ _ X 9 _",
        "_ X 10 _ X 11 12 X _",
        "13 14 _ _ X 15 _ 16 _",
        "X _ X X X X X _ X",
        "17 _ 18 19 X 20 21 _ 22",
        "_ X 23 _ X 24 _ X _",
        "25 26 X 27 _ _ X 28 _",
        "29 _ _ _ X 30 _ _ _",
    };

    static final int R = 9;
    static final int C = 9;

    static boolean black(String[][] lab, int r, int c) {
        return lab[r][c].equals("X");
    }

    public static void build(Instance inst, Model m, Outputs out) {
        String[][] lab = new String[R][C];
        for (int r = 0; r < R; r++) {
            String[] tokens = GRID[r].trim().split("\\s+");
            for (int c = 0; c < C; c++) lab[r][c] = tokens[c];
        }

        // every white cell holds a digit
        CPIntVar[][] d = new CPIntVar[R][C];
        for (int r = 0; r < R; r++)
            for (int c = 0; c < C; c++)
                if (!black(lab, r, c)) d[r][c] = m.intVar(0, 9);

        // the entries: a run of white cells across or down, read as a number
        CPIntVar[] across = new CPIntVar[31];
        CPIntVar[] down = new CPIntVar[31];
        for (int r = 0; r < R; r++) {
            for (int c = 0; c < C; c++) {
                if (black(lab, r, c)) continue;
                if (c == 0 || black(lab, r, c - 1)) {
                    List<CPIntVar> cells = new ArrayList<>();
                    for (int cc = c; cc < C && !black(lab, r, cc); cc++) cells.add(d[r][cc]);
                    if (cells.size() >= 2) across[clueNumber(lab[r][c])] = entry(m, cells);
                }
                if (r == 0 || black(lab, r - 1, c)) {
                    List<CPIntVar> cells = new ArrayList<>();
                    for (int rr = r; rr < R && !black(lab, rr, c); rr++) cells.add(d[rr][c]);
                    if (cells.size() >= 2) down[clueNumber(lab[r][c])] = entry(m, cells);
                }
            }
        }

        // 1 across: 27 across times two
        timesK(m, A(across, 1), A(across, 27), 2);
        // 4 across: 4 down plus seventy-one
        plusK(m, A(across, 4), A(down, 4), 71);
        // 7 across: 18 down plus four
        plusK(m, A(across, 7), A(down, 18), 4);
        // 8 across: 6 down divided by sixteen
        timesK(m, A(down, 6), A(across, 8), 16);
        // 9 across: 2 down minus eighteen
        plusK(m, A(down, 2), A(across, 9), 18);
        // 10 across: dozen in six gross (6 gross = 864 = 72 dozen)
        fix(m, A(across, 10), 72);
        // 11 across: 5 down minus seventy
        plusK(m, A(down, 5), A(across, 11), 70);
        // 13 across: 26 down times 23 across
        prod(m, A(across, 13), A(down, 26), A(across, 23));
        // 15 across: 6 down minus 350
        plusK(m, A(down, 6), A(across, 15), 350);
        // 17 across: 25 across times 23 across
        prod(m, A(across, 17), A(across, 25), A(across, 23));
        // 20 across: a square number
        square(m, A(across, 20));
        // 23 across: a prime number
        prime(m, A(across, 23));
        // 24 across: a square number
        square(m, A(across, 24));
        // 25 across: 20 across divided by seventeen
        timesK(m, A(across, 20), A(across, 25), 17);
        // 27 across: 6 down divided by four
        timesK(m, A(down, 6), A(across, 27), 4);
        // 28 across: four dozen
        fix(m, A(across, 28), 48);
        // 29 across: seven gross
        fix(m, A(across, 29), 1008);
        // 30 across: 22 down plus 450
        plusK(m, A(across, 30), A(down, 22), 450);

        // 1 down: 1 across plus twenty-seven
        plusK(m, A(down, 1), A(across, 1), 27);
        // 2 down: five dozen
        fix(m, A(down, 2), 60);
        // 3 down: 30 across plus 888
        plusK(m, A(down, 3), A(across, 30), 888);
        // 4 down: two times 17 across
        timesK(m, A(down, 4), A(across, 17), 2);
        // 5 down: 29 across divided by twelve
        timesK(m, A(across, 29), A(down, 5), 12);
        // 6 down: 28 across times 23 across
        prod(m, A(down, 6), A(across, 28), A(across, 23));
        // 10 down: 10 across plus four
        plusK(m, A(down, 10), A(across, 10), 4);
        // 12 down: three times 24 across
        timesK(m, A(down, 12), A(across, 24), 3);
        // 14 down: 13 across divided by sixteen
        timesK(m, A(across, 13), A(down, 14), 16);
        // 16 down: 28 down times fifteen
        timesK(m, A(down, 16), A(down, 28), 15);
        // 17 down: 13 across minus 399
        plusK(m, A(across, 13), A(down, 17), 399);
        // 18 down: 29 across divided by eighteen
        timesK(m, A(across, 29), A(down, 18), 18);
        // 19 down: 22 down minus ninety-four
        plusK(m, A(down, 22), A(down, 19), 94);
        // 20 down: 20 across minus nine
        plusK(m, A(across, 20), A(down, 20), 9);
        // 21 down: 25 across minus fifty-two
        plusK(m, A(across, 25), A(down, 21), 52);
        // 22 down: 20 down times six
        timesK(m, A(down, 22), A(down, 20), 6);
        // 26 down: five times 24 across
        timesK(m, A(down, 26), A(across, 24), 5);
        // 28 down: 21 down plus twenty-seven
        plusK(m, A(down, 28), A(down, 21), 27);

        // the grid: black cells read as 0, white cells as their digit
        Object[][] grid = new Object[R][C];
        for (int r = 0; r < R; r++)
            for (int c = 0; c < C; c++)
                grid[r][c] = black(lab, r, c) ? (Object) Integer.valueOf(0) : d[r][c];
        out.put("M", grid);
    }

    static CPIntVar A(CPIntVar[] entries, int n) {
        if (entries[n] == null) throw new IllegalStateException("no entry for clue " + n);
        return entries[n];
    }

    static int clueNumber(String label) {
        if (label.equals("_")) throw new IllegalStateException("an entry starts at an unnumbered cell");
        return Integer.parseInt(label);
    }

    static int pow10(int e) {
        int p = 1;
        for (int i = 0; i < e; i++) p *= 10;
        return p;
    }

    // the number read from its digits, most significant first, with no leading zero
    static CPIntVar entry(Model m, List<CPIntVar> cells) {
        int n = cells.size();
        CPIntVar value = m.intVar(pow10(n - 1), pow10(n) - 1);
        CPIntVar[] terms = new CPIntVar[n];
        for (int i = 0; i < n; i++) terms[i] = mul(cells.get(i), pow10(n - 1 - i));
        m.cp().post(eq(sum(terms), value));
        return value;
    }

    // x = k * y
    static void timesK(Model m, CPIntVar x, CPIntVar y, int k) {
        m.cp().post(eq(mul(y, k), x));
    }

    // x = y + k
    static void plusK(Model m, CPIntVar x, CPIntVar y, int k) {
        m.cp().post(eq(plus(y, k), x));
    }

    // x = y * z
    static void prod(Model m, CPIntVar x, CPIntVar y, CPIntVar z) {
        m.cp().post(eq(mul(y, z), x));
    }

    // x = k
    static void fix(Model m, CPIntVar x, int k) {
        m.cp().post(eq(x, k));
    }

    // x is one of the squares
    static void square(Model m, CPIntVar x) {
        int top = 0;
        while ((top + 1) * (top + 1) <= 9999) top++;
        int[] squares = new int[top + 1];
        for (int k = 0; k <= top; k++) squares[k] = k * k;
        CPIntVar idx = m.intVar(0, top);
        m.cp().post(eq(element(squares, idx), x));
    }

    // x is one of the primes below 100
    static void prime(Model m, CPIntVar x) {
        int[] primes = {11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97};
        CPIntVar idx = m.intVar(0, primes.length - 1);
        m.cp().post(eq(element(primes, idx), x));
    }
}
