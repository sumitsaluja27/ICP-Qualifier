import os
from pathlib import Path
from dotenv import load_dotenv
import yaml
load_dotenv()
# Root directory
ROOT_DIR = Path(__file__).parent.parent
# Load configuration
CONFIG_FILE = ROOT_DIR / "config.yaml"
def load_config():
    """Load configuration from YAML file."""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {CONFIG_FILE}\n"
            f"Please copy config.example.yaml to config.yaml and customize settings."
        )
   
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
   
    # Override with environment variables for sensitive data
    if 'search' in config and 'google' in config['search']:
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key:
            config['search']['google']['api_key'] = api_key
       
        cse_id = os.getenv('GOOGLE_CSE_ID')
        if cse_id:
            config['search']['google']['search_engine_id'] = cse_id
   
    return config
# Load configuration
try:
    CONFIG = load_config()
except FileNotFoundError as e:
    print(f"⚠️ Warning: {e}")
    CONFIG = {}
# Paths
DASHCAM_DATA_PATH = ROOT_DIR / "Data"
DASHCAM_VECTOR_DB_PATH = ROOT_DIR / "vector_db" / "dashcam_vectordb"
METADATA_FILE = ROOT_DIR / "vector_db" / "metadata.json"
RESULTS_FILE = ROOT_DIR / "results.json"
# Create necessary directories
(ROOT_DIR / "vector_db").mkdir(exist_ok=True)
DASHCAM_DATA_PATH.mkdir(exist_ok=True)
