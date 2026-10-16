import com.google.gson.JsonArray;
import com.google.gson.JsonParser;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import org.maxicp.search.DFSearch;
import org.maxicp.search.SearchStatistics;
import org.maxicp.util.exception.InconsistencyException;
import static org.maxicp.cp.CPFactory.*;
import static org.maxicp.search.Searches.*;

// Assign a digit to each letter so that the addends add up to the sum.
public class Cryptarithm {
    public static void main(String[] args) throws Exception {
        var data = JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject();
        JsonArray addendsJson = data.getAsJsonArray("addends");
        String sumWord = data.get("sum").getAsString();
        List<String> addends = new ArrayList<>();
        for (int i = 0; i < addendsJson.size(); i++) addends.add(addendsJson.get(i).getAsString());

        CPSolver cp = CPFactory.makeSolver();
        // one digit variable per letter, in order of first appearance
        Map<Character, CPIntVar> digit = new LinkedHashMap<>();
        for (String word : addends) for (char c : word.toCharArray()) digit.computeIfAbsent(c, k -> makeIntVar(cp, 0, 9));
        for (char c : sumWord.toCharArray()) digit.computeIfAbsent(c, k -> makeIntVar(cp, 0, 9));
        CPIntVar[] letters = digit.values().toArray(new CPIntVar[0]);

        // different letters get different digits
        cp.post(allDifferent(letters));

        // no word of more than one letter starts with 0
        for (String word : addends) if (word.length() > 1) cp.post(neq(digit.get(word.charAt(0)), 0));
        if (sumWord.length() > 1) cp.post(neq(digit.get(sumWord.charAt(0)), 0));

        // the addends add up to the sum: a letter in position p of a word counts 10^p
        List<CPIntVar> left = new ArrayList<>();
        for (String word : addends) {
            for (int k = 0; k < word.length(); k++) {
                int power = (int) Math.pow(10, word.length() - 1 - k);
                left.add(mul(digit.get(word.charAt(k)), power));
            }
        }
        List<CPIntVar> right = new ArrayList<>();
        for (int k = 0; k < sumWord.length(); k++) {
            int power = (int) Math.pow(10, sumWord.length() - 1 - k);
            right.add(mul(digit.get(sumWord.charAt(k)), power));
        }
        try {
            cp.post(eq(sum(left.toArray(new CPIntVar[0])), sum(right.toArray(new CPIntVar[0]))));
        } catch (InconsistencyException refuted) {
            System.out.println("{\"status\": \"unsatisfiable\"}");
            return;
        }

        // one solution is enough
        int[] found = new int[letters.length];
        DFSearch search = CPFactory.makeDfs(cp, firstFailBinary(letters));
        search.onSolution(() -> {
            for (int i = 0; i < letters.length; i++) found[i] = letters[i].min();
        });
        SearchStatistics stats = search.solve(s -> s.numberOfSolutions() >= 1);
        if (stats.numberOfSolutions() == 0) {
            System.out.println("{\"status\": \"unsatisfiable\"}");
            return;
        }
        StringBuilder out = new StringBuilder("{\"digits\": {");
        int i = 0;
        for (Map.Entry<Character, CPIntVar> entry : digit.entrySet()) {
            if (i > 0) out.append(", ");
            out.append('"').append(entry.getKey()).append("\": ").append(found[i]);
            i++;
        }
        out.append("}}");
        System.out.println(out);
    }
}
