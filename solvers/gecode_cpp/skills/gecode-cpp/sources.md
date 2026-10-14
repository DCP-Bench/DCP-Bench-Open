# Sources for `gecode-cpp`

- Gecode 6.2.0 as packaged by Debian bookworm, `libgecode-dev=6.2.0-5`
  (<https://packages.debian.org/bookworm/libgecode-dev>). Upstream tag `release-6.2.0`,
  <https://github.com/Gecode/gecode/tree/release-6.2.0>. Licence: MIT-style Gecode licence.
- The installed headers `/usr/include/gecode/{int,set,minimodel,search}.hh` and
  `gecode/int/*.hh`: every signature in `references/constraints.md` was extracted from
  them.
- Christian Schulte, Guido Tack, Mikael Z. Lagerkvist, *Modeling and Programming with
  Gecode*, version for Gecode 6.2.0 (<https://www.gecode.org/doc-latest/MPG.pdf>):
  Space, cloning, MiniModel, propagation levels, branching, search engines, LDSB.
- `references/catalogue.cpp` checks the semantics stated in SKILL.md against brute
  force in the image (51 checks, all passing).
- The DCP section describes `solvers/gecode_cpp/cpp/dcp.h` and `driver.cpp`; the
  examples ran through that driver in `dcp-eval/gecode_cpp:v1`.
