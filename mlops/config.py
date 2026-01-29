"""
MLOps Configuration Module

Central configuration for W&B project settings, hyperparameters, and paths.
"""

import os
import yaml

# W&B Configuration
WANDB_API_KEY = "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"
WANDB_PROJECT = "web-usage-mining-mlops"
WANDB_ENTITY = None  # Will use default entity

# Project Paths (relative to project root)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "Data")
RAW_LOGS_DIR = os.path.join(DATA_DIR, "Logs")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "extractedAndcleanedData")
APRIORI_DIR = os.path.join(DATA_DIR, "apriori")
FPGROWTH_DIR = os.path.join(DATA_DIR, "fp_growth")
ECLAT_DIR = os.path.join(DATA_DIR, "ECLAT")

# Default Hyperparameters
DEFAULT_HYPERPARAMS = {
    "min_support": 0.01,
    "min_confidence": 0.5,
    "min_lift": 1.0,
    "max_len": 10
}

# Data Files
DATA_FILES = {
    "raw_logs": [
        os.path.join(RAW_LOGS_DIR, "access_log_Aug95"),
        os.path.join(RAW_LOGS_DIR, "access_log_Jul95")
    ],
    "extracted": os.path.join(PROCESSED_DATA_DIR, "extracted_logs.csv"),
    "cleaned": os.path.join(PROCESSED_DATA_DIR, "cleaned_data.csv"),
    "user_sessions": os.path.join(PROCESSED_DATA_DIR, "usersessions.csv")
}

# Model artifact names
MODEL_ARTIFACT_NAMES = {
    "apriori": "apriori-rules",
    "fpgrowth": "fpgrowth-rules", 
    "eclat": "eclat-rules"
}


def load_config(config_path=None):
    """Load configuration from YAML file."""
    if config_path is None:
        config_path = os.path.join(PROJECT_ROOT, "config.yaml")
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}


def get_wandb_config():
    """Get W&B configuration dict."""
    return {
        "api_key": WANDB_API_KEY,
        "project": WANDB_PROJECT,
        "entity": WANDB_ENTITY
    }


def init_wandb():
    """Initialize wandb with API key."""
    import wandb
    wandb.login(key=WANDB_API_KEY)
    return wandb
