from enum import Enum
import json
import os
from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
CODE_DIR = ROOT_DIR / "code"

if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from artifact_paths import MIRAGE_DATA_FILE, OUTPUT_DIR, PUFFER_DATA_FILE


def convert_enums(obj):
    if isinstance(obj, dict):
        return {key: convert_enums(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [convert_enums(value) for value in obj]
    if isinstance(obj, Enum):
        return obj.name
    return obj


def create_output_dir(script_path):
    script_name = Path(script_path).stem
    timestamp = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = OUTPUT_DIR / f"{script_name}__run_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def write_json(path, payload):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(convert_enums(payload), handle, indent=4)


def base_settings():
    from defs import ContinentalName, Direction, all_history_algo_name, monthly_algo_name, paper_algo_name

    return {
        "seed": 100,
        "num_repeats": 1,
        "toPlot": False,
        "PlotToPaper": True,
        "algorithm_names": ["VPN", "CCI", all_history_algo_name, monthly_algo_name, paper_algo_name],
        "contract_hours": 168,
        "ski_rental_history": 168,
        "c1": 0.9,
        "c2": 1.1,
        "delay_hours": 72,
        "CONTINENTAL": ContinentalName.EUROPE,
        "direction": Direction.GCP_to_AWS,
    }


def apply_verification_mode(settings):
    if os.environ.get("TOGGLECCI_VERIFY_RUN") != "1":
        return settings

    settings = dict(settings)
    settings["num_repeats"] = 1
    sweep_values = list(settings.get("sweep_values", []))
    if len(sweep_values) > 4:
        settings["sweep_values"] = [
            sweep_values[0],
            sweep_values[len(sweep_values) // 3],
            sweep_values[(2 * len(sweep_values)) // 3],
            sweep_values[-1],
        ]
    return settings
