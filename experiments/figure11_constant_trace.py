import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

from common import apply_verification_mode, base_settings, create_output_dir, write_json
from CciDecision import run_simulations_with_general_sweeping
from defs import *


if __name__ == "__main__":
    settings = {
        **base_settings(),
        "param_to_sweep": "mean_traffic",
        "sweep_values": list(range(20, 201, 10)),
        "xlabel_sweep": "Mean traffic volume [GB/hour]",
        "num_of_pairs": 1,
        "HOURS": 730 * 12,
        "trace_from_file": False,
        "file": "",
        "dist": "constant",
        "mean_traffic": 220,
        "mean_traffic_values": list(range(50, 501, 50)),
        "lambda_interval": 1 / 1460,
        "duration_mean": 168 * 2,
        "figure_name": "figure11_constant_trace",
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
