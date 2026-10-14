// General store sign: an alphametic in which sixteen words (CHESS, CASH, ...,
// SHEEP) add up to ALL WOOL. Each letter is a different digit.
//
// The instance has no fields: the words of the sign are the puzzle's own data,
// mirrored from the reference (which allows leading zeros).
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let letters = "CHESABOWPL";
    let addends = [
        "CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS", "HOPS", "ALES",
        "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP",
    ];
    let total = "ALLWOOL";

    let x: Vec<Var> = letters.chars().map(|_| solver.new_bounded_integer(0, 9)).collect();

    // Different letters are different digits.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(x.clone(), tag)).post();

    // The words above the line add up to ALL WOOL. Each letter's coefficient is
    // the sum of its place values over the addends, minus its place values in the
    // total; the largest coefficient stays below 10^7, well within 32 bits.
    let mut coefficient = vec![0i32; letters.len()];
    let mut add_word = |word: &str, sign: i32| {
        for (pos, ch) in word.chars().rev().enumerate() {
            let k = letters.find(ch).unwrap();
            coefficient[k] += sign * 10i32.pow(pos as u32);
        }
    };
    for word in addends.iter() {
        add_word(word, 1);
    }
    add_word(total, -1);
    let terms: Vec<Term> = coefficient
        .iter()
        .zip(&x)
        .filter(|(&c, _)| c != 0)
        .map(|(&c, &v)| v.scaled(c))
        .collect();
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(terms, 0, tag)).post();

    let mut m = Model::new();
    for (k, ch) in letters.chars().enumerate() {
        m.put(&ch.to_string(), x[k]);
    }
    m
}
