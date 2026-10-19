// Crossfigures (CSPLib 021) on the 9x9 grid given in the description.
// X marks a black cell (reported as 0); every other cell holds one digit.
// A run of two or more white cells across or down is a word. Each word is read as a
// number, most significant digit first, with no leading zero, and the clues fix the
// number of each word. The instance has no fields: the grid and the clues come from
// the description.

use std::collections::BTreeMap;

const GRID: [&str; 9] = [
    "....X....",
    "..X...X..",
    ".X..X..X.",
    "....X....",
    "X.XXXXX.X",
    "....X....",
    ".X..X..X.",
    "..X...X..",
    "....X....",
];

fn is_prime(n: i64) -> bool {
    n >= 2 && (2..).take_while(|d| d * d <= n).all(|d| n % d != 0)
}

fn squares(lo: i64, hi: i64) -> Vec<i64> {
    (1..)
        .map(|k: i64| k * k)
        .skip_while(|&s| s < lo)
        .take_while(|&s| s <= hi)
        .collect()
}

// The number written by these digits, most significant first.
fn number(digits: &[View<i64>]) -> IntLinearExp {
    let n = digits.len();
    digits
        .iter()
        .enumerate()
        .map(|(i, d)| *d * 10i64.pow((n - 1 - i) as u32))
        .sum()
}

// sum of terms[i].0 * terms[i].1 == rhs
fn rel(m: &mut Model, terms: &[(View<i64>, i64)], rhs: i64) -> Res<()> {
    let e: IntLinearExp = terms.iter().map(|(v, c)| *v * *c).sum();
    eq2(m, e, rhs)
}

// The value of a word: a view over its length's range, equal to the number its digits make.
// A word has no leading zero.
fn word(m: &mut Model, digits: &[View<i64>]) -> Res<View<i64>> {
    let len = digits.len() as u32;
    let v = m.new_int_decision(10i64.pow(len - 1)..=10i64.pow(len) - 1);
    eq2(m, number(digits) - IntLinearExp::from(v), 0)?;
    m.linear(digits[0]).ge(1).post()?;
    Ok(v)
}

