import os
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[1]
DATABASE_DIR = ROOT_DIR / 'database'
PRICING_DIR = DATABASE_DIR / 'pricing_catalog'
OUTPUT_DIR = Path(os.environ.get('TOGGLECCI_OUTPUT_DIR', ROOT_DIR / 'experiments_output'))
MIRAGE_DATA_FILE = DATABASE_DIR / 'mirage.csv'
PUFFER_DATA_FILE = DATABASE_DIR / 'channel_puffer.csv'
PRICING_AWS_DIRECT_LINK_FILE = PRICING_DIR / 'aws_direct_Link_out_all_new.xlsx'
