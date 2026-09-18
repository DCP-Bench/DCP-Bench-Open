# DCP-Bench Open

[![Website](https://img.shields.io/badge/Website-DCP--Bench%20Open-4f46e5?logo=googlechrome&logoColor=white)](https://dcp-bench.github.io/DCP-Bench-Open/)
[![Deploy](https://github.com/DCP-Bench/DCP-Bench-Open/actions/workflows/deploy.yml/badge.svg)](https://github.com/DCP-Bench/DCP-Bench-Open/actions/workflows/deploy.yml)
[![Paper](https://img.shields.io/badge/Paper-arXiv%3A2506.06052-b31b1b?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2506.06052)
[![Release](https://img.shields.io/github/v/release/DCP-Bench/DCP-Bench-Open?label=release)](https://github.com/DCP-Bench/DCP-Bench-Open/releases)
[![License](https://img.shields.io/github/license/DCP-Bench/DCP-Bench-Open)](LICENSE)

DCP-Bench Open is a collaborative benchmark of Discrete Combinatorial Problems using only integer and Boolean decision variables. Many problem formulations come from the Constraint Programming (CP) community, as well as the Integer Programming community (without continuous variables), Pseudo-Boolean and Satisfiability communities.

[**Open the interactive catalogue (DCP Rosetta) →**](https://dcp-bench.github.io/DCP-Bench-Open/)

This benchmark has two primary goals:

1.  **To provide a centralized repository** of discrete combinatorial optimisation and satisfaction problems, including clear natural language descriptions, corresponding data instances and ground-truth constraint models. You are more than welcome to contribute new problems and/or problem instances for existing problems (please see the [Contributing Guide](CONTRIBUTING.md) for more details).
2.  **To serve as an evaluation framework** for evaluating generative AI systems (e.g. LLMs) in their ability to generate executable constraint models from natural language descriptions.

In the repository, the ground-truth models are (currently) using the CPMpy library. The evaluation package runs registered solver integrations in containers and checks their declared outputs against the CPMpy reference. See [evaluation setup and usage](evaluation/README.md).

The generated models shown on the website are a draft collection: every one was
accepted by this repository's evaluator, but coverage is still growing, so the
collection is not yet a settled generated-model benchmark. Use a tagged release
when reporting results.

This benchmark is an open source project that welcomes additional problems, data instances and evaluation tooling from interested developers. For reproducibility, always use a specific 'Release' in your research (see below). This project started as an extension of the original [CP-Bench](https://huggingface.co/datasets/kostis-init/CP-Bench) published at ECAI 2025.

## Getting the Dataset

There are two main ways to get the benchmark dataset:

### 1. Recommended: Download from a Release

This is the best way to get a stable, versioned copy of the dataset and all corresponding evaluation scripts.

1.  Visit the project's [**GitHub Releases page**](https://github.com/DCP-Bench/DCP-Bench-Open/releases).
2.  From the latest release, download the `dcp-bench-open.jsonl` file (and if you need more files, e.g. eval scripts etc., then download the `Source code` archive as well).

### 2. Generate from Source

If you want to use the very latest (unreleased) version of the problems, you can generate the dataset file yourself.

1.  Clone the repository.
2.  Run `python jsonl_convert.py` to create `dcp-bench-open.jsonl`.

The notebook [stats.ipynb](stats.ipynb) shows how to load that file and gather
statistics from it.


## The catalogue website

From the repository root, build the static site and serve it:

```bash
python jsonl_convert.py
python generate_site.py
python -m http.server 8000 --directory site
```

Then open <http://localhost:8000/>. The hosted version is the [interactive catalogue](https://dcp-bench.github.io/DCP-Bench-Open/).

Alongside the problem catalogue, the
[paradigm breakdown](https://dcp-bench.github.io/DCP-Bench-Open/paradigms.html)
groups the verified models by the kind of model they are — constraint
programming, MIP, SMT, ASP and so on — with how much of the catalogue each
paradigm reaches and which problems have been modelled in more than one of
them. Those are the problems worth reading side by side.

## Repository Structure

The benchmark itself:

| Path | What it holds |
| --- | --- |
| `dataset/` | The problems. Per problem, `<name>.cpmpy.py` with the natural language description, a sample instance and the ground-truth CPMpy model, plus `<name>.json` with one or more instances. |
| `generated_models/` | Models produced by generative systems, with the verdict each one received. Not ground truth — see [SOURCES.md](SOURCES.md). |
| `web/` | Source for the catalogue website. `generate_site.py` builds it into `site/`, which is generated and not committed. |

The evaluation framework:

| Path | What it holds |
| --- | --- |
| `evaluation/` | The verifier. Runs a candidate in a container and checks its answers against the reference model. See [evaluation/README.md](evaluation/README.md). |
| `solvers/` | One directory per framework integration: image, runner, readiness checks, and the modelling skill for that framework. Each one declares the modelling paradigm its submissions are written in, drawn from the vocabulary in [solvers/paradigms.json](solvers/paradigms.json). |
| `runner/` | The protocol that runs inside those images. |
| `tests/` | Unit tests, plus container tests behind `DCP_CONTAINER_TESTS=1`. |

The model generation framework:

| Path | What it holds |
| --- | --- |
| `skills/` | Instructions an agent follows: `model-generator` runs a "campaign", `solver-setup` adds a framework. |
| `generation/` | The campaign harness — work queue, run ledger, readiness gate — and `runs/`, the record of past campaigns. See [generation/README.md](generation/README.md); its agent-facing contract is [generation/AGENTS.md](generation/AGENTS.md). |

The source catalogue for the problems is documented in [SOURCES.md](SOURCES.md).


## Evaluation framework

The container-based [evaluation package](evaluation/README.md) provides a Python API, a JSON CLI and configurable instance/solution counts. Ten integrations are certified: CPMpy, CP-SAT (Python and C++), MiniZinc/Gecode, Z3, clingo, SWI-Prolog/CLP(FD), PuLP/CBC, PyChoco and Pumpkin (Rust). Build their images explicitly with `python -m evaluation.build`.

A model is accepted by falsification rather than by comparison: the evaluator enumerates the candidate's solutions and looks for one the reference rejects. Finding none within the budget is what acceptance means, so a larger solution limit is a stronger test.

To use the evaluation framework, you will need Python 3.12 and the libraries listed in `requirements.txt`.

### Verifying Problem Consistency

The `self_consistency.py` script ensures that the example solution provided in each problem's `.py` file is valid and executes correctly. It works by adding the generated solution as a constraint and re-solving the model.

To run the check on all problems:

```bash
python self_consistency.py
```

### Automated evaluation of solution accuracy

The `eval.py` script can be used to automate this evaluation process provided that there exists a file containing the generated models. For example, if you have the file `sample_test.jsonl` with generated models, you can run:

```bash
 python eval.py --dataset_file dcp-bench-open.jsonl --test_file sample_test.jsonl --modelling_framework CPMpy
```

Here, `--dataset_file` specifies the path to the jsonl version of the benchmark, `--test_file` specifies the path to the file with generated models, and `--modelling_framework` indicates a registered container integration. Legacy aliases are `CPMpy`, `OR-Tools`/`ortools`, and `MiniZinc`; unsupported frameworks fail explicitly.

### Creating your test file with models to be evaluated

Regarding the test file, each line should be a JSON object with two keys: `id` and `model`.
* `id`: The ID of the problem exactly as it appears in the dataset (e.g., `csplib_001_car_sequencing`).
* `model`: The generated model for the problem (as a string representing runnable code). Make sure that it eventually outputs the solution as a json with key(s) as described in the `decision_variables` entry and values as would be expected in the problem. This is part of the evaluation as well: unexpected keys, or value types are considered incorrect. This is because our automatic evaluation is based on the solution printed by the submitted models.

An example test file with 5 generated models is included ([sample_test.jsonl](sample_test.jsonl)). Four of them are wrong on purpose, so running it shows what each kind of rejection looks like:

```
FAIL csplib_001_car_sequencing   execution_error  TypeError: list indices must be integers or slices, not _IntVarImpl
FAIL csplib_002_template_design  execution_error  IndexError: index 7 is out of bounds for axis 0 with size 7
FAIL csplib_005_autocorrelation  invalid_output  Expected exactly these outputs: ['sequence']
FAIL csplib_006_golomb_rulers    suboptimal_solution  Declared outputs cannot achieve the reference optimum
PASS csplib_007_all_interval     accepted

1/5 accepted. Full JSON in summary.txt.
```

`eval.py` checks the embedded example instance only. To check a model against the other instances of a problem, use the evaluation package directly — see [evaluation/README.md](evaluation/README.md).

## Generating models

The same problem modelled in many frameworks is more useful than the same
problem modelled once, so this repository also contains the machinery to write and evaluate models.

An agent follows `skills/model-generator`: it picks work from a queue ordered
so that problems with several instances come first (a model that hardcoded the
example cannot survive a second instance), writes a model from the reference,
and submits it to the evaluator. A model is kept only when the evaluator
accepts it.

Every campaign leaves a ledger under `generation/runs/`: what was attempted,
what the evaluator said, and what was kept, including the attempts that failed.

## Benchmark Design

*   **Satisfiable Problems:** All problems are designed to have at least one feasible solution. For multi-instance problems, at least the first instance is guaranteed to be satisfiable, the rest are not guaranteed to be solvable in a short amount of time, information about runtimes is currently not part of the dataset.
*   **Human-Readable Descriptions:** Problem descriptions are written to be clear and preferably non-technical.
*   **Clear Output Format:** The required output format for each problem is explicitly specified to facilitate automated evaluation of solution accuracy.

## How to Contribute

We encourage contributions to expand the benchmark! If you have a new problem you'd like to add, please follow the guidelines outlined in our **[Contributing Guide](CONTRIBUTING.md)**.

## Citation

Feel free to cite our work as follows:

```bibtex
@misc{michailidis2026dcpbenchopenevaluatingllmsconstraint,
      title={DCP-Bench-Open: Evaluating LLMs for Constraint Modelling of Discrete Combinatorial Problems}, 
      author={Kostis Michailidis and Dimos Tsouros and Tias Guns},
      year={2026},
      eprint={2506.06052},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2506.06052}, 
}
```

```bibtex
@dataset{dcpbenchopen,
  author       = {Michailidis, K. and Tsouros, D. and Guns, T.},
  title        = {DCP-Bench-Open},
  year         = {2025},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.17800138},
  url          = {https://doi.org/10.5281/zenodo.17800138}
}
```
