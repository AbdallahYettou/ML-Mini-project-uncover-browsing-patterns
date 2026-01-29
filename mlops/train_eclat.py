"""
ECLAT Algorithm Training with W&B Experiment Tracking

This module trains the ECLAT algorithm for association rule mining
with full experiment tracking using Weights & Biases.
"""

import os
import time
import pandas as pd
import wandb
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpmax, association_rules
from collections import defaultdict

from mlops.config import (
    WANDB_PROJECT,
    WANDB_API_KEY,
    DEFAULT_HYPERPARAMS,
    DATA_FILES,
    ECLAT_DIR,
    PROJECT_ROOT
)


def load_sessions(filepath):
    """Load session data from CSV file."""
    sessions = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                paths = [p.strip() for p in line.split(',') if p.strip()]
                if len(paths) >= 2:
                    sessions.append(paths)
    return sessions


def eclat_algorithm(transactions, min_support, max_len=10):
    """
    Custom ECLAT implementation using vertical data format.
    
    ECLAT (Equivalence Class Clustering and bottom-up Lattice Traversal)
    uses tidsets (transaction ID sets) for faster support counting.
    """
    # Build vertical database (item -> set of transaction indices)
    vertical_db = defaultdict(set)
    for tid, transaction in enumerate(transactions):
        for item in transaction:
            vertical_db[item].add(tid)
    
    n_transactions = len(transactions)
    min_count = min_support * n_transactions
    
    # Get frequent 1-itemsets
    frequent_itemsets = []
    items = sorted([item for item, tids in vertical_db.items() 
                   if len(tids) >= min_count])
    
    # Add 1-itemsets
    for item in items:
        support = len(vertical_db[item]) / n_transactions
        frequent_itemsets.append({
            'itemsets': frozenset([item]),
            'support': support
        })
    
    def eclat_recursive(prefix, items_tids, k):
        """Recursive ECLAT to find k+1 itemsets."""
        if k >= max_len:
            return
        
        items_list = list(items_tids.keys())
        for i, item1 in enumerate(items_list):
            tids1 = items_tids[item1]
            new_prefix = prefix | frozenset([item1])
            
            # Find extensions
            new_items_tids = {}
            for item2 in items_list[i+1:]:
                tids2 = items_tids[item2]
                new_tids = tids1 & tids2
                
                if len(new_tids) >= min_count:
                    new_items_tids[item2] = new_tids
                    # Found a frequent itemset
                    itemset = new_prefix | frozenset([item2])
                    support = len(new_tids) / n_transactions
                    frequent_itemsets.append({
                        'itemsets': itemset,
                        'support': support
                    })
            
            # Recurse
            if new_items_tids:
                eclat_recursive(new_prefix, new_items_tids, k + 1)
    
    # Build initial items_tids for 2-itemset generation
    items_tids = {item: vertical_db[item] for item in items}
    eclat_recursive(frozenset(), items_tids, 1)
    
    return pd.DataFrame(frequent_itemsets)


