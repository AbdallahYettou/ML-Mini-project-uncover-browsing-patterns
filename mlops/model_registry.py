"""
Model Registry Module

Utilities for registering, versioning, and loading models from W&B registry.
"""

import os
import wandb
import pandas as pd

from mlops.config import (
    WANDB_PROJECT,
    WANDB_API_KEY,
    MODEL_ARTIFACT_NAMES,
    APRIORI_DIR,
    FPGROWTH_DIR,
    ECLAT_DIR,
    PROJECT_ROOT
)


def init_wandb_run(job_type="model-registry"):
    """Initialize W&B run for model registry operations."""
    wandb.login(key=WANDB_API_KEY)
    run = wandb.init(
        project=WANDB_PROJECT,
        job_type=job_type,
        config={"task": "model_registry"}
    )
    return run


def register_model(algorithm, rules_df, metrics, alias=None):
    """
    Register a model to W&B model registry with optional alias.
    
    Parameters:
    - algorithm: Name of algorithm ('apriori', 'fpgrowth', 'eclat')
    - rules_df: DataFrame of association rules
    - metrics: Dict of performance metrics
    - alias: Optional alias like 'production', 'staging', 'best'
    
    Returns:
    - artifact: The registered artifact
    """
    run = init_wandb_run(job_type="model-registration")
    
    try:
        artifact_name = MODEL_ARTIFACT_NAMES.get(algorithm, f"{algorithm}-rules")
        
        # Create artifact
        artifact = wandb.Artifact(
            name=artifact_name,
            type="model",
            description=f"{algorithm.upper()} association rules for web usage mining",
            metadata={
                "algorithm": algorithm,
                "num_rules": len(rules_df),
                **metrics
            }
        )
        
        # Save rules to temp file and add to artifact
        output_dirs = {
            'apriori': APRIORI_DIR,
            'fpgrowth': FPGROWTH_DIR,
            'eclat': ECLAT_DIR
        }
        output_dir = output_dirs.get(algorithm, PROJECT_ROOT)
        rules_file = os.path.join(output_dir, f"{algorithm}_rules.csv")
        
        if os.path.exists(rules_file):
            artifact.add_file(rules_file)
        else:
            # Save if doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            rules_df.to_csv(rules_file, index=False)
            artifact.add_file(rules_file)
        
        # Log artifact with aliases
        aliases = ["latest"]
        if alias:
            aliases.append(alias)
        
        run.log_artifact(artifact, aliases=aliases)
        print(f"✓ Registered model '{artifact_name}' with aliases: {aliases}")
        
        return artifact
        
    finally:
        run.finish()


def load_model(algorithm, version="latest"):
    """
    Load model from W&B registry.
    
    Parameters:
    - algorithm: Name of algorithm
    - version: Version or alias to load ('latest', 'production', 'v1', etc.)
    
    Returns:
    - rules_df: DataFrame of association rules
    """
    wandb.login(key=WANDB_API_KEY)
    api = wandb.Api()
    
    artifact_name = MODEL_ARTIFACT_NAMES.get(algorithm, f"{algorithm}-rules")
    artifact_path = f"{WANDB_PROJECT}/{artifact_name}:{version}"
    
    try:
        artifact = api.artifact(artifact_path)
        download_dir = artifact.download()
        
        # Find the rules CSV file
        for filename in os.listdir(download_dir):
            if filename.endswith('_rules.csv') or filename.endswith('rules.csv'):
                rules_path = os.path.join(download_dir, filename)
                rules_df = pd.read_csv(rules_path)
                print(f"✓ Loaded model '{artifact_name}:{version}' with {len(rules_df)} rules")
                return rules_df
        
        print(f"✗ No rules file found in artifact '{artifact_path}'")
        return None
        
    except Exception as e:
        print(f"✗ Failed to load model: {e}")
        return None


def get_production_model(algorithm):
    """
    Get the production version of a model.
    
    Parameters:
    - algorithm: Name of algorithm
    
    Returns:
    - rules_df: DataFrame of production rules
    """
    return load_model(algorithm, version="production")


def promote_to_production(algorithm, version="latest"):
    """
    Promote a model version to production.
    
    Parameters:
    - algorithm: Name of algorithm
    - version: Version to promote
    """
    wandb.login(key=WANDB_API_KEY)
    api = wandb.Api()
    
    artifact_name = MODEL_ARTIFACT_NAMES.get(algorithm, f"{algorithm}-rules")
    artifact_path = f"{WANDB_PROJECT}/{artifact_name}:{version}"
    
    try:
        artifact = api.artifact(artifact_path)
        artifact.aliases.append("production")
        artifact.save()
        print(f"✓ Promoted '{artifact_name}:{version}' to production")
        
    except Exception as e:
        print(f"✗ Failed to promote model: {e}")


def list_model_versions(algorithm):
    """
    List all versions of a model in the registry.
    
    Parameters:
    - algorithm: Name of algorithm
    
    Returns:
    - versions: List of version info dicts
    """
    wandb.login(key=WANDB_API_KEY)
    api = wandb.Api()
    
    artifact_name = MODEL_ARTIFACT_NAMES.get(algorithm, f"{algorithm}-rules")
    
    try:
        artifacts = api.artifacts(
            type_name="model",
            name=f"{WANDB_PROJECT}/{artifact_name}"
        )
        
        versions = []
        for artifact in artifacts:
            versions.append({
                "version": artifact.version,
                "aliases": artifact.aliases,
                "created_at": artifact.created_at,
                "metadata": artifact.metadata
            })
        
        return versions
        
    except Exception as e:
        print(f"✗ Failed to list versions: {e}")
        return []


if __name__ == "__main__":
    # Example usage
    print("Model Registry Module")
    print("=" * 40)
    
    for algo in ["apriori", "fpgrowth", "eclat"]:
        print(f"\n{algo.upper()} versions:")
        versions = list_model_versions(algo)
        for v in versions:
            print(f"  - {v['version']}: {v['aliases']}")
