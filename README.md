# DCP-Bench-Open

DCP-Bench-Open is a collaborative benchmark of Discrete Combinatorial Problems, with only involving integer and Boolean decision variables. Many problem formulations come from the Constraint Programming (CP) community, as well as the Integer Programming community (no continuous variables), Pseudo-Boolean and Satisfiability communities.

This benchmark has two primary goals:

1.  **To provide a centralized repository** of discrete combinatorial optimisation and satisfaction problems, including clear natural language descriptions, corresponding data instances and ground-truth constraint models. You are more than welcome to contribute new problems and/or problem instances for existing problems (please see the [Contributing Guide](CONTRIBUTING.md) for more details).
2.  **To serve as an evaluation framework** for evaluating generative AI systems (e.g. LLMs) in their ability to generate executable constraint models from natural language descriptions.

In the repository, the ground-truth models are (currently) using the CPMpy library. The evaluation framework can (currently) evaluate generated models in CPMpy, MiniZinc or Or-Tools CP-SAT and more can be added with limited effort.

This benchmark is an open source project that welcomes additional problems, data instances and evaluation tooling from interested developers. For reproducability, always use a specific 'Release' in your research (see below). This project started as an extension of the original [CP-Bench](https://huggingface.co/datasets/kostis-init/CP-Bench) published at ECAI 2025.

## Getting the Dataset

There are two main ways to get the benchmark dataset:

### 1. Recommended: Download from a Release

This is the best way to get a stable, versioned copy of the dataset and all corresponding evaluation scripts.

1.  Visit the project's [**GitHub Releases page**](https://github.com/kostis-init/CP-Bench-Colab/releases).
2.  From the latest release, download the `dcp-bench-open.jsonl` file (and if you need more files, e.g. eval scripts etc., then download the `Source code` archive as well).

### 2. Generate from Source

If you want to use the very latest (unreleased) version of the problems, you can generate the dataset file yourself.

1.  Clone the repository.
2.  Run `python jsonl_convert.py` to create `dcp-bench-open.jsonl`.


## Repository Structure

The `dataset/` directory contains the source problems for the benchmark. Each problem consists of two files:

*   `<problem_name>/<problem_name>.cpmpy.py`: A Python script containing the natural language problem description, a sample instance, and a ground-truth CPMpy model.
*   `<problem_name>/<problem_name>.json`: A JSON file containing one or more instances for the problem, compatible with the python script.


## Evaluation framework

To use the evaluation framework, you will need Python 3.12 and the libraries listed in `requirements.txt`.

### Verifying Problem Consistency

The `self_consistency.py` script ensures that the example solution provided in each problem's `.py` file is valid and executes correctly. It works by adding the generated solution as a constraint and re-solving the model.

To run the check on all problems:

```bash
python self_consistency.py
```

### Generating a JSONL file containing all problems

To generate a new JSONL file containing all problems in the `dataset/` directory, you can use the `jsonl_convert.py` script:

```bash
python jsonl_convert.py
```

### Automated evaluation of solution accuracy

This dataset is primarily designed to evaluate systems that generate constraint models from natural language. A generated model is considered correct if it produces a valid solution for a given instance. This can be verified by checking if the solution satisfies the constraints of the ground-truth model provided in the dataset. For optimization problems, the objective value must also match. 

The `eval.py` script can be used to automate this evaluation process provided that there exists a file containing the generated models. For example, if you have the file `sample_test.jsonl` with generated models, you can run:

```bash
 python eval.py --dataset_file dcp-bench-open.jsonl --test_file sample_test.jsonl --modelling_framework CPMpy
```

Here, `--dataset_file` specifies the path to the jsonl version of the benchmark, `--test_file` specifies the path to the file with generated models, and `--modelling_framework` indicates the modelling framework used in the generated models. 

### Creating your test file with models to be evaluated

Regarding the test file, each line should be a JSON object with two keys: `id` and `model`.
* `id`: The ID of the problem exactly as it appears in the dataset (e.g., `csplib_001_car_sequencing`).
* `model`: The generated model for the problem (as a string representing runnable code). Make sure that it eventually outputs the solution as a json with key(s) as described in the `decision_variables` entry and values as would be expected in the problem. This is part of the evaluation as well: unexpected keys, or value types are considered incorrect. This is because our automatic evaluation is based on the solution printed by the submitted models.

An example test file with just 5 generated models can be found in this repo for your assistance ([sample_test.jsonl](sample_test.jsonl)).

Finally, for now, evaluation assumes that the first instance of each (multi-instance) problem is used.

## Benchmark Design

*   **Satisfiable Problems:** All problems are designed to have at least one feasible solution. For multi-instance problems, at least the first instance is guaranteed to be satisfiable, the rest are not guaranteed to be solvable in a short amount of time, information about runtimes is currently not part of the dataset.
*   **Human-Readable Descriptions:** Problem descriptions are written to be clear and preferably non-technical.
*   **Clear Output Format:** The required output format for each problem is explicitly specified to facilitate automated evaluation of solution accuracy.

## How to Contribute

We encourage contributions to expand the benchmark! If you have a new problem you'd like to add, please follow the guidelines outlined in our **[Contributing Guide](CONTRIBUTING.md)**.

## Citation

Feel free to cite our work as follows:

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

or (APA format):
```
Michailidis, K., Tsouros, D., & Guns, T. (2025). DCP-Bench-Open [Data set]. Zenodo. https://doi.org/10.5281/zenodo.17800138
```

And here is the paper reference:

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
