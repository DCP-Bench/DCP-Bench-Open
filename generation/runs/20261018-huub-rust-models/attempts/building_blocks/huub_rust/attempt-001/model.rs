// Building blocks: place each letter of the alphabet on one of the num_blocks
// blocks, so that every word of the list can be spelled with its letters on
// distinct blocks.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("num_letters");
    let nb = inst.size("num_blocks");
    let ns = inst.size("num_sides");
    let alphabet: Vec<char> = inst.get("alphabet").as_str().unwrap().chars().collect();
    let words = inst.strings("words_str");

    // dice[i] is the block that carries the i-th letter of the alphabet.
    let dice = m.new_int_decisions(n, 0..=(nb as i64 - 1));

    // Each block has one letter on each of its num_sides sides.
    for b in 0..nb {
        m.linear(count_eq(&dice, b as i64)).eq(ns as i64).post()?;
    }

    // Each word is spelled by taking its letters from distinct blocks.
    for word in &words {
        let idx: Vec<usize> = word
            .chars()
            .map(|c| alphabet.iter().position(|&a| a == c).expect("letter not in alphabet"))
            .collect();
        for p in 0..idx.len() {
            for q in (p + 1)..idx.len() {
                m.linear(dice[idx[p]] - dice[idx[q]]).ne(0).post()?;
            }
        }
    }

    let mut out = Out::new();
    out.put("dice", dice);
    Ok(out)
}
