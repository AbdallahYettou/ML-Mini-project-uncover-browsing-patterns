"""
Data Versioning Module

This module handles versioning of datasets using W&B Artifacts.
It tracks the data lineage from raw logs → extracted → cleaned data.
"""

import os
import wandb
from mlops.config import (
    WANDB_PROJECT, 
    WANDB_API_KEY,
    DATA_FILES,
    RAW_LOGS_DIR,
    PROCESSED_DATA_DIR,
    PROJECT_ROOT
)


def init_wandb_run(job_type="data-versioning"):
    """Initialize a W&B run for data versioning."""
    wandb.login(key=WANDB_API_KEY)
    run = wandb.init(
        project=WANDB_PROJECT,
        job_type=job_type,
        config={"task": "data_versioning"}
    )
    return run


def log_raw_data():
    """
    Log raw log files as W&B artifacts.
    This creates a versioned snapshot of the raw NASA access logs.
    """
    run = init_wandb_run(job_type="data-ingestion")
    
    try:
        # Create artifact for raw logs
        artifact = wandb.Artifact(
            name="raw-logs",
            type="raw-data",
            description="NASA HTTP access logs (Aug95 and Jul95)",
            metadata={
                "source": "NASA-HTTP dataset",
                "format": "Apache access log",
                "files": ["access_log_Aug95", "access_log_Jul95"]
            }
        )
        
        # Add raw log files (reference only due to large size)
        for log_file in DATA_FILES["raw_logs"]:
            if os.path.exists(log_file):
                filename = os.path.basename(log_file)
                # For large files, we log a reference with metadata
                artifact.add_reference(f"file://{log_file}", name=filename)
                print(f"  Added reference: {filename}")
        
        # Log the artifact
        run.log_artifact(artifact)
        print("✓ Raw logs artifact logged successfully")
        
    finally:
        run.finish()
    
    return artifact


def log_extracted_data():
    """
    Log extracted session data as W&B artifact.
    This is the output from extract_logs.py.
    """
    run = init_wandb_run(job_type="data-extraction")
    
    try:
        artifact = wandb.Artifact(
            name="extracted-sessions",
            type="extracted-data",
            description="User sessions extracted from raw logs (before cleaning)",
            metadata={
                "source_artifact": "raw-logs",
                "extraction_script": "cleanningData/extract_logs.py"
            }
        )
        
        extracted_file = DATA_FILES["extracted"]
        if os.path.exists(extracted_file):
            artifact.add_file(extracted_file, name="extracted_logs.csv")
            print(f"  Added file: extracted_logs.csv")
        
        run.log_artifact(artifact)
        print("✓ Extracted sessions artifact logged successfully")
        
    finally:
        run.finish()
    
    return artifact


def log_cleaned_data():
    """
    Log cleaned session data as W&B artifact.
    This is the output from clean_extracted_data.py - the final training data.
    """
    run = init_wandb_run(job_type="data-cleaning")
    
    try:
        artifact = wandb.Artifact(
            name="cleaned-sessions",
            type="processed-data",
            description="Cleaned and normalized user sessions ready for mining",
            metadata={
                "source_artifact": "extracted-sessions",
                "cleaning_script": "cleanningData/clean_extracted_data.py",
                "noise_paths_removed": True,
                "max_path_depth": 3,
                "max_session_length": 25
            }
        )
        
        cleaned_file = DATA_FILES["cleaned"]
        if os.path.exists(cleaned_file):
            artifact.add_file(cleaned_file, name="cleaned_data.csv")
            print(f"  Added file: cleaned_data.csv")
        
        # Also add the user sessions file if it exists
        user_sessions = DATA_FILES.get("user_sessions")
        if user_sessions and os.path.exists(user_sessions):
            artifact.add_file(user_sessions, name="usersessions.csv")
            print(f"  Added file: usersessions.csv")
        
        run.log_artifact(artifact)
        print("✓ Cleaned sessions artifact logged successfully")
        
    finally:
        run.finish()
    
    return artifact


def version_all_data():
    """
    Version all datasets in the pipeline.
    Creates a complete data lineage in W&B.
    """
    print("\n" + "="*60)
    print("DATA VERSIONING WITH W&B")
    print("="*60 + "\n")
    
    print("Step 1: Versioning raw logs...")
    log_raw_data()
    
    print("\nStep 2: Versioning extracted sessions...")
    log_extracted_data()
    
    print("\nStep 3: Versioning cleaned sessions...")
    log_cleaned_data()
    
    print("\n" + "="*60)
    print("✓ All data artifacts versioned successfully!")
    print(f"View at: https://wandb.ai/{WANDB_PROJECT}")
    print("="*60 + "\n")


if __name__ == "__main__":
    version_all_data()
