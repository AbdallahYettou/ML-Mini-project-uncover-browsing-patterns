"""
MLOps Pipeline Automation

End-to-end training pipeline that orchestrates:
1. Data preprocessing (optional)
2. Data versioning
3. Training all algorithms
4. Model registration
"""

import os
import sys
import yaml
import argparse
import wandb

from mlops.config import (
    WANDB_PROJECT,
    WANDB_API_KEY,
    DEFAULT_HYPERPARAMS,
    PROJECT_ROOT,
    load_config
)
from mlops.data_versioning import version_all_data
from mlops.train_apriori import train_apriori
from mlops.train_fpgrowth import train_fpgrowth
from mlops.train_eclat import train_eclat
from mlops.model_registry import promote_to_production


def run_preprocessing():
    """Run data preprocessing scripts."""
    print("\n" + "="*60)
    print("DATA PREPROCESSING")
    print("="*60)
    
    # Run extract_logs.py
    extract_script = os.path.join(PROJECT_ROOT, "cleanningData", "extract_logs.py")
    if os.path.exists(extract_script):
        print("\n[1/2] Running log extraction...")
        os.system(f"cd {PROJECT_ROOT} && python cleanningData/extract_logs.py")
    else:
        print("  Warning: extract_logs.py not found, skipping")
    
    # Run clean_extracted_data.py
    clean_script = os.path.join(PROJECT_ROOT, "cleanningData", "clean_extracted_data.py")
    if os.path.exists(clean_script):
        print("\n[2/2] Running data cleaning...")
        os.system(f"cd {PROJECT_ROOT} && python cleanningData/clean_extracted_data.py")
    else:
        print("  Warning: clean_extracted_data.py not found, skipping")
    
    print("\n✓ Preprocessing complete!")


def run_pipeline(
    run_preprocessing_step=False,
    version_data=True,
    algorithms=None,
    hyperparams=None,
    register_best=True
):
    """
    Run the complete MLOps pipeline.
    
    Parameters:
    - run_preprocessing_step: Whether to run data preprocessing
    - version_data: Whether to version data artifacts
    - algorithms: List of algorithms to train ['apriori', 'fpgrowth', 'eclat']
    - hyperparams: Dict of hyperparameters
    - register_best: Whether to register best model to production
    """
    print("\n" + "="*60)
    print("WEB USAGE MINING - MLOps PIPELINE")
    print("="*60)
    
    # Default algorithms
    if algorithms is None:
        algorithms = ["apriori", "fpgrowth", "eclat"]
    
    # Default hyperparams
    if hyperparams is None:
        hyperparams = DEFAULT_HYPERPARAMS.copy()
    
    # Step 1: Data Preprocessing (optional)
    if run_preprocessing_step:
        run_preprocessing()
    
    # Step 2: Data Versioning
    if version_data:
        print("\n" + "-"*40)
        print("STEP: Data Versioning")
        print("-"*40)
        version_all_data()
    
    # Step 3: Train algorithms
    print("\n" + "-"*40)
    print("STEP: Model Training")
    print("-"*40)
    
    results = {}
    training_funcs = {
        "apriori": train_apriori,
        "fpgrowth": train_fpgrowth,
        "eclat": train_eclat
    }
    
    for algo in algorithms:
        if algo in training_funcs:
            print(f"\nTraining {algo.upper()}...")
            rules = training_funcs[algo](
                min_support=hyperparams.get("min_support"),
                min_confidence=hyperparams.get("min_confidence"),
                min_lift=hyperparams.get("min_lift"),
                max_len=hyperparams.get("max_len")
            )
            results[algo] = {
                "num_rules": len(rules) if rules is not None else 0,
                "rules": rules
            }
    
    # Step 4: Register best model
    if register_best and results:
        print("\n" + "-"*40)
        print("STEP: Model Registration")
        print("-"*40)
        
        # Find best model by number of rules (or could use other metric)
        best_algo = max(results.keys(), key=lambda k: results[k]["num_rules"])
        print(f"\nBest model: {best_algo} with {results[best_algo]['num_rules']} rules")
        
        # Promote to production
        promote_to_production(best_algo, version="latest")
    
    # Final Summary
    print("\n" + "="*60)
    print("PIPELINE COMPLETE - SUMMARY")
    print("="*60)
    
    for algo, result in results.items():
        print(f"  {algo.upper()}: {result['num_rules']} rules generated")
    
    print(f"\n  View experiments at: https://wandb.ai/{WANDB_PROJECT}")
    print("="*60 + "\n")
    
    return results


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Web Usage Mining MLOps Pipeline"
    )
    parser.add_argument(
        "--preprocess", 
        action="store_true",
        help="Run data preprocessing before training"
    )
    parser.add_argument(
        "--no-version", 
        action="store_true",
        help="Skip data versioning"
    )
    parser.add_argument(
        "--algorithms",
        nargs="+",
        choices=["apriori", "fpgrowth", "eclat"],
        default=["apriori", "fpgrowth", "eclat"],
        help="Algorithms to train"
    )
    parser.add_argument(
        "--min-support",
        type=float,
        default=DEFAULT_HYPERPARAMS["min_support"],
        help="Minimum support threshold"
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=DEFAULT_HYPERPARAMS["min_confidence"],
        help="Minimum confidence threshold"
    )
    parser.add_argument(
        "--min-lift",
        type=float,
        default=DEFAULT_HYPERPARAMS["min_lift"],
        help="Minimum lift threshold"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to config YAML file"
    )
    
    args = parser.parse_args()
    
    # Load config from file if provided
    if args.config:
        config = load_config(args.config)
        hyperparams = config.get("training", {}).get("hyperparameters", {})
    else:
        hyperparams = {
            "min_support": args.min_support,
            "min_confidence": args.min_confidence,
            "min_lift": args.min_lift,
            "max_len": DEFAULT_HYPERPARAMS["max_len"]
        }
    
    # Run pipeline
    run_pipeline(
        run_preprocessing_step=args.preprocess,
        version_data=not args.no_version,
        algorithms=args.algorithms,
        hyperparams=hyperparams
    )


if __name__ == "__main__":
    main()
