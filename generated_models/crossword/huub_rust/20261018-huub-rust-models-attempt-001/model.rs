// Crossword: complete the 6x5 puzzle by selecting 8 of the 15 given words.
// The 8 numbered locations are slots: 1 across (5 letters), 2 down (5), 3 down (5),
// 4 across (4), 5 down (4), 6 down (3), 7 across (3), 8 across (5).
// The word list is sorted longest first, then alphabetically; E[k] is the index of the
// word that starts at location k+1.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // The 15 words, in the order the description sorts them.
    let words: Vec<&str> = vec![
        "HOSES", "LASER", "SAILS", "SHEET", "STEER", // 5 letters
        "HEEL", "HIKE", "KEEL", "KNOT", "LINE", // 4 letters
        "AFT", "ALE", "EEL", "LEE", "TIE", // 3 letters
    ];
    // Length of the word that each numbered location starts.
    let slot_len: [usize; 8] = [5, 5, 5, 4, 4, 3, 3, 5];

    // Select the words: E[k] is the index of the word for location k+1.
    let e = m.new_int_decisions(8, 0..=14);
    // Select 8 distinct words from the list.
    m.unique(e.clone()).post()?;

    // Each location holds a word of the right length from the list. The letter
    // variables are the letters of that word, position by position.
    let mut letters: Vec<Vec<View<i64>>> = Vec::new();
    for k in 0..8 {
        let ls = m.new_int_decisions(slot_len[k], 0..=25);
        let mut vars = vec![e[k]];
        vars.extend(ls.iter().cloned());
        let rows: Vec<Vec<i64>> = words
            .iter()
            .enumerate()
            .filter(|(_, w)| w.len() == slot_len[k])
            .map(|(i, w)| {
                let mut row = vec![i as i64];
                row.extend(w.bytes().map(|b| (b - b'A') as i64));
                row
            })
            .collect();
        m.table(vars).values(rows).post()?;
        letters.push(ls);
    }

    // The crossing cells hold the same letter in both words.
    // Each entry is (location a, position i in a, location b, position j in b).
    let crossings: [(usize, usize, usize, usize); 12] = [
        (0, 2, 1, 0), // 1 across and 2 down
        (0, 4, 2, 0), // 1 across and 3 down
        (3, 1, 1, 2), // 4 across and 2 down
        (3, 2, 4, 0), // 4 across and 5 down
        (3, 3, 2, 2), // 4 across and 3 down
        (6, 0, 1, 3), // 7 across and 2 down
        (6, 1, 4, 1), // 7 across and 5 down
        (6, 2, 2, 3), // 7 across and 3 down
        (7, 0, 5, 1), // 8 across and 6 down
        (7, 2, 1, 4), // 8 across and 2 down
        (7, 3, 4, 2), // 8 across and 5 down
        (7, 4, 2, 4), // 8 across and 3 down
    ];
    for (a, i, b, j) in crossings {
        eq2(m, letters[a][i] - letters[b][j], 0)?;
    }

    let mut out = Out::new();
    out.put("E", e);
    Ok(out)
}
