# chuffed_cpp setup evidence

- Integration: `solvers/chuffed_cpp/` (Chuffed (C++), native Chuffed API, harness pattern like ortools_cp_sat_cpp).
- Chuffed tag 0.14.0, commit f698d5623bb0c2bcd497388ba966f0436d62caf4, tarball sha256 8f0da88d498bc610d894b784da59f87e1e7570fe017dd7249cc90f6ae81f1267, static libraries in /opt/chuffed.
- Image dcp-eval/chuffed_cpp:v1, sha256:c9ab4df4442483a848ae6ef04e521d4353cde5d1352f55c5d27b8b0121e2ad94, built with `python -m evaluation.build chuffed_cpp` (build.log).
- Readiness: `python -m generation.readiness check --solver chuffed_cpp` passed all 11 required checks plus unbranched_fixed and optimum_enumeration; `verify` passes (solvers/chuffed_cpp/readiness.json).
- `pytest tests/test_solvers.py`: 7 passed, 12 skipped (container tests need every pilot image). The chuffed pilot, maximization and compilation paths ran through the evaluator directly (smoke.log).
- Driver: one fork()ed child per phase, since Chuffed's globals cannot be reset. Optimum is proven before any solution is emitted. Phase 2 fixes the objective and enumerates distinct outputs. Fallback branching over all IntVars, then VSIDS. A root failure (Chuffed calls exit(0)) is reported as unsat.
- Limitations: 32-bit integers, domains within +-500M; output leaves are IntVars only (Booleans through bool2int); a submission calling exit(0) reads as unsat (a rejection, never an acceptance).
- Skill: solvers/chuffed_cpp/skills/chuffed-cpp, validated with `generation.skills validate --project`; examples evaluated and accepted.
- Agents: setup by a claude-sonnet-5-5 subagent, reviewed by claude-opus-5-5.
