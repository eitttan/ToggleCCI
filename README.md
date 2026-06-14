# IEEE Paper Artifact

This folder contains the research code artifact for the paper:

**Understanding Cross-Cloud Interconnects: Hands-On Measurements and Cost Optimization**  
Paper DOI/arXiv: https://doi.org/10.48550/arXiv.2606.01440

The artifact is a clean, self-contained package for reproducing the simulator-based figures in the paper.

## Structure

- `code/`: simulator core, algorithms, pricing model, definitions, and plotting helpers.
- `database/`: bundled input datasets and pricing catalog used by the experiments.
- `experiments/`: runnable scripts for the paper figures.
- `experiments_output/`: default output folder created when scripts are run.

## Datasets

- `database/mirage.csv`
- `database/channel_puffer.csv`
## Setup

From the artifact root:

```bash
pip install -r requirements.txt
```

Required packages are intentionally minimal:

- `matplotlib`
- `numpy`
- `openpyxl`
- `pandas`

## Running Experiments

Run any script from the artifact root, for example:

```bash
python experiments/<script_name>
```

Outputs are written to `experiments_output/<script_name>__run_<timestamp>/`.

To write outputs somewhere else:

```bash
set TOGGLECCI_OUTPUT_DIR=C:\path\to\output
python experiments/figure08_gcp_azure_mirage.py
```
