# Evaluation Metrics & Plots

## Task

Add comprehensive evaluation to a model that only prints training loss.

## Scenario

You're given a training script that only prints loss. Your job is to add proper evaluation.

## Instructions

1. **Create `evaluate.py`** that:

```python
"""Comprehensive model evaluation."""
import json
import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    roc_curve, precision_recall_curve
)
import matplotlib.pyplot as plt

def evaluate_model(y_true, y_pred, y_prob=None):
    """Compute all relevant metrics."""
    results = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, average='weighted'),
        'recall': recall_score(y_true, y_pred, average='weighted'),
        'f1': f1_score(y_true, y_pred, average='weighted'),
    }
    
    if y_prob is not None:
        results['auc'] = roc_auc_score(y_true, y_prob)
    
    return results

def plot_confusion_matrix(y_true, y_pred, save_path='plots/confusion_matrix.png'):
    """Plot and save confusion matrix."""
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    plt.imshow(cm, cmap='Blues')
    plt.colorbar()
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.savefig(save_path)
    plt.close()

def plot_roc_curve(y_true, y_prob, save_path='plots/roc_curve.png'):
    """Plot and save ROC curve."""
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    auc = roc_auc_score(y_true, y_prob)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, label=f'AUC = {auc:.3f}')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend()
    plt.savefig(save_path)
    plt.close()
```

2. **Save plots** to `plots/`:
   - `confusion_matrix.png`
   - `roc_curve.png` (for binary classification)
   - `precision_recall_curve.png`

3. **Create `report.md`**:
```markdown
# Model Evaluation Report

## Metrics Summary
| Metric | Value |
|--------|-------|
| Accuracy | 0.85 |
| Precision | 0.83 |
| Recall | 0.87 |
| F1 Score | 0.85 |
| AUC | 0.91 |

## Confusion Matrix
![Confusion Matrix](plots/confusion_matrix.png)

## ROC Curve
![ROC Curve](plots/roc_curve.png)

## Observations
- Model performs well on majority class
- Some confusion between classes X and Y
- Consider threshold tuning for better precision
```

4. **Save results** to `evaluation_results.json`

## Grading Criteria

1. **evaluate.py exists** with metric functions
2. **Multiple metrics computed** (not just accuracy)
3. **Plots saved** (at least confusion matrix)
4. **report.md** summarizes findings
5. **JSON results** for programmatic access
