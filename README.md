# DCP-Bench Open

[![Catalogue](https://img.shields.io/badge/Catalogue-DCP%20Rosetta-4f46e5?logo=googlechrome&logoColor=white)](https://dcp-bench.github.io/DCP-Rosetta/)
[![Paper](https://img.shields.io/badge/Paper-arXiv%3A2506.06052-b31b1b?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2506.06052)
[![Release](https://img.shields.io/github/v/release/DCP-Bench/DCP-Bench-Open?label=release)](https://github.com/DCP-Bench/DCP-Bench-Open/releases)
[![License](https://img.shields.io/github/license/DCP-Bench/DCP-Bench-Open)](LICENSE)

DCP-Bench Open is a collaborative benchmark of natural language Discrete Combinatorial Problems, using only integer and Boolean decision variables. Many problem formulations come from the Constraint Programming (CP) community, as well as the Integer Programming community (without continuous variables), Pseudo-Boolean and Satisfiability communities.

This repository holds the problems: for each one a clear natural language description, its data instances and a ground-truth constraint model, currently written in the CPMpy library. You are more than welcome to contribute new problems and/or problem instances for existing problems (please see the [Contributing Guide](CONTRIBUTING.md) for more details).

The evaluator that checks generated models against these references, the solver integrations it runs, the generated models themselves and the interactive catalogue live in [DCP Rosetta](https://github.com/DCP-Bench/DCP-Rosetta), which includes this repository as a submodule. [**Open the interactive catalogue →**](https://dcp-bench.github.io/DCP-Rosetta/)

This benchmark is an open source project that welcomes additional problems and data instances from interested developers. For reproducibility, always use a specific 'Release' in your research (see below). This project started as an extension of the original [CP-Bench](https://huggingface.co/datasets/kostis-init/CP-Bench) published at ECAI 2025.

## Getting the Dataset

There are two main ways to get the benchmark dataset:

### 1. Recommended: Download from a Release

This is the best way to get a stable, versioned copy of the dataset.

1.  Visit the project's [**GitHub Releases page**](https://github.com/DCP-Bench/DCP-Bench-Open/releases).
2.  From the latest release, download the `dcp-bench-open.jsonl` file.

### 2. Generate from Source

If you want to use the very latest (unreleased) version of the problems, you can generate the dataset file yourself.

1.  Clone the repository and install `requirements.txt` (Python 3.12).
2.  Run `python jsonl_convert.py` to create `dcp-bench-open.jsonl`.

The notebook [stats.ipynb](stats.ipynb) shows how to load that file and gather
statistics from it.

## Repository Structure

| Path | What it holds |
| --- | --- |
| `dataset/` | The problems. Per problem, `<name>.cpmpy.py` with the natural language description, a sample instance and the ground-truth CPMpy model, plus `<name>.json` with one or more instances. |
| `dcp_bench/` | The reference loader: reads a problem's data section, declared outputs and instances without running its solve tail. |
| `jsonl_convert.py` | Builds `dcp-bench-open.jsonl` from `dataset/`. |
| `self_consistency.py` | Checks that each problem's example solution satisfies its own model. |
| `tests/` | The dataset audit that CI runs. |

The source catalogue for the problems is documented in [SOURCES.md](SOURCES.md).

## Verifying Problem Consistency

The `self_consistency.py` script ensures that the example solution provided in each problem's `.py` file is valid and executes correctly. It works by adding the generated solution as a constraint and re-solving the model.

To run the check on all problems:

```bash
python self_consistency.py
```

The dataset audit checks that every reference loads, that the first entry of each `.json` matches the embedded example exactly, that every listed instance builds the model, and that instances carry no extra keys beyond `name` and `note`:

```bash
python -m unittest tests.test_dataset
```

## Evaluating generated models

To check models generated from these descriptions, use the container-based evaluator in [DCP Rosetta](https://github.com/DCP-Bench/DCP-Rosetta). It runs each model in an isolated solver image and accepts it only when no solution it produces is rejected by the reference.

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
