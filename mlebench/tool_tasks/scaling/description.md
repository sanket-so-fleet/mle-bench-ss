# Feature Scaling Decisions

## Task

Determine if and how to scale features based on model type and data characteristics.

## Instructions

1. **Load the training data** from `/home/data/train.csv`

2. **Identify your model type:**
   | Model Type | Needs Scaling? |
   |------------|----------------|
   | Linear/Logistic Regression | Yes |
   | SVM | Yes (especially RBF kernel) |
   | KNN | Yes |
   | Neural Networks | Yes |
   | Decision Trees | No |
   | Random Forest | No |
   | XGBoost/LightGBM | No |

3. **Analyze feature distributions:**
   - Are there outliers?
   - Are scales very different across features?
   - Is data approximately normal?

4. **Choose scaling method:**
   - `none` - Tree-based models, no scaling needed
   - `standard` - StandardScaler: when data is ~normal, no major outliers
   - `minmax` - MinMaxScaler: when you need bounded [0,1] range
   - `robust` - RobustScaler: when outliers present
   - `normalizer` - When you care about direction, not magnitude

5. **Write your analysis to `/home/submission/scaling_analysis.json`:

```json
{
  "model_type": "logistic_regression",
  "feature_analysis": {
    "age": {"min": 0, "max": 80, "mean": 35, "std": 15, "has_outliers": false},
    "income": {"min": 0, "max": 1000000, "mean": 50000, "std": 80000, "has_outliers": true}
  },
  "scale_differences": "Large - age in [0,80], income in [0,1M]",
  "needs_scaling": true,
  "chosen_method": "robust",
  "reasoning": "Using logistic regression which requires scaling. Income has outliers (max 1M vs mean 50K), so RobustScaler is better than StandardScaler. It uses median and IQR which are robust to outliers.",
  "implementation_notes": "Fit scaler on train only, transform both train and test"
}
```

## Grading Criteria

1. **Correct model assessment** - Does model need scaling?
2. **Feature analysis** - Identified scale differences, outliers
3. **Method matches data** - Robust for outliers, standard for normal
4. **Implementation awareness** - Fit on train only

## Common Mistakes

- Scaling tree-based models (wastes time)
- Using StandardScaler with outliers
- Fitting scaler on full data before split (leakage)
- Forgetting to scale test data
