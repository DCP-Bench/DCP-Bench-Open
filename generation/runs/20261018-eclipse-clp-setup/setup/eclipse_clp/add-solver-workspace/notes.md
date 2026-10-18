# ECLiPSe 7.2 #13 probes (image dcp-eval/eclipse_clp:v1), continuation notes

Run form: `docker run --rm --network none --entrypoint /opt/eclipse/lib/x86_64_linux/eclipse.exe -e ECLIPSEDIR=/opt/eclipse -e LD_LIBRARY_PATH=/opt/eclipse/lib/x86_64_linux -v <dir>:/w -w /w dcp-eval/eclipse_clp:v1 -f model.ecl -e main`. No `eclipse` wrapper script in the tarball install (no bin/ dir); only eclipse.exe. EOF on stdin ends the toplevel after -e.

## Corrections to the earlier notes
- lib(json) EXISTS (json_read/3 with [names_as_atoms] gives {[key:Value,...]}; json_write/3 with [indent(0)] writes one line). Earlier note "no JSON library" was wrong. lib(csv) exists too.
- `:- import alldifferent/1 from ic_global.` after `:- lib(ic). :- lib(ic_global).` resolves the ambiguity.
- table/2 lives in lib(ic_mdd) (also reexported by ic_global_gac); `:- lib(ic_mdd).` then `table([[A,B]], Rows)` works. gfd also exports table/2, gcc/2, disjunctive/2, cumulative/4, circuit/1, element/3, cumulatives/5, bin_packing/3, regular/2, sequence/4,5, nvalues/3, count/4, among/4, disjoint2/1 (not yet run).
- ic_edge_finder and ic_edge_finder3 export disjunctive/2, cumulative/4, cumulative/5; ic_cumulative exports cumulative/4; lib(cumulative) exports cumulative/4. ic_global exports nvalue/2, ordered_sum/2, lexico_le/2, bin_packing/3,4, alldifferent_matrix/1. ic exports circuit/1, element/3, alldifferent/1, labeling/1, indomain/1, and re-exports ic_search (search/6).
- nth0/nth1 are undefined without lib(listut) ("calling an undefined procedure nth1(...) in module eclipse").
- `seed/1` is a built-in: `:- dynamic seed/1` gives "trying to redefine a built-in predicate".
- `collection_to_list/2` on a 2-D array returns a list of row arrays (then get_finite_integer_bounds type error); use `flatten_array/2`. `collection_to_list(M[I,1..N], Row)` gives a row list.
- argv: while the -e goal runs, `argv(all, L)` = [ProgramPath | UserArgs] (strings); `-f`, `-e`, `--` are already removed. In a `:- directive` during load they are still present.
- gfd search/6 rejects indomain_middle ("out of range in search(...)"); gfd prints "Loaded Gecode solver 6.2.0" on stdout at first use.
- bb_min default prints "Found a solution with cost ..." lines on stdout; `bb_options{report_success:true/0, report_failure:true/0}` silences them. `bb_options{timeout:Secs}` makes bb_min exit normally with the best found and print "Branch-and-bound timeout while searching for solution better than N"; `report_timeout:mark/0` hook lets the model record that the run was not proven. `solutions:all` backtracks through all optimal solutions (gave 2 teams on the cost-5 team toy). Strategies: continue (default), restart/step, dichotomic. delta default 1.0 (use smaller for non-integral cost).
- timeout/3 (lib(timeout)) did not stop a long gfd (Gecode) search: a gfd magic-square N=6 batch ran past 600 s though each call was wrapped in timeout(...,60,...). Not yet isolated; the background container may still be running (docker kill was denied by the permission system, so it was left alone).

## Measured (cputime inside ECLiPSe; wall adds ~0.28 s start-up)
Toy models (all in solvers/eclipse_clp/skills/eclipse-clp/assets/, each about 0.3 s wall): satisfy-magic-square 4x4, all-solutions-queens N=8 (92), maximise-knapsack (value 51), minimise-jobshop 3x3 (makespan 10), cumulative-schedule (makespan 9), table-element-lex (4 routes), routing-tour (44), infeasible-pigeonhole (infeasible), data-assignment (JSON, total 13), all-optimal-team (2 teams).

ft06 (optimum 55), 6x6, bb_min continue, smallest/indomain_min: ic_edge_finder disjunctive/2 0.01 s; ic_edge_finder3 0.01 s; ic_edge_finder cumulative/4 with limit 1 0.01 s; ic_cumulative cumulative/4 limit 1: no proof in 120 s; pairwise reified `or` disjunction: no proof in 120 s.
Random 7x7 (LCG seed 6, optimum 56): ef smallest/min 0.92 s; ef input_order 4.36; ef first_fail 0.34; ef smallest/max 4.76; ef smallest/split 0.93; ef anti_first_fail 15.55; restart 0.94; dichotomic 0.93; ef3 0.01; efcum 0.38; ic_cumulative and pairwise: >60 s.
7x7 seed 3 (optimum 58): ef3 smallest 1.19 s, ef3 first_fail 0.04 s. 8x8 seed 7: ef3 first_fail 0.05 s (67), ef3 smallest, ef first_fail, efcum first_fail all >60 s: heavy-tailed, order matters unpredictably. 10x10 seed 1: no proof in 60 s; with bb timeout 5 s the best found is 90.
N-queens (decomposed #\= unless noted): ic all N=10: 0.03 s dec vs 0.65 s alldifferent-triple; ic all N=12: 0.80 s dec vs 16.25 s alld; gfd all N=12: 0.99 s dec, 1.14 s alld. First solution first_fail: ic N=100 0.01 s, N=200 9.2 s; gfd N=100 0.04, N=200 2.52 s; ic alld N=60 >60 s while gfd alld N=100 0.00 s. input_order N=30: ic >60 s, gfd 55.7 s.
Magic square first solution, first_fail/indomain_min: ic N=5 alld 0.04, dec 0.01; ic N=6 alld 3.96, dec 1.17; ic N=7 both >60 s; gfd N=4,5 about 0.00-0.02 s; gfd N=6 not finished.

## Not done
README.md per asset, SKILL.md, sources.md, evals/evals.json, validation, check_integration; gfd N=6 magic-square timing (hangs past timeout/3); gfd gcc/table/cumulative/disjunctive signatures run; error-text table for Common issues (partly known above); fix wording of the last line in all-solutions-queens/model.ecl ("row 1 in column 1").
