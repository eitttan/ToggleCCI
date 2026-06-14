import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

from common import MIRAGE_DATA_FILE, apply_verification_mode, base_settings, create_output_dir, write_json
from CciDecision import compare_algorithms_with_breakdown
from defs import *


def build_settings(continent, direction):
    settings = {
        **base_settings(),
        "num_of_pairs": 8 if continent == ContinentalName.EUROPE else 5,
        "HOURS": 730 * 24,
        "CONTINENTAL": continent,
        "direction": direction,
        "trace_from_file": True,
        "file": str(MIRAGE_DATA_FILE),
        "seed": 100,
        "mean_traffic": 100000,
        "num_repeats": 1,
        "toPlot": False,
        "PlotToPaper": True,
        "algorithm_names": ["VPN", "CCI", all_history_algo_name, monthly_algo_name, paper_algo_name],
        "dist": "constant",
        "contract_hours": 168,
        "ski_rental_history": 730 if continent == ContinentalName.EUROPE else 168,
        "lambda_interval": 1 / 730,
        "duration_mean": 168,
        "delay_hours": 72,
        "c1": 0.9,
        "c2": 1.1,
    }
    return apply_verification_mode(settings)


def plot_breakdown(ax, breakdown, title):
    algorithms = ["VPN", "CCI", all_history_algo_name, monthly_algo_name, paper_algo_name]
    labels = ["VPN", "CCI", "Avg All", "Avg Month", "ToggleCCI"]
    leasing = [breakdown[algo]["leasing_cost"] for algo in algorithms]
    traffic = [breakdown[algo]["traffic_cost"] for algo in algorithms]
    x_positions = range(len(algorithms))

    ax.bar(x_positions, leasing, color="#E45756", label="Leasing")
    ax.bar(x_positions, traffic, bottom=leasing, color="#4C78A8", label="Traffic")
    ax.set_title(title, fontsize=13)
    ax.set_xticks(list(x_positions))
    ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=9)
    ax.set_ylabel("Total cost [USD]", fontsize=11)
    ax.grid(True, axis="y", alpha=0.25)
    ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))


if __name__ == "__main__":
    output_dir = create_output_dir(__file__)
    cases = [
        ("eu_gcp_to_aws", ContinentalName.EUROPE, Direction.GCP_to_AWS, "EU: GCP to AWS"),
        ("eu_aws_to_gcp", ContinentalName.EUROPE, Direction.AWS_to_GCP, "EU: AWS to GCP"),
        ("us_gcp_to_aws", ContinentalName.NORTH_AMERICA, Direction.GCP_to_AWS, "US: GCP to AWS"),
        ("us_aws_to_gcp", ContinentalName.NORTH_AMERICA, Direction.AWS_to_GCP, "US: AWS to GCP"),
    ]

    payload = {}
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.2), sharey=True)

    for ax, (case_name, continent, direction, title) in zip(axes.flatten(), cases):
        settings = build_settings(continent, direction)
        breakdown, total_costs, total_traffic = compare_algorithms_with_breakdown(
            settings,
            settings["mean_traffic"],
            settings["seed"],
        )
        payload[case_name] = {
            "settings": settings,
            "breakdown": breakdown,
            "total_costs": total_costs,
            "total_traffic": total_traffic,
        }
        plot_breakdown(ax, breakdown, title)

    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, fontsize=12, frameon=False)
    fig.tight_layout(rect=(0, 0.08, 1, 1))

    write_json(output_dir / "figure07_cost_breakdown_mirage_summary.json", payload)
    write_json(output_dir / "hyperparameters.json", {name: data["settings"] for name, data in payload.items()})
    fig.savefig(output_dir / "figure07_cost_breakdown_mirage.pdf", format="pdf", bbox_inches="tight", dpi=300)
    fig.savefig(output_dir / "figure07_cost_breakdown_mirage.png", bbox_inches="tight", dpi=300)
    plt.show()