// x lies in the given set of values.
fn in_set(m: &mut Model, x: View<i64>, vals: Vec<i64>) -> Res<()> {
    let set = Set::from_iter(vals.into_iter().map(|v| v..=v));
    let b = m.contains(set).member(x).define();
    m.proposition(BoolFormula::Atom(b)).post()
}

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // Cells: black cells are fixed to 0, white cells take a digit.
    let mut cells: Vec<Vec<View<i64>>> = Vec::new();
    for row in GRID.iter() {
        let line: Vec<View<i64>> = row
            .chars()
            .map(|ch| {
                if ch == 'X' {
                    m.new_int_decision(0..=0)
                } else {
                    m.new_int_decision(0..=9)
                }
            })
            .collect();
        cells.push(line);
    }
    let white = |r: usize, c: usize| GRID[r].as_bytes()[c] != b'X';

    // Words, numbered in reading order as in the grid. Across and down words are
    // maximal white runs of two or more cells.
    let mut across: BTreeMap<usize, Vec<View<i64>>> = BTreeMap::new();
    let mut down: BTreeMap<usize, Vec<View<i64>>> = BTreeMap::new();
    let mut next = 1usize;
    for r in 0..9 {
        for c in 0..9 {
            if !white(r, c) {
                continue;
            }
            let starts_across = (c == 0 || !white(r, c - 1)) && c + 1 < 9 && white(r, c + 1);
            let starts_down = (r == 0 || !white(r - 1, c)) && r + 1 < 9 && white(r + 1, c);
            if !starts_across && !starts_down {
                continue;
            }
            if starts_across {
                let run: Vec<View<i64>> = (c..9)
                    .take_while(|&cc| white(r, cc))
                    .map(|cc| cells[r][cc])
                    .collect();
                across.insert(next, run);
            }
            if starts_down {
                let run: Vec<View<i64>> = (r..9)
                    .take_while(|&rr| white(rr, c))
                    .map(|rr| cells[rr][c])
                    .collect();
                down.insert(next, run);
            }
            next += 1;
        }
    }

    // Word values.
    let mut av: BTreeMap<usize, View<i64>> = BTreeMap::new();
    for (n, digits) in &across {
        let v = word(m, digits)?;
        av.insert(*n, v);
    }
    let mut dv: BTreeMap<usize, View<i64>> = BTreeMap::new();
    for (n, digits) in &down {
        let v = word(m, digits)?;
        dv.insert(*n, v);
    }
    let a = |n: usize| av[&n];
    let d = |n: usize| dv[&n];

    // Across 1: 27 across times two.
    rel(m, &[(a(1), 1), (a(27), -2)], 0)?;
    // Across 4: 4 down plus seventy-one.
    rel(m, &[(a(4), 1), (d(4), -1)], 71)?;
    // Across 7: 18 down plus four.
    rel(m, &[(a(7), 1), (d(18), -1)], 4)?;
    // Across 8: 6 down divided by sixteen.
    rel(m, &[(d(6), 1), (a(8), -16)], 0)?;
    // Across 9: 2 down minus eighteen.
    rel(m, &[(d(2), 1), (a(9), -1)], 18)?;
    // Across 10: Dozen in six gross.
    rel(m, &[(a(10), 1)], 72)?;
    // Across 11: 5 down minus seventy.
    rel(m, &[(d(5), 1), (a(11), -1)], 70)?;
    // Across 13: 26 down times 23 across.
    m.mul(d(26), a(23)).result(a(13)).post()?;
    // Across 15: 6 down minus 350.
    rel(m, &[(d(6), 1), (a(15), -1)], 350)?;
    // Across 17: 25 across times 23 across.
    m.mul(a(25), a(23)).result(a(17)).post()?;
    // Across 20: A square number.
    in_set(m, a(20), squares(1000, 9999))?;
    // Across 23: A prime number.
    let primes: Vec<i64> = (10..=99).filter(|&p| is_prime(p)).collect();
    in_set(m, a(23), primes)?;
    // Across 24: A square number.
    in_set(m, a(24), squares(10, 99))?;
    // Across 25: 20 across divided by seventeen.
    rel(m, &[(a(20), 1), (a(25), -17)], 0)?;
    // Across 27: 6 down divided by four.
    rel(m, &[(d(6), 1), (a(27), -4)], 0)?;
    // Across 28: Four dozen.
    rel(m, &[(a(28), 1)], 48)?;
    // Across 29: Seven gross.
    rel(m, &[(a(29), 1)], 1008)?;
    // Across 30: 22 down plus 450.
    rel(m, &[(a(30), 1), (d(22), -1)], 450)?;

    // Down 1: 1 across plus twenty-seven.
    rel(m, &[(d(1), 1), (a(1), -1)], 27)?;
    // Down 2: Five dozen.
    rel(m, &[(d(2), 1)], 60)?;
    // Down 3: 30 across plus 888.
    rel(m, &[(d(3), 1), (a(30), -1)], 888)?;
    // Down 4: Two times 17 across.
    rel(m, &[(d(4), 1), (a(17), -2)], 0)?;
    // Down 5: 29 across divided by twelve.
    rel(m, &[(a(29), 1), (d(5), -12)], 0)?;
    // Down 6: 28 across times 23 across.
    m.mul(a(28), a(23)).result(d(6)).post()?;
    // Down 10: 10 across plus four.
    rel(m, &[(d(10), 1), (a(10), -1)], 4)?;
    // Down 12: Three times 24 across.
    rel(m, &[(d(12), 1), (a(24), -3)], 0)?;
    // Down 14: 13 across divided by sixteen.
    rel(m, &[(a(13), 1), (d(14), -16)], 0)?;
    // Down 16: 28 down times fifteen.
    rel(m, &[(d(16), 1), (d(28), -15)], 0)?;
    // Down 17: 13 across minus 399.
    rel(m, &[(a(13), 1), (d(17), -1)], 399)?;
    // Down 18: 29 across divided by eighteen.
    rel(m, &[(a(29), 1), (d(18), -18)], 0)?;
    // Down 19: 22 down minus ninety-four.
    rel(m, &[(d(22), 1), (d(19), -1)], 94)?;
    // Down 20: 20 across minus nine.
    rel(m, &[(a(20), 1), (d(20), -1)], 9)?;
    // Down 21: 25 across minus fifty-two.
    rel(m, &[(a(25), 1), (d(21), -1)], 52)?;
    // Down 22: 20 down times six.
    rel(m, &[(d(22), 1), (d(20), -6)], 0)?;
    // Down 26: Five times 24 across.
    rel(m, &[(d(26), 1), (a(24), -5)], 0)?;
    // Down 28: 21 down plus twenty-seven.
    rel(m, &[(d(28), 1), (d(21), -1)], 27)?;

    let mut out = Out::new();
    out.put("M", cells);
    Ok(out)
}
