This folder contains the research code for the paper:

**Understanding Cross-Cloud Interconnects: Hands-On Measurements and Cost Optimization**  
Paper DOI/arXiv: https://doi.org/10.48550/arXiv.2606.01440

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

