import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;

// Complete the 6 by 5 crossword from 8 of the 15 given words.
// Words are numbered from 0 in the order: longest first, then alphabetically.
public class Submission {
    public static void build(Instance inst, Model m, Outputs out) {
        // the list of words given in the description
        String[] given = {"AFT", "ALE", "EEL", "HEEL", "HIKE", "HOSES", "KEEL", "KNOT",
                          "LASER", "LEE", "LINE", "SAILS", "SHEET", "STEER", "TIE"};
        String[] words = given.clone();
        Arrays.sort(words, Comparator.comparingInt((String w) -> -w.length())
                                     .thenComparing(Comparator.naturalOrder()));
        int nWords = words.length;

        // the crossword: the 8 numbered words, each as the list of its cells (row, column), 0-based;
        // the cells marked # are blocked.
        int[][][] slots = {
            {{0,0},{0,1},{0,2},{0,3},{0,4}},   // 1 across
            {{0,2},{1,2},{2,2},{3,2},{4,2}},   // 2 down
            {{0,4},{1,4},{2,4},{3,4},{4,4}},   // 3 down
            {{2,1},{2,2},{2,3},{2,4}},         // 4 across
            {{2,3},{3,3},{4,3},{5,3}},         // 5 down
            {{3,0},{4,0},{5,0}},               // 6 down
            {{3,2},{3,3},{3,4}},               // 7 across
            {{4,0},{4,1},{4,2},{4,3},{4,4}},   // 8 across
        };

        // one letter variable (A to Z, as 0 to 25) for every open cell
        CPIntVar[][] letter = new CPIntVar[6][5];
        for (int[][] slot : slots)
            for (int[] cell : slot)
                if (letter[cell[0]][cell[1]] == null) letter[cell[0]][cell[1]] = m.intVar(0, 25);

        // the word placed in each numbered slot
        CPIntVar[] place = m.intVarArray(slots.length, 0, nWords - 1);

        // each word fills its place: its letters match the squares it covers,
        // and only words of the place's length are allowed
        for (int s = 0; s < slots.length; s++) {
            int len = slots[s].length;
            List<int[]> rows = new ArrayList<>();
            for (int j = 0; j < nWords; j++) {
                if (words[j].length() != len) continue;
                int[] row = new int[len + 1];
                row[0] = j;
                for (int i = 0; i < len; i++) row[i + 1] = words[j].charAt(i) - 'A';
                rows.add(row);
            }
            CPIntVar[] xs = new CPIntVar[len + 1];
            xs[0] = place[s];
            for (int i = 0; i < len; i++) xs[i + 1] = letter[slots[s][i][0]][slots[s][i][1]];
            m.cp().post(table(xs, rows.toArray(new int[0][])));
        }

        // select 8 different words from the list of 15, one for each number
        m.cp().post(allDifferent(place));

        // print the word for each number 1 to 8, in order
        out.put("E", place);
    }
}
