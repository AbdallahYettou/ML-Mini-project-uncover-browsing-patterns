"""
Model Monitoring Module

Tracks predictions and data distribution in production for drift detection.
"""

import os
import time
from datetime import datetime
import wandb
import pandas as pd
from collections import Counter

from mlops.config import (
    WANDB_PROJECT,
    WANDB_API_KEY
)


class ProductionMonitor:
    """
    Monitor for production model performance and data drift.
    
    Usage:
        monitor = ProductionMonitor()
        monitor.start_session()
        
        # Log each prediction
        monitor.log_prediction(
            user_paths=['/shuttle', '/history'],
            predictions=[('/missions', 0.85), ('/news', 0.72)],
            algorithm='apriori'
        )
        
        monitor.end_session()
    """
    
    def __init__(self, buffer_size=100):
        """
        Initialize the production monitor.
        
        Parameters:
        - buffer_size: Number of predictions to buffer before logging
        """
        self.buffer_size = buffer_size
        self.prediction_buffer = []
        self.run = None
        self.session_start = None
        
        # Statistics
        self.total_predictions = 0
        self.path_counter = Counter()
        self.algorithm_counter = Counter()
        
    def start_session(self, session_name=None):
        """Start a monitoring session."""
        wandb.login(key=WANDB_API_KEY)
        
        if session_name is None:
            session_name = f"monitoring-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        self.run = wandb.init(
            project=WANDB_PROJECT,
            job_type="production-monitoring",
            name=session_name,
            config={"buffer_size": self.buffer_size}
        )
        self.session_start = time.time()
        print(f"✓ Started monitoring session: {session_name}")
        
    def log_prediction(self, user_paths, predictions, algorithm, metadata=None):
        """
        Log a prediction to the monitoring buffer.
        
        Parameters:
        - user_paths: List of paths the user visited
        - predictions: List of (predicted_path, confidence) tuples
        - algorithm: Algorithm used for prediction
        - metadata: Optional dict of additional metadata
        """
        if self.run is None:
            # Auto-start session if not started
            self.start_session()
        
        timestamp = datetime.now().isoformat()
        
        # Update statistics
        self.total_predictions += 1
        self.path_counter.update(user_paths)
        self.algorithm_counter[algorithm] += 1
        
        # Create prediction record
        record = {
            "timestamp": timestamp,
            "user_paths": ",".join(user_paths),
            "num_input_paths": len(user_paths),
            "predictions": str(predictions[:5]),  # Top 5 predictions
            "num_predictions": len(predictions),
            "top_prediction": predictions[0][0] if predictions else None,
            "top_confidence": predictions[0][1] if predictions else 0,
            "algorithm": algorithm
        }
        
        if metadata:
            record.update(metadata)
        
        self.prediction_buffer.append(record)
        
        # Flush buffer if full
        if len(self.prediction_buffer) >= self.buffer_size:
            self._flush_buffer()
    
    def _flush_buffer(self):
        """Flush the prediction buffer to W&B."""
        if not self.prediction_buffer or self.run is None:
            return
        
        # Create table from buffer
        df = pd.DataFrame(self.prediction_buffer)
        table = wandb.Table(dataframe=df)
        self.run.log({"predictions/batch": table})
        
        # Log aggregate metrics
        self.run.log({
            "monitoring/total_predictions": self.total_predictions,
            "monitoring/batch_size": len(self.prediction_buffer),
            "monitoring/avg_confidence": df['top_confidence'].mean() if 'top_confidence' in df else 0,
            "monitoring/avg_input_paths": df['num_input_paths'].mean() if 'num_input_paths' in df else 0
        })
        
        # Clear buffer
        self.prediction_buffer = []
        print(f"  Flushed {len(df)} predictions to W&B")
    
    def log_input_distribution(self):
        """Log the distribution of input paths."""
        if self.run is None:
            return
        
        # Create histogram of most common paths
        most_common = self.path_counter.most_common(50)
        if most_common:
            paths, counts = zip(*most_common)
            table = wandb.Table(
                data=[[p, c] for p, c in most_common],
                columns=["path", "count"]
            )
            self.run.log({"monitoring/path_distribution": table})
    
    def get_statistics(self):
        """Get current monitoring statistics."""
        return {
            "total_predictions": self.total_predictions,
            "unique_paths": len(self.path_counter),
            "top_paths": self.path_counter.most_common(10),
            "algorithm_usage": dict(self.algorithm_counter),
            "session_duration": time.time() - self.session_start if self.session_start else 0
        }
    
    def end_session(self):
        """End the monitoring session."""
        if self.run is None:
            return
        
        # Flush remaining predictions
        self._flush_buffer()
        
        # Log final statistics
        self.log_input_distribution()
        
        stats = self.get_statistics()
        self.run.log({
            "session/total_predictions": stats["total_predictions"],
            "session/unique_paths": stats["unique_paths"],
            "session/duration_sec": stats["session_duration"]
        })
        
        # Log algorithm usage
        for algo, count in stats["algorithm_usage"].items():
            self.run.log({f"session/algorithm_{algo}_count": count})
        
        print(f"\n✓ Monitoring session ended")
        print(f"  Total predictions: {stats['total_predictions']}")
        print(f"  Unique paths seen: {stats['unique_paths']}")
        print(f"  Duration: {stats['session_duration']:.1f}s")
        
        self.run.finish()
        self.run = None


# Global monitor instance for easy access
_monitor = None


def get_monitor():
    """Get or create the global monitor instance."""
    global _monitor
    if _monitor is None:
        _monitor = ProductionMonitor()
    return _monitor


def log_prediction(user_paths, predictions, algorithm, metadata=None):
    """
    Convenience function to log a prediction using the global monitor.
    """
    monitor = get_monitor()
    monitor.log_prediction(user_paths, predictions, algorithm, metadata)


if __name__ == "__main__":
    # Demo usage
    print("Production Monitoring Demo")
    print("=" * 40)
    
    monitor = ProductionMonitor(buffer_size=5)
    monitor.start_session("demo-session")
    
    # Simulate some predictions
    demo_predictions = [
        (['/shuttle', '/history'], [('/missions', 0.85), ('/news', 0.65)], 'apriori'),
        (['/news', '/press'], [('/history', 0.72), ('/images', 0.58)], 'fpgrowth'),
        (['/missions', '/sts-70'], [('/countdown', 0.91), ('/shuttle', 0.67)], 'eclat'),
    ]
    
    for paths, preds, algo in demo_predictions:
        monitor.log_prediction(paths, preds, algo)
        time.sleep(0.5)
    
    print("\nStatistics:", monitor.get_statistics())
    monitor.end_session()
