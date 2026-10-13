# essence_prime_minion setup evidence

Sources: Savile Row 1.11.1 release page and manual (https://www-users.york.ac.uk/peter.nightingale/savilerow/),
tarball savilerow-1.11.1-linux.tgz, sha256 7b9653bb9ffa8fd71b29f3d5c2de41011cdc136ed2241f82b39f86aa9b3489c6
(verified in the Dockerfile). Bundled Minion binary; Java 17 runtime (eclipse-temurin:17-jre-jammy, pinned by digest).

Image: dcp-eval/essence_prime_minion:v1, id sha256:542193a0d056ec579dbf0bb37980a8cb47aa53605699e5947f61d74a3a7c2cc5 (about 358 MB).

Commands run, all green:
- python -m evaluation.build essence_prime_minion
- python -m generation.readiness check --solver essence_prime_minion --output solvers/essence_prime_minion/readiness.json
- python -m generation.readiness verify --solver essence_prime_minion --record solvers/essence_prime_minion/readiness.json
- pytest tests/test_solvers.py -q (7 passed, 12 skipped: container tests need every image built)
- pilot fixture through the evaluator (satisfaction, optimisation, maximisation swap, 2 instances, limit 5): accepted, 7/7/1 solutions checked.

Capabilities: satisfaction, minimising/maximising (emitted only when Minion finished, SolverTimeOut:0),
enumeration (satisfaction by -num-solutions with re-asking on duplicate declared outputs; optimisation by
reading the optimum through an auxiliary variable, then fixing it).

Limits: no strings or floats in instances, empty lists are refused, objective on its own line for enumeration,
objective magnitude below 1e12 for enumeration, timeouts keep a 2 s margin inside execution_timeout,
partial satisfaction solutions are lost when the hard time limit kills Savile Row.
Findings: Savile Row accepts one `such that` list only (a second one is a parse error) and an objective must precede it;
a `given`-less instance field is ignored; an untyped or typed `letting x = []` is not accepted.
Disk: / had 306 MB free after the build.
