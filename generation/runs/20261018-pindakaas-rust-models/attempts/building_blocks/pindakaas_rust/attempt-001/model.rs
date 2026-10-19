// Building blocks: alphabet blocks carry one letter on each side; the blocks
// contain every letter except Q and Z. Decide at which block each letter is
// placed (dice), so that every word of the list can be spelled.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let nb = inst.int("num_blocks");
    let ns = inst.int("num_sides");
    let num_letters = inst.size("num_letters");
    let alphabet: Vec<char> = inst.get("alphabet").as_str().expect("alphabet string").chars().collect();
    let words = inst.strings("words_str");

    // Each letter of the alphabet is placed on one block, numbered 0 to num_blocks-1.
    let dice: Vec<IntVar> = (0..num_letters).map(|_| IntVar::new(0..=nb - 1)).collect();

    // Each block has num_sides sides, each showing a single letter, so a block holds at most num_sides letters.
    for b in 0..nb {
        let c = IntVar::new(0..=ns);
        count_eq(s, &dice, b, &c)?;
    }

    // Arranging the blocks spells a word: the letters of a word are on distinct blocks.
    for w in &words {
        let vars: Vec<IntVar> = w
            .chars()
            .map(|ch| {
                let i = alphabet.iter().position(|&a| a == ch).expect("word letter in alphabet");
                dice[i].clone()
            })
            .collect();
        all_different(s, &vars)?;
    }

    let mut out = Out::new();
    out.put("dice", &dice);
    Ok(out)
}
