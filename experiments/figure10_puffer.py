import os
import matplotlib.pyplot as plt

from common import PUFFER_DATA_FILE, create_output_dir, write_json
from CciDecision import compare_algorithms
from defs import *


def build_settings():
    return {
        "num_of_pairs": 7,
        "HOURS": 6192,
        "CONTINENTAL": ContinentalName.EUROPE,
        "direction": Direction.GCP_to_AWS,
        "trace_from_file": True,
        "file": str(PUFFER_DATA_FILE),
        "seed": 100,
        "mean_traffic": 1,
        "num_repeats": 1,
        "toPlot": True,
        "PlotToPaper": True,
        "algorithm_names": ["VPN", "CCI", all_history_algo_name, monthly_algo_name, paper_algo_name],
        "dist": "constant",
        "contract_hours": 168,
        "ski_rental_history": 168,
        "lambda_interval": 1 / 730,
        "duration_mean": 168,
        "c1": 0.9,
        "c2": 1.1,
        "delay_hours": 72,
    }


if __name__ == "__main__":
    settings = build_settings()
    output_dir = create_output_dir(__file__)
    settings["output_dir"] = str(output_dir)
    write_json(output_dir / "hyperparameters.json", settings)

    original_cwd = os.getcwd()
    os.chdir(output_dir)
    try:
        total_costs, total_traffic = compare_algorithms(settings, settings["mean_traffic"], settings["seed"])
        write_json(
            output_dir / "figure10_puffer_summary.json",
            {
                "total_costs": total_costs,
                "total_traffic": total_traffic,
            },
        )
        for stem in ["eff", "bars"]:
            for extension in ["png", "pdf"]:
                source = output_dir / f"{stem}.{extension}"
                target = output_dir / f"figure10_puffer_{stem}.{extension}"
                if source.exists():
                    source.replace(target)
    finally:
        os.chdir(original_cwd)
        plt.close("all")
