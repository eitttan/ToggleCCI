import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

from common import apply_verification_mode, base_settings, create_output_dir, write_json
from CciDecision import run_simulations_with_general_sweeping
from defs import *


if __name__ == "__main__":
    settings = {
        **base_settings(),
        "param_to_sweep": "poisson_mean_intense",
        "sweep_values": list(range(200, 1201, 100)),
        "xlabel_sweep": "Mean traffic volume per burst [GB/hour]",
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
        "toPlot": False,
        "figure_name": "figure12_bursty_trace",
    }
    settings = apply_verification_mode(settings)

    output_dir = create_output_dir(__file__)
    settings["output_dir"] = str(output_dir)
    write_json(output_dir / "hyperparameters.json", settings)

    run_simulations_with_general_sweeping(settings)

    ax = plt.gca()
    ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
    ax.yaxis.get_offset_text().set_fontsize(18)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.tight_layout()
    plt.savefig(output_dir / f"{settings['figure_name']}.pdf", format="pdf", bbox_inches="tight", dpi=300)
    plt.savefig(output_dir / f"{settings['figure_name']}.png", bbox_inches="tight", dpi=300)
    plt.show()
