import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

from common import apply_verification_mode, base_settings, create_output_dir, write_json
from CciDecision import run_simulations_with_general_sweeping
from defs import *


if __name__ == "__main__":
    settings = {
        **base_settings(),
        "param_to_sweep": "lambda_interval",
        "sweep_values": [1 / (168 * i) for i in range(1, 9)],
        "xlabel_sweep": "Lambda",
        "num_of_pairs": 1,
        "HOURS": 730 * 12,
        "trace_from_file": False,
        "file": "",
        "dist": "poisson",
        "mean_traffic": 220,
        "mean_traffic_values": list(range(50, 1251, 50)),
        "lambda_interval": 1 / 730,
        "duration_mean": 168,
        "poisson_mean_intense": 400,
        "num_repeats": 20,
        "figure_name": "figure13_inter_burst",
    }
    settings = apply_verification_mode(settings)

    output_dir = create_output_dir(__file__)
    settings["output_dir"] = str(output_dir)
    write_json(output_dir / "hyperparameters.json", settings)

    results, _ = run_simulations_with_general_sweeping(settings)

    denoms = [int(1 / value) for value in settings["sweep_values"]]
    labels = [f"{int(value / 24)}" for value in denoms]
    linestyles = cycle(["-", "--", "-.", ":"])
    markers = cycle(["o", "s", "D", "^", "v", "<", ">", "x", "*", "+", "p", "h"])

    plt.figure(figsize=(6, 4))
    ax = plt.gca()
    for algo in settings["algorithm_names"]:
        plt.plot(
            denoms,
            results[algo],
            linestyle=next(linestyles),
            marker=next(markers),
            label=algo,
        )

    plt.ylabel("Total Cost [USD]", fontsize=18)
    plt.xlabel("Mean inter-burst duration [days]", fontsize=18)
    plt.legend(fontsize=14)
    plt.grid()
    plt.yticks(fontsize=18)
    ax.set_xticks(denoms)
    ax.set_xticklabels(labels, fontsize=18)
    ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
    ax.yaxis.get_offset_text().set_fontsize(18)
    ax.set_yticks(list(range(20000, 200001, 40000)))
    plt.ylim(0, 200000)
    plt.tight_layout()
    plt.savefig(output_dir / f"{settings['figure_name']}.pdf", format="pdf", bbox_inches="tight", dpi=300)
    plt.savefig(output_dir / f"{settings['figure_name']}.png", bbox_inches="tight", dpi=300)
    plt.show()
