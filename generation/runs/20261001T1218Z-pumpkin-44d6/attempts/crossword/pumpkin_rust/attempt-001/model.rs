// Crossword: choose a different word from the list of 15 for each of the 8 slots
// of the grid so that the words agree on every crossing square. E[s] is the word
// placed in slot s.
//
// The instance has no fields: the word list (ordered longest first, then
// alphabetically) and the twelve crossings of the grid are the puzzle's own
// data, mirrored from the reference.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    // Words, padded with '.' to five letters (the reference pads with 0).
    let words: [&[u8; 5]; 15] = [
        b"HOSES", b"LASER", b"SAILS", b"SHEET", b"STEER", b"HEEL.", b"HIKE.", b"KEEL.",
        b"KNOT.", b"LINE.", b"AFT..", b"ALE..", b"EEL..", b"LEE..", b"TIE..",
    ];
    let num_words = words.len();
    let slots = 8;

    // [slot1, letter1, slot2, letter2]: letter letter1 of the word in slot1 lies
    // on the same square as letter letter2 of the word in slot2.
    let overlapping: [[usize; 4]; 12] = [
        [0, 2, 1, 0], // s
        [0, 4, 2, 0], // s
        [3, 1, 1, 2], // i
        [3, 2, 4, 0], // k
        [3, 3, 2, 2], // e
        [6, 0, 1, 3], // l
        [6, 1, 4, 1], // e
        [6, 2, 2, 3], // e
        [7, 0, 5, 1], // l
        [7, 2, 1, 4], // s
        [7, 3, 4, 2], // e
        [7, 4, 2, 4], // r
    ];

    let e: Vec<Var> = (0..slots).map(|_| solver.new_bounded_integer(0, num_words as i32 - 1)).collect();

    // Each slot gets a different word.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(e.clone(), tag)).post();

    // Crossing words share the letter on their common square. For each crossing
    // the pairs of words whose letters agree there are listed as a table; this is
    // the reference's A[E[s1], l1] == A[E[s2], l2] with A fixed to the word list.
    let crossings = solver.new_constraint_tag();
    for &[s1, l1, s2, l2] in overlapping.iter() {
        let agree: Vec<Vec<i32>> = (0..num_words)
            .flat_map(|w1| (0..num_words).map(move |w2| (w1, w2)))
            .filter(|&(w1, w2)| words[w1][l1] == words[w2][l2])
            .map(|(w1, w2)| vec![w1 as i32, w2 as i32])
            .collect();
        solver.add_constraint(pumpkin_solver::table(vec![e[s1], e[s2]], agree, crossings)).post();
    }

    let mut m = Model::new();
    m.put("E", e);
    m
}
