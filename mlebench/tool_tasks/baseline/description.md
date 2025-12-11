# Baseline Model Implementation

## Task

Create a solid baseline model with proper evaluation.

## Instructions

1. **Create `baseline.py`** that:

```python
"""Baseline model for [competition name]."""
import pandas as pd
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression  # or appropriate model
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# Load data
train = pd.read_csv('/home/data/train.csv')
X = train.drop(columns=['target'])
y = train['target']

# Create pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LogisticRegression())
])

# Cross-validation
scores = cross_val_score(pipeline, X, y, cv=5, scoring='accuracy')
print(f"CV Accuracy: {scores.mean():.4f} (+/- {scores.std()*2:.4f})")
```

2. **Requirements for `baseline.py`:**
   - Loads train.csv from /home/data/
   - Uses cross-validation (not just train/test split)
   - Prints validation metrics clearly
   - Handles basic preprocessing (scaling, encoding)
   - Uses an appropriate model for the task type

3. **Create `README.md`:**
```markdown
# Baseline Model

## How to Run
```bash
python baseline.py
```

## Model
- Type: Logistic Regression
- Features: All numeric columns, scaled
- CV: 5-fold stratified

## Results
- CV Accuracy: 0.82 (+/- 0.03)
```

4. **Save results** to `baseline_results.json`:
```json
{
  "model_type": "logistic_regression",
  "cv_folds": 5,
  "metrics": {
    "accuracy": {"mean": 0.82, "std": 0.015}
  },
  "features_used": 10,
  "preprocessing": ["standard_scaling"]
}
```

## Grading Criteria

1. **baseline.py exists and runs**
2. **Uses cross-validation** (not simple split)
3. **Prints metrics** to stdout
4. **README has instructions** to run the code
5. **Results saved** in JSON format

## Tips

- Start simple: LogisticRegression or RandomForest
- Use sklearn pipelines to avoid leakage
- Print both mean and std of CV scores
- Don't over-engineer - it's a baseline!
