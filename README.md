# Web Usage Mining Mini Project - MLOps Edition

This project implements web usage mining techniques with **complete MLOps lifecycle** using Weights & Biases (W&B). It analyzes NASA HTTP server access logs using association rule mining algorithms to discover and predict user browsing patterns.

## MLOps Features

- **Data Versioning**: Track dataset versions with W&B Artifacts
- **Experiment Tracking**: Log hyperparameters, metrics, and visualizations
- **Model Registry**: Version and deploy trained models
- **Pipeline Automation**: Reproducible end-to-end training
- **Production Monitoring**: Track predictions and data drift

## Project Structure

```
MinProject/
├── mlops/                          # MLOps package
│   ├── __init__.py
│   ├── config.py                   # W&B and project configuration
│   ├── data_versioning.py          # Dataset versioning with artifacts
│   ├── train_apriori.py            # Apriori training with tracking
│   ├── train_fpgrowth.py           # FP-Growth training with tracking
│   ├── train_eclat.py              # ECLAT training with tracking
│   ├── pipeline.py                 # Automated training pipeline
│   ├── model_registry.py           # Model versioning and deployment
│   └── monitoring.py               # Production monitoring
├── cleanningData/                  # Data preprocessing scripts
│   ├── extract_logs.py             # Raw log extraction
│   └── clean_extracted_data.py     # Data cleaning and normalization
├── usedAlgorithme/                 # Original algorithm notebooks
│   ├── apriori.ipynb
│   ├── fp_growth.ipynb
│   └── ECLAT.ipynb
├── Data/                           # Datasets and model outputs
│   ├── Logs/                       # Raw NASA access logs
│   ├── extractedAndcleanedData/    # Processed datasets
│   ├── apriori/                    # Apriori model outputs
│   ├── fp_growth/                  # FP-Growth model outputs
│   └── ECLAT/                      # ECLAT model outputs
├── app.py                          # Streamlit dashboard
├── config.yaml                     # Pipeline configuration
└── requirements.txt                # Python dependencies
```

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure W&B (already configured in `mlops/config.py`):
   ```bash
   wandb login
   ```

## MLOps Workflow

### 1. Data Versioning

Version your datasets as W&B artifacts:

```bash
python -m mlops.data_versioning
```

This creates versioned snapshots of:
- Raw logs (referenced)
- Extracted sessions
- Cleaned sessions

### 2. Run Training Pipeline

Execute the full pipeline with all algorithms:

```bash
python -m mlops.pipeline
```

With custom hyperparameters:

```bash
python -m mlops.pipeline --min-support 0.02 --min-confidence 0.6
```

Run specific algorithm:

```bash
python -m mlops.pipeline --algorithms apriori
```

### 3. Train Individual Algorithms

```bash
# Apriori
python -m mlops.train_apriori

# FP-Growth  
python -m mlops.train_fpgrowth

# ECLAT
python -m mlops.train_eclat
```

### 4. View Experiments

Visit your W&B dashboard to see:
- Experiment comparisons
- Hyperparameter tuning results
- Metric visualizations
- Model artifacts

### 5. Promote Model to Production

```python
from mlops.model_registry import promote_to_production
promote_to_production('apriori', version='latest')
```

### 6. Run Dashboard

```bash
streamlit run app.py
```

## Configuration

Edit `config.yaml` to customize:

```yaml
wandb:
  project: "web-usage-mining-mlops"

training:
  algorithms:
    - apriori
    - fpgrowth
    - eclat
  hyperparameters:
    min_support: 0.01
    min_confidence: 0.5
    min_lift: 1.0
```

## Algorithms

| Algorithm | Description |
|-----------|-------------|
| **Apriori** | Classic bottom-up frequent itemset mining |
| **FP-Growth** | Pattern growth approach without candidate generation |
| **ECLAT** | Vertical data format with set intersection |

## W&B Dashboard

After running experiments, view your MLOps dashboard at:
`https://wandb.ai/<your-entity>/web-usage-mining-mlops`

Features available:
- **Runs**: Compare experiment metrics
- **Artifacts**: Browse versioned data and models
- **Charts**: Visualize training progress
- **Tables**: Explore generated rules

## License

This project is for educational purposes - ESI-SBA SEDS Module.