def train_eclat(
    min_support=None,
    min_confidence=None,
    min_lift=None,
    max_len=None,
    data_path=None,
    output_dir=None
):
    """
    Train ECLAT algorithm with W&B tracking.
    
    Parameters:
    - min_support: Minimum support threshold
    - min_confidence: Minimum confidence for rules
    - min_lift: Minimum lift for filtering rules
    - max_len: Maximum itemset length
    - data_path: Path to cleaned session data
    - output_dir: Directory to save output files
    
    Returns:
    - rules_df: DataFrame of association rules
    """
    # Use defaults if not specified
    min_support = min_support or DEFAULT_HYPERPARAMS["min_support"]
    min_confidence = min_confidence or DEFAULT_HYPERPARAMS["min_confidence"]
    min_lift = min_lift or DEFAULT_HYPERPARAMS["min_lift"]
    max_len = max_len or DEFAULT_HYPERPARAMS["max_len"]
    data_path = data_path or DATA_FILES["cleaned"]
    output_dir = output_dir or ECLAT_DIR
    
    # Initialize W&B
    wandb.login(key=WANDB_API_KEY)
    run = wandb.init(
        project=WANDB_PROJECT,
        job_type="training",
        name="eclat-training",
        config={
            "algorithm": "ECLAT",
            "min_support": min_support,
            "min_confidence": min_confidence,
            "min_lift": min_lift,
            "max_len": max_len,
            "data_path": data_path
        }
    )
    
    try:
        print("\n" + "="*60)
        print("ECLAT ALGORITHM TRAINING")
        print("="*60)
        
        # Track start time
        start_time = time.time()
        
        # Load data
        print("\n[1/5] Loading session data...")
        sessions = load_sessions(data_path)
        wandb.log({"data/num_sessions": len(sessions)})
        print(f"  Loaded {len(sessions)} sessions")
        
        # Count unique items
        unique_items = set()
        for session in sessions:
            unique_items.update(session)
        wandb.log({"data/num_unique_items": len(unique_items)})
        print(f"  Unique items: {len(unique_items)}")
        
        # Run ECLAT
        print(f"\n[2/5] Running ECLAT (min_support={min_support})...")
        frequent_itemsets = eclat_algorithm(sessions, min_support, max_len)
        wandb.log({"training/num_frequent_itemsets": len(frequent_itemsets)})
        print(f"  Found {len(frequent_itemsets)} frequent itemsets")
        
        # Save frequent itemsets
        os.makedirs(output_dir, exist_ok=True)
        itemsets_file = os.path.join(output_dir, "ECLAT_frequent_itemsets.csv")
        frequent_itemsets.to_csv(itemsets_file, index=False)
        
        # Generate rules
        print(f"\n[3/5] Generating rules (min_confidence={min_confidence})...")
        if len(frequent_itemsets) > 0:
            rules = association_rules(
                frequent_itemsets,
                metric="confidence",
                min_threshold=min_confidence
            )
            # Filter by lift
            rules = rules[rules['lift'] >= min_lift]
            rules = rules.sort_values('confidence', ascending=False)
        else:
            rules = pd.DataFrame()
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Log metrics
        metrics = {
            "training/num_rules": len(rules),
            "training/execution_time_sec": elapsed_time,
        }
        
        if len(rules) > 0:
            metrics.update({
                "metrics/avg_support": rules['support'].mean(),
                "metrics/avg_confidence": rules['confidence'].mean(),
                "metrics/avg_lift": rules['lift'].mean(),
                "metrics/max_confidence": rules['confidence'].max(),
                "metrics/max_lift": rules['lift'].max(),
            })
        
        wandb.log(metrics)
        print(f"\n[4/5] Generated {len(rules)} rules in {elapsed_time:.2f}s")
        
        # Log rule table
        if len(rules) > 0:
            # Convert frozensets to strings for W&B Table
            rules_for_table = rules.head(100).copy()
            rules_for_table['antecedents'] = rules_for_table['antecedents'].apply(lambda x: ', '.join(sorted(x)))
            rules_for_table['consequents'] = rules_for_table['consequents'].apply(lambda x: ', '.join(sorted(x)))
            rules_table = wandb.Table(
                dataframe=rules_for_table[['antecedents', 'consequents', 'support', 'confidence', 'lift']]
            )
            wandb.log({"rules/top_100_rules": rules_table})
        
        # Save rules to file
        rules_file = os.path.join(output_dir, "ECLAT_rules.csv")
        rules.to_csv(rules_file, index=False)
        print(f"  Saved rules to: {rules_file}")
        
        # Log as artifact
        artifact = wandb.Artifact(
            name="eclat-rules",
            type="model",
            description=f"ECLAT rules with support>={min_support}, confidence>={min_confidence}, lift>={min_lift}",
            metadata={
                "algorithm": "ECLAT",
                "num_rules": len(rules),
                "min_support": min_support,
                "min_confidence": min_confidence,
                "min_lift": min_lift,
                "execution_time": elapsed_time
            }
        )
        artifact.add_file(rules_file)
        artifact.add_file(itemsets_file)
        run.log_artifact(artifact)
        print("  Logged model artifact to W&B")
        
        print("\n" + "="*60)
        print("✓ ECLAT training complete!")
        print(f"  View run at: {run.url}")
        print("="*60 + "\n")
        
        return rules
        
    finally:
        run.finish()


if __name__ == "__main__":
    train_eclat()
