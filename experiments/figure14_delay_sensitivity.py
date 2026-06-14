import matplotlib.pyplot as plt

from common import apply_verification_mode, base_settings, create_output_dir, write_json
from CciDecision import run_simulations_with_general_sweeping
from defs import *


if __name__ == "__main__":
    settings = {
        **base_settings(),
        "param_to_sweep": "delay_hours",
        "sweep_values": list(range(0, 169, 24)),
        "xlabel_sweep": "Delay [hours]",
        "num_of_pairs": 1,
        "HOURS": 730 * 12,
        "trace_from_file": False,
        "file": "",
        "dist": "poisson",
        "mean_traffic": 450,
        "mean_traffic_values": list(range(50, 1251, 50)),
        "lambda_interval": 1 / 730,
        "duration_mean": 168,
        "poisson_mean_intense": 430,
        "num_repeats": 20,
        "figure_name": "figure14_delay_sensitivity",
    }
    settings = apply_verification_mode(settings)

    output_dir = create_output_dir(__file__)
    settings["output_dir"] = str(output_dir)
    write_json(output_dir / "hyperparameters.json", settings)

    total_cost_summary, _ = run_simulations_with_general_sweeping(settings)
    write_json(output_dir / "summary_delay_hours.json", total_cost_summary)

    ax = plt.gca()
    ax.set_xticks(settings["sweep_values"])
    ax.set_xlabel("Delay [hours]", fontsize=18)
    ax.set_ylabel("Total Cost [USD]", fontsize=18)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.legend(loc="upper left", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / f"{settings['figure_name']}.pdf", format="pdf", dpi=300, bbox_inches="tight")
    plt.savefig(output_dir / f"{settings['figure_name']}.png", dpi=300, bbox_inches="tight")
