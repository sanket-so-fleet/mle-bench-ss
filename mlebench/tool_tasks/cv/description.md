# Cross-Validation Strategy Selection

## Task

Analyze the dataset and determine the appropriate cross-validation strategy.

## Instructions

1. **Load and analyze the training data** from `/home/data/train.csv`
2. **Check for these data characteristics:**
   - Is there temporal structure? (date/time columns, sequential IDs)
   - Are there groups that shouldn't be split? (user IDs, patient IDs, etc.)
   - Is the target variable imbalanced?
   - How large is the dataset?

3. **Choose the appropriate CV strategy:**
   - `kfold` - Standard k-fold for i.i.d. data
   - `stratified` - Stratified k-fold for imbalanced classification
   - `timeseries` - TimeSeriesSplit for temporal data (no future leakage)
   - `group` - GroupKFold when samples from same group must stay together
   - `leave_one_out` - For very small datasets

4. **Write your analysis to `/home/submission/cv_analysis.json`:

```json
{
  "data_characteristics": {
    "num_rows": 10000,
    "num_cols": 15,
    "target_column": "label",
    "target_type": "binary",
    "temporal_columns": [],
    "group_columns": ["user_id"],
    "class_distribution": {"0": 0.7, "1": 0.3}
  },
  "has_temporal_structure": false,
  "has_groups": true,
  "is_imbalanced": false,
  "recommended_strategy": "group",
  "recommended_n_splits": 5,
  "reasoning": "Dataset contains user_id which suggests samples from the same user should not appear in both train and validation. Using GroupKFold to prevent data leakage from user behavior patterns."
}
```

## Grading Criteria

Your submission will be graded on:
1. **Analysis completeness** - All required fields present
2. **Correct diagnosis** - Did you identify temporal/group/imbalance characteristics?
3. **Strategy matches data** - Does your choice fit the data characteristics?
4. **Reasoning quality** - Did you explain why?

## Common Mistakes

- Using standard k-fold on time-series data (causes future leakage)
- Splitting user data across train/val (causes user behavior leakage)
- Not stratifying when classes are imbalanced
- Using LOO on large datasets (computationally wasteful)
