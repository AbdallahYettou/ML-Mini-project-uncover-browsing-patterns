import wandb
from mlops.config import WANDB_PROJECT, WANDB_API_KEY

def verify_wandb():
    print(f"="*60)
    print(f"VERIFYING W&B PLATFORM CONTENT")
    print(f"="*60)
    
    print(f"Connecting to W&B Project: {WANDB_PROJECT}...")
    try:
        api = wandb.Api(api_key=WANDB_API_KEY)
        
        # 1. Verify Project Exists
        print(f"\n[1/3] Checking Project...")
        projects = api.projects()
        target_project = None
        for p in projects:
            if p.name == WANDB_PROJECT:
                target_project = p
                break
        
        if target_project:
            print(f"✅ Project found: {target_project.name}")
            print(f"   URL: {target_project.url}")
        else:
            print(f"❌ Project {WANDB_PROJECT} NOT found! Run pipeline first.")
            return

        # 2. Verify Runs
        print(f"\n[2/3] Checking Experiments (Runs)...")
        runs = api.runs(path=f"{target_project.entity}/{WANDB_PROJECT}")
        if len(runs) > 0:
            print(f"✅ Found {len(runs)} runs logged:")
            for run in runs:
                algo = run.config.get('algorithm', 'Unknown')
                job_type = run.job_type
                state = "🟢" if run.state == "finished" else "🟡" if run.state == "running" else "🔴"
                
                # Get key metric if available
                metric = ""
                if 'training/num_rules' in run.summary:
                    metric = f"| Rules: {run.summary['training/num_rules']}"
                elif 'session/total_predictions' in run.summary:
                    metric = f"| Preds: {run.summary['session/total_predictions']}"
                    
                print(f"   {state} {run.name:<25} [{job_type:<15}] {algo:<10} {metric}")
        else:
            print("❌ No runs found!")

        # 3. Verify Artifacts
        print(f"\n[3/3] Checking Artifacts (Data & Models)...")
        artifact_types = api.artifact_types(project=WANDB_PROJECT)
        
        found_data = False
        found_models = False
        
        for at in artifact_types:
            print(f"   📂 Type: {at.name}")
            for collection in at.collections():
                print(f"      📦 {collection.name}")
                
                if at.name in ['raw-data', 'extracted-data', 'processed-data']:
                    found_data = True
                if at.name == 'model':
                    found_models = True

        print("-" * 60)
        
        if found_data:
            print("✅ Data Versioning: VERIFIED (Raw/Extracted/Cleaned artifacts found)")
        else:
            print("⚠️ Data Versioning: NOT FOUND")
            
        if found_models:
            print("✅ Model Registry:  VERIFIED (Model artifacts found)")
        else:
            print("⚠️ Model Registry:  NOT FOUND")
            
        if len(runs) > 0:
            print("✅ Experiment Tracking: VERIFIED (Runs found)")
        else:
            print("⚠️ Experiment Tracking: NOT FOUND")

    except Exception as e:
        print(f"❌ Error verifying W&B: {e}")

if __name__ == "__main__":
    verify_wandb()
