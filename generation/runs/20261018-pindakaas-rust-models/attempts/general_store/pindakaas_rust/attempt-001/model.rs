// General store puzzle: the sixteen addends CHESS, CASH, BOWWOW, CHOPS, ALSOPS,
// PALEALE, COOL, BASS, HOPS, ALES, HOES, APPLES, COWS, CHEESE, CHSOAP and SHEEP
// sum to ALL WOOL. Each different letter stands for a different digit.
// The instance carries no data: the puzzle is fixed.

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    const LETTERS: &str = "CHESABOWPL";
    let ix = |c: char| LETTERS.find(c).unwrap();

    // Each letter is a digit, and different letters are different digits.
    let x: Vec<IntVar> = LETTERS.chars().map(|_| IntVar::new(0..=9)).collect();
    all_different(s, &x)?;

    let addends = [
        "CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
        "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP",
    ];
    let total = "ALLWOOL";
    let width = 7;

    // Column coefficients: how often each letter appears in each digit position
    // of the addends (positive) and of the total (negative).
    let mut coef = vec![[0i64; 10]; width];
    for w in addends.iter() {
        for (p, ch) in w.chars().rev().enumerate() {
            coef[p][ix(ch)] += 1;
        }
    }
    for (p, ch) in total.chars().rev().enumerate() {
        coef[p][ix(ch)] -= 1;
    }

    // Carries between columns. The sum of a column is at most 16 * 9 + 15 = 159,
    // so a carry is at most 15. The total has seven digits, so there is no carry
    // out of the leftmost column.
    let carry: Vec<IntVar> = (0..width - 1).map(|_| IntVar::new(0..=15)).collect();

    // The words above the horizontal line represent numbers that add to the total of
    // 'ALL WOOL'. Column by column: the addend digits plus the carry in equal the
    // total's digit plus ten times the carry out.
    for p in 0..width {
        let mut e = LinExp::default();
        for l in 0..10 {
            if coef[p][l] != 0 {
                e += scaled(&x[l], coef[p][l]);
            }
        }
        if p > 0 {
            e += scaled(&carry[p - 1], 1);
        }
        if p + 1 < width {
            e += scaled(&carry[p], -10);
        }
        post(s, e, Comparator::Equal, 0)?;
    }

    let mut out = Out::new();
    for (i, ch) in LETTERS.chars().enumerate() {
        out.put(&ch.to_string(), &x[i]);
    }
    Ok(out)
}
