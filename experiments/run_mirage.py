import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

from common import MIRAGE_DATA_FILE, convert_enums, create_output_dir, write_json
from CciDecision import run_simulations_with_general_sweeping
from defs import *


if __name__ == "__main__":
    settings = {
        "param_to_sweep": "mean_traffic",
        "sweep_values": list(range(20000, 200001, 20000)),
        "xlabel_sweep": "Number of users",
        "num_of_pairs": 8,
        "HOURS": 730 * 24,
        "CONTINENTAL": ContinentalName.EUROPE,
        "direction": Direction.GCP_to_AWS,
        "trace_from_file": True,
        "file": str(MIRAGE_DATA_FILE),
        "seed": 100,
        "mean_traffic_values": list(range(50, 501, 50)),
        "mean_traffic": 220,
        "num_repeats": 1,
        "toPlot": False,
        "PlotToPaper": True,
        "algorithm_names": ["VPN", "CCI", all_history_algo_name, monthly_algo_name, paper_algo_name],
        "dist": "constant",
        "contract_hours": 168,
        "ski_rental_history": 168,
        "lambda_interval": 1 / 730,
        "duration_mean": 168,
        "delay_hours": 72,
        "c1": 0.9,
        "c2": 1.1,
        "figure_name": "mirage_vs_number_users",
    }

    output_dir = create_output_dir(__file__)
    settings["output_dir"] = str(output_dir)
    write_json(output_dir / "hyperparameters.json", convert_enums(settings))

    run_simulations_with_general_sweeping(settings)

    ax = plt.gca()
    ax.set_xticks(settings["sweep_values"])
    ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
    ax.yaxis.get_offset_text().set_fontsize(20)
    ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))
    ax.xaxis.get_offset_text().set_fontsize(20)
    plt.tight_layout()
    plt.savefig(output_dir / f"{settings['figure_name']}.pdf", format="pdf", bbox_inches="tight", dpi=300)
    plt.savefig(output_dir / f"{settings['figure_name']}.png", bbox_inches="tight", dpi=300)
    plt.show()
