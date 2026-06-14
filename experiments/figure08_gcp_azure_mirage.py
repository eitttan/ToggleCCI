import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

from common import MIRAGE_DATA_FILE, apply_verification_mode, base_settings, create_output_dir, write_json
from CciDecision import run_simulations_with_general_sweeping
from defs import *


def build_settings(direction):
    settings = {
        **base_settings(),
        "param_to_sweep": "mean_traffic",
        "sweep_values": list(range(20000, 200001, 20000)),
        "xlabel_sweep": "Number of users",
        "num_of_pairs": 8,
        "HOURS": 730 * 24,
        "CONTINENTAL": ContinentalName.EUROPE,
        "direction": direction,
        "trace_from_file": True,
        "file": str(MIRAGE_DATA_FILE),
        "seed": 100,
        "mean_traffic_values": list(range(50, 501, 50)),
        "mean_traffic": 220,
        "num_repeats": 20 ,
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


def run_case(direction, output_dir):
    settings = build_settings(direction)
    settings["output_dir"] = str(output_dir)
    total_cost_summary, total_traffic = run_simulations_with_general_sweeping(settings)
    plt.close()
    return settings, total_cost_summary, total_traffic


def plot_case(ax, x_values, summary, title):
    styles = {
        "VPN": {"color": "#1f77b4", "marker": "o", "linestyle": "-"},
        "CCI": {"color": "#ff7f0e", "marker": "s", "linestyle": "--"},
        all_history_algo_name: {"color": "#2ca02c", "marker": "^", "linestyle": "-."},
        monthly_algo_name: {"color": "#d62728", "marker": "v", "linestyle": ":"},
        paper_algo_name: {"color": "#9467bd", "marker": "D", "linestyle": "-"},
    }

    for algo, style in styles.items():
        ax.plot(x_values, summary[algo], label=algo, linewidth=1.0, markersize=2.8, **style)

    ax.set_title(title, fontsize=7, fontweight="bold")
    ax.set_xlabel("Number of users", fontsize=6.5)
    ax.set_ylabel("Total Cost [USD]", fontsize=6.5)
    ax.set_ylim(0, 300000)
    ax.grid(True, alpha=0.3, linewidth=0.4)
    ax.tick_params(axis="both", labelsize=5.5, width=0.6, length=2.5)
    for spine in ax.spines.values():
        spine.set_linewidth(0.6)
    ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))
    ax.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))


if __name__ == "__main__":
    output_dir = create_output_dir(__file__)

    cases = [
        ("gcp_to_azure_eu", Direction.GCP_to_AZURE, "(a) EU: GCP -> AZURE"),
        ("azure_to_gcp_eu", Direction.AZURE_to_GCP, "(b) EU: AZURE -> GCP"),
    ]

    payload = {}
    fig, axes = plt.subplots(1, 2, figsize=(5.2, 1.95), sharey=True)

    for ax, (case_name, direction, title) in zip(axes, cases):
        settings, summary, total_traffic = run_case(direction, output_dir)
        payload[case_name] = {
            "settings": settings,
            "total_cost_summary": summary,
            "total_traffic": total_traffic,
        }
        plot_case(ax, settings["sweep_values"], summary, title)

    handles, labels = axes[1].get_legend_handles_labels()
    axes[0].legend(handles, labels, loc="upper left", fontsize=4.8, frameon=True)
    fig.tight_layout()

    write_json(output_dir / "figure08_gcp_azure_mirage_summary.json", payload)
    write_json(output_dir / "hyperparameters.json", {name: data["settings"] for name, data in payload.items()})
    fig.savefig(output_dir / "figure08_gcp_azure_mirage.pdf", format="pdf", bbox_inches="tight", dpi=300)
    fig.savefig(output_dir / "figure08_gcp_azure_mirage.png", bbox_inches="tight", dpi=300)
    plt.show()
