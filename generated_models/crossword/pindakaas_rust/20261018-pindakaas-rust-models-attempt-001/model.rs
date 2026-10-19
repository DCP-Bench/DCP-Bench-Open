// Crossword: complete the 6 x 5 grid of the description with 8 words chosen
// from the list of 15 words. Output E[k] is the index (0-based, in the sorted
// word order) of the word for entry k+1 (the entries numbered 1 to 8 in the grid).

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // The words, sorted by length (longest first), then alphabetically.
    let mut words: Vec<&str> = vec![
        "AFT", "ALE", "EEL", "HEEL", "HIKE", "HOSES", "KEEL", "KNOT", "LASER", "LEE", "LINE",
        "SAILS", "SHEET", "STEER", "TIE",
    ];
    words.sort_by(|a, b| b.len().cmp(&a.len()).then(a.cmp(b)));

    // The entries, numbered as in the grid, each a list of its cells (row, column), 1-based.
    let entries: Vec<Vec<(usize, usize)>> = vec![
        // 1 across
        vec![(1, 1), (1, 2), (1, 3), (1, 4), (1, 5)],
        // 2 down
        vec![(1, 3), (2, 3), (3, 3), (4, 3), (5, 3)],
        // 3 down
        vec![(1, 5), (2, 5), (3, 5), (4, 5), (5, 5)],
        // 4 across
        vec![(3, 2), (3, 3), (3, 4), (3, 5)],
        // 5 down
        vec![(3, 4), (4, 4), (5, 4), (6, 4)],
        // 6 down
        vec![(4, 1), (5, 1), (6, 1)],
        // 7 across
        vec![(4, 3), (4, 4), (4, 5)],
        // 8 across
        vec![(5, 1), (5, 2), (5, 3), (5, 4), (5, 5)],
    ];

    // One letter variable (0..25, A = 0) per open cell; crossing entries share it.
    let mut letters: Vec<Vec<Option<IntVar>>> = vec![vec![None; 7]; 7];
    for cells in &entries {
        for &(r, c) in cells {
            if letters[r][c].is_none() {
                letters[r][c] = Some(IntVar::new(0..=25));
            }
        }
    }

    // One word index per entry.
    let last = words.len() as i64 - 1;
    let e: Vec<IntVar> = (0..entries.len()).map(|_| IntVar::new(0..=last)).collect();

    // The letters of the chosen word are the letters of its cells.
    for (k, cells) in entries.iter().enumerate() {
        let mut xs = vec![e[k].clone()];
        for &(r, c) in cells {
            xs.push(letters[r][c].clone().expect("cell has a letter variable"));
        }
        let mut rows: Vec<Vec<i64>> = Vec::new();
        for (w, word) in words.iter().enumerate() {
            if word.len() == cells.len() {
                let mut row = vec![w as i64];
                row.extend(word.bytes().map(|b| (b - b'A') as i64));
                rows.push(row);
            }
        }
        table(s, &xs, &rows)?;
    }

    // The 8 selected words are distinct.
    all_different(s, &e)?;

    let mut out = Out::new();
    out.put("E", &e);
    Ok(out)
}
