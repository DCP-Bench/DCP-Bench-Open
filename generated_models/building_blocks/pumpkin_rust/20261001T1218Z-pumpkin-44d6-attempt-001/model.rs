// Building blocks: distribute the letters of the alphabet over alphabet blocks,
// each block carrying the same number of letters, so that every word on the list
// can be spelled with its letters on different blocks.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let num_blocks = inst.size("num_blocks");
    let num_sides = inst.int("num_sides"); // letters on each block
    let num_letters = inst.size("num_letters");
    let words_str = inst.strings("words_str"); // the words to spell
    let alphabet = inst
        .get("alphabet")
        .as_str()
        .expect("instance field alphabet: expected a string")
        .to_string();

    // A letter is identified by its position in the alphabet string.
    let words: Vec<Vec<usize>> = words_str
        .iter()
        .map(|word| {
            word.chars()
                .map(|c| {
                    alphabet
                        .chars()
                        .position(|a| a == c)
                        .unwrap_or_else(|| panic!("letter {c} is not in the alphabet"))
                })
                .collect()
        })
        .collect();

    // dice[l] is the block (0 to num_blocks - 1) that carries letter l.
    let dice: Vec<Var> = (0..num_letters)
        .map(|_| solver.new_bounded_integer(0, num_blocks as i32 - 1))
        .collect();

    // The letters of a word must be on different blocks.
    let spelling = solver.new_constraint_tag();
    for word in &words {
        let blocks_of_word: Vec<Var> = word.iter().map(|&l| dice[l]).collect();
        solver
            .add_constraint(pumpkin_solver::all_different(blocks_of_word, spelling))
            .post();
    }

    // Each block carries exactly num_sides letters. Pumpkin has no counting
    // constraint, so a literal per letter says "this letter is on block b" and
    // the literals of a block are summed.
    let on_block = solver.new_constraint_tag();
    let block_load = solver.new_constraint_tag();
    let sides = solver.new_bounded_integer(num_sides, num_sides);
    for b in 0..num_blocks {
        let mut here: Vec<Lit> = Vec::new();
        for l in 0..num_letters {
            let flag = solver.new_literal();
            solver
                .add_constraint(pumpkin_solver::equals(
                    vec![dice[l].scaled(1)], b as i32, on_block))
                .reify(flag);
            here.push(flag);
        }
        solver
            .add_constraint(pumpkin_solver::boolean_equals(
                vec![1; num_letters], here, sides, block_load))
            .post();
    }

    let mut m = Model::new();
    m.put("dice", dice);
    m
}
