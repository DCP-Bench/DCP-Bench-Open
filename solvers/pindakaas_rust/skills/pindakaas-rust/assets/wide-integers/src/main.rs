// Wide integers: values far beyond what an IntVar can hold. Every linear constraint over an
// IntVar lists each value of its domain, so a domain of 10^8 values aborts. Here the numbers
// are literals worth 2^i each, and the constraints use an adder network, whose cost grows
// with the number of bits.
use pindakaas::constraint::linear::{AdderEncoder, Comparator, LinExp, Linear, LinearEncoder};
use pindakaas::solver::cadical::Cadical;
use pindakaas::solver::{SolveResult, Solver};
use pindakaas::{BoolVal, ClauseDatabaseTools, Lit, Unsatisfiable, Valuation};

type Res<T = ()> = Result<T, Unsatisfiable>;

/// A number `lo + sum 2^i * bits[i]`.
struct Wide {
    bits: Vec<Lit>,
    lo: i64,
}

impl Wide {
    fn exp(&self) -> LinExp {
        let mut e = LinExp::from(self.lo);
        for (i, &b) in self.bits.iter().enumerate() {
            e += LinExp::from(b) * (1i64 << i);
        }
        e
    }

    fn value(&self, sol: &impl Valuation) -> i64 {
        self.bits.iter().enumerate().fold(self.lo, |acc, (i, &b)| acc + if sol.value(b) { 1i64 << i } else { 0 })
    }
}

/// `expr <cmp> k` with the adder encoder: cheap at any width up to 2^62.
fn post_wide(s: &mut Cadical, e: LinExp, cmp: Comparator, k: i64) -> Res {
    s.encode(&Linear::new(e, cmp, k), &LinearEncoder::new(AdderEncoder::default()))
}

/// A fresh number in `0..=hi`. The bits alone reach the next power of two, so cut the top.
fn wide_int(s: &mut Cadical, hi: i64) -> Res<Wide> {
    let n = 64 - (hi as u64).leading_zeros() as usize;
    let w = Wide { bits: (0..n).map(|_| s.new_lit()).collect(), lo: 0 };
    if hi + 1 != 1i64 << n {
        post_wide(s, w.exp(), Comparator::LessEq, hi)?;
    }
    Ok(w)
}

fn main() -> Res {
    // 3x + 7y = 10^15 with x, y in 0..=10^15: all pairs are about 10^14 apart in size.
    let n: i64 = 1_000_000_000_000_000;
    let mut s = Cadical::default();
    let x = wide_int(&mut s, n)?;
    let y = wide_int(&mut s, n)?;
    post_wide(&mut s, x.exp() * 3 + y.exp() * 7, Comparator::Equal, n)?;

    // Enumerate three solutions, blocking each through the bit pattern.
    for _ in 0..3 {
        let (xv, yv) = match s.solve() {
            SolveResult::Satisfied(sol) => (x.value(&sol), y.value(&sol)),
            _ => panic!("expected a solution"),
        };
        println!("x = {xv}, y = {yv}");
        assert_eq!(3 * xv + 7 * yv, n);
        let mut block: Vec<BoolVal> = Vec::new();
        for (w, v) in [(&x, xv), (&y, yv)] {
            for (i, &b) in w.bits.iter().enumerate() {
                block.push(BoolVal::Lit(if (v >> i) & 1 == 1 { !b } else { b }));
            }
        }
        s.add_clause(block)?;
    }

    // Divisibility: a number that is 7 times something plus 3, below 10^12, ending in ...3.
    let mut s = Cadical::default();
    let m = wide_int(&mut s, 999_999_999_999)?;
    let q = wide_int(&mut s, 142_857_142_857)?;
    post_wide(&mut s, m.exp() - q.exp() * 7, Comparator::Equal, 3)?;
    let tenth = wide_int(&mut s, 99_999_999_999)?; // m = 10 * tenth + 3
    post_wide(&mut s, m.exp() - tenth.exp() * 10, Comparator::Equal, 3)?;
    match s.solve() {
        SolveResult::Satisfied(sol) => {
            let v = m.value(&sol);
            println!("m = {v}");
            assert_eq!(v % 7, 3);
            assert_eq!(v % 10, 3);
        }
        _ => panic!("expected a solution"),
    }
    Ok(())
}
