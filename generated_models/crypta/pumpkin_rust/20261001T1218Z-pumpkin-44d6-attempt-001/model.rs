// Cryptarithm: BAIJJAJIIAHFCFEBBJEA + DHFGABCDIDBIFFAGFEJE = GJEGACDDHFAFJBFIHEEF,
// where the letters A..J are distinct digits and no number starts with zero.
//
// The instance has no fields: the three twenty-digit words are the puzzle's own
// data. As in the reference, the addition is split into three column blocks of
// 7, 7 and 6 digits joined by carries Sr1 and Sr2, so each linear equation stays
// within 32-bit coefficients.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"];
    let ld: Vec<Var> = (0..10).map(|_| solver.new_bounded_integer(0, 9)).collect();
    let letter = |c: u8| ld[(c - b'A') as usize];

    // The carries out of the lowest and the middle block.
    let sr1 = solver.new_bounded_integer(0, 1);
    let sr2 = solver.new_bounded_integer(0, 1);

    // All letters are distinct digits.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(ld.clone(), tag)).post();

    // The leading letters B, D and G are not zero.
    let leading = solver.new_constraint_tag();
    for c in [b'B', b'D', b'G'] {
        solver.add_constraint(pumpkin_solver::less_than_or_equals(vec![letter(c).scaled(-1)], -1, leading)).post();
    }

    // Each block: digits of the first and second addend (written most significant
    // first) plus the carry in equal the digits of the sum plus 10^7 times the
    // carry out. A block's words are read off the full words above.
    let first = b"BAIJJAJIIAHFCFEBBJEA";
    let second = b"DHFGABCDIDBIFFAGFEJE";
    let sum = b"GJEGACDDHFAFJBFIHEEF";
    // (start, end) column ranges, most significant first, carry in, carry out.
    let blocks = [(13usize, 20usize, None, Some(sr1)), (6, 13, Some(sr1), Some(sr2)), (0, 6, Some(sr2), None)];
    let columns = solver.new_constraint_tag();
    for (start, end, carry_in, carry_out) in blocks {
        let mut terms: Vec<Term> = Vec::new();
        for pos in start..end {
            let weight = 10i32.pow((end - 1 - pos) as u32);
            terms.push(letter(first[pos]).scaled(weight));
            terms.push(letter(second[pos]).scaled(weight));
            terms.push(letter(sum[pos]).scaled(-weight));
        }
        if let Some(c) = carry_in {
            terms.push(c.scaled(1));
        }
        if let Some(c) = carry_out {
            terms.push(c.scaled(-10i32.pow((end - start) as u32)));
        }
        solver.add_constraint(pumpkin_solver::equals(terms, 0, columns)).post();
    }

    let mut m = Model::new();
    for (i, name) in names.iter().enumerate() {
        m.put(name, ld[i]);
    }
    m
}
