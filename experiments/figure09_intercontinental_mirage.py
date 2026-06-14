import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

from common import MIRAGE_DATA_FILE, apply_verification_mode, base_settings, create_output_dir, write_json
from CciDecision import run_simulations_with_general_sweeping
from defs import *


def build_settings(coloc_city):
    settings = {
        **base_settings(),
        "param_to_sweep": "mean_traffic",
        "sweep_values": list(range(20000, 200001, 20000)),
        "xlabel_sweep": "Number of users",
        "num_of_pairs": 8,
        "HOURS": 730 * 24,
        "CONTINENTAL": None,
        "gcp_continents": [ContinentalName.EUROPE],
        "aws_continents": [ContinentalName.EUROPE, ContinentalName.NORTH_AMERICA],
        "coloc_city": coloc_city,
        "direction": Direction.GCP_to_AWS,
        "trace_from_file": True,
        "file": str(MIRAGE_DATA_FILE),
        "seed": 100,
        "mean_traffic_values": list(range(50, 501, 50)),
        "mean_traffic": 220,
        "num_repeats": 20,
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
    }
    return apply_verification_mode(settings)


def run_case(coloc_city, output_dir):
    settings = build_settings(coloc_city)
    settings["output_dir"] = str(output_dir)
    total_cost_summary, total_traffic = run_simulations_with_general_sweeping(settings)
    plt.close()
    return settings, total_cost_summary, total_traffic


def plot_case(ax, x_values, summary, title):
    styles = {
        "VPN": {"color": "#4C78A8", "marker": "o", "linestyle": "-"},
        "CCI": {"color": "#F58518", "marker": "s", "linestyle": "--"},
        all_history_algo_name: {"color": "#B279A2", "marker": "^", "linestyle": ":"},
        monthly_algo_name: {"color": "#E45756", "marker": "v", "linestyle": "-"},
        paper_algo_name: {"color": "#54A24B", "marker": "D", "linestyle": "-."},
    }

    for algo, style in styles.items():
        ax.plot(x_values, summary[algo], label=algo, linewidth=2.0, markersize=5.0, **style)

    ax.set_title(title, fontsize=15)
    ax.set_xlabel("Number of users", fontsize=13)
    ax.set_ylabel("Total cost [USD]", fontsize=13)
    ax.set_ylim(0, 300000)
    ax.grid(True, alpha=0.28)
    ax.tick_params(axis="both", labelsize=11)
    ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))
    ax.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))


if __name__ == "__main__":
    output_dir = create_output_dir(__file__)
    cases = [
        ("paris_colocation", "Paris", "CCI colocation in Paris"),
        ("ohio_colocation", "Ohio", "CCI colocation in Ohio"),
    ]

    payload = {}
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), sharey=True)

    for ax, (case_name, coloc_city, title) in zip(axes, cases):
        settings, summary, total_traffic = run_case(coloc_city, output_dir)
        payload[case_name] = {
            "settings": settings,
            "total_cost_summary": summary,
            "total_traffic": total_traffic,
        }
        plot_case(ax, settings["sweep_values"], summary, title)

    handles, labels = axes[1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=5, fontsize=10.5, frameon=False)
    fig.tight_layout(rect=(0, 0.15, 1, 1))

    write_json(output_dir / "figure09_intercontinental_mirage_summary.json", payload)
    write_json(output_dir / "hyperparameters.json", {name: data["settings"] for name, data in payload.items()})
    fig.savefig(output_dir / "figure09_intercontinental_mirage.pdf", format="pdf", bbox_inches="tight", dpi=300)
    fig.savefig(output_dir / "figure09_intercontinental_mirage.png", bbox_inches="tight", dpi=300)
    plt.show()
