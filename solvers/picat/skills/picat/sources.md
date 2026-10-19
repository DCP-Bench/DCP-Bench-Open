# Sources for `picat`

Tested with Picat 3.9#12 (`picat --version`), Linux x86-64, inside the `dcp-eval/picat:v1` image (Python 3.12.11 on Debian bookworm).

Refactored from the DCP-Bench integration skill; examples verified inside the dcp-eval/picat:v1 image.

Existing skills: none found for Picat when this skill was first written.

- <https://picat-lang.org/download.html> — Picat 3.9#12 download page, released 2026-08-28, the Linux archive used by the install step
- <https://picat-lang.org/download/picat_guide_html/picat_guide.html> — Picat guide, HTML: solving options (common, cp, sat), constraints, findall and solve
- <https://picat-lang.org/download/picat_guide.pdf> — Picat guide, PDF, same content
- <https://picat-lang.org/modules.html> — library modules, including the `sys` predicate `time_out/3`
- `Picat/doc/constraints.tex` in `picat39_12_linux64.tar.gz` — the Constraints chapter of the Picat guide: domain variables, table, arithmetic, Boolean and global constraints, and the solving options of the cp and sat modules
- `Picat/doc/module.tex` in the same archive — static binding of calls, and the run-time search that call/N performs over the loaded modules
- `Picat/doc/all.tex` in the same archive — maps (`get/2`, `put/3`), `vars/1`, `read_term/1`, `findall/2`, loops and `if` statements
- `Picat/LICENSE` in the same archive — Picat is free for any purpose; its C sources are under the Mozilla Public License 2.0
- `/opt/picat/lib/cp.pi`, `sat.pi`, `sys.pi` in the image — the signatures of `solve/1`, `solve/2`, `solve_all/1`, `time_out/3` and the `$report`/`$label` options

Verified by running: every example under `assets/` and the Quick start, in the image, with `picat model.pi`. Also verified by running inside the image:

- `solve(Options, Vars)` order: `solve([$max(X)], [X])` optimises; `solve([X], [$max(X)])` labels the options list and silently returns a non-optimal value.
- `findall(Vars, solve(Vars))` enumerates all solutions of `Vars` (cp and sat).
- `time_out(solve(Vars), Millis, Res)` returns `Res = success` or `time_out`.
- A constraint whose posting fails inside `main` stops the program with `error(failed, main/0)`; an `if (...)` condition catches it.
- Map access with `M.get(n)`, `M.get('NUM_CELLS')`, `M.get('_SHIP')`; `Grid[2,1]` indexes both `new_array` arrays and lists of lists (`L = [[1,2],[3,4]]`, `L[2,1]` is `3`). Chained `L[1][2]` is a syntax error (`wrong expression`).
- `main(Args)` with `picat file.pi instance.json`: `Args` is a list of strings, so `Args[1]` is the file name as a list of characters; `read_file_chars/1` reads it.
- Operators: `10**2` is `100`, `10^2` is `8` (XOR); `Z #= 2 ** X` with `X :: 0..3` posts and solves in `cp`; `Z #= X*10^2` raises `invalid_constraint_expression`.
- Characters: `$a` is `a`; `$0` is the integer 0; `C >= '0'` and `$'5' >= $'0'` fail with `Wrong function in expression`, so comparisons use `ord/1`.
- Heads: `sk(Cs, Cs) => true.` called with an unbound second argument fails; `:-` unifies its head.
- Comprehension comparisons such as `[K == 4 : K in 1..2]` print as terms (`[1 == 4,2 == 4]`), not booleans; `if IsLast[2] == 1` works on a 0/1 list.
- Picat 3.9#12 has no JSON library (`json_decode`, `parse_json` undefined); `assets/read-json-instance/` reads a JSON file with a plain-Picat reader.
- Syntax errors print `*** SYNTAX ERROR *** (line-range)` on stderr with exit code 1.
- The `sat` defect: two variables over 0..3 under `all_different/1`, each equal to `2 * A + B` over its own two 0/1 variables, give 192 solutions under `sat` against the correct 12 under `cp` or with pairwise `#!=` under `sat`.
- The assignment example optimum 13 agrees with a brute-force enumeration of all 24 permutations.

## Independent toy test

An independent tester solved the add-solver toy problems from this skill alone, running each model in `dcp-eval/picat:v1`. All 18 instances passed.

| Problem | Instances | Passed |
|---|---|---|
| cryptarithm | 3 | 3/3 |
| graph-colouring | 3 | 3/3 |
| jobshop | 2 | 2/2 |
| knapsack | 2 | 2/2 |
| knapsack-all-optimal | 3 | 3/3 |
| n-queens | 3 | 3/3 |
| n-queens-all | 2 | 2/2 |
| **Total** | **18** | **18/18** |

Five problems passed after a harness fix only (the import must come first). Cryptarithm and jobshop needed repairs beyond the budget of two, all from Picat behaviour that is now in this skill: `^` as XOR, `**` as power, character literals, chained indexing, index used as a goal, comprehension booleans, and `=>` head matching.

