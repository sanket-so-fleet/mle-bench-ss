# Class Imbalance Handling

## Task

Analyze class distribution and determine if/how to handle class imbalance.

## Instructions

1. **Load the training data** from `/home/data/train.csv`

2. **Calculate class distribution:**
   - Count samples per class
   - Calculate imbalance ratio (majority / minority)
   - Visualize distribution

3. **Determine if imbalanced:**
   | Ratio | Severity | Action Needed |
   |-------|----------|---------------|
   | < 3:1 | Balanced | Usually none |
   | 3:1 - 10:1 | Moderate | Consider handling |
   | > 10:1 | Severe | Definitely handle |
   | > 100:1 | Extreme | Special techniques |

4. **Choose a strategy:**
   - `none` - Classes balanced, no action needed
   - `class_weights` - Weight minority class higher in loss
   - `oversample` - SMOTE or random oversampling of minority
   - `undersample` - Random undersampling of majority
   - `threshold` - Adjust classification threshold
   - `combined` - Multiple strategies together

5. **Write your analysis** to `imbalance_analysis.json`:

```json
{
  "class_distribution": {
    "0": 9000,
    "1": 1000
  },
  "class_percentages": {
    "0": 0.90,
    "1": 0.10
  },
  "imbalance_ratio": 9.0,
  "is_imbalanced": true,
  "severity": "moderate",
  "chosen_strategy": "class_weights",
  "reasoning": "With a 9:1 ratio, the model may ignore the minority class. Using class weights is preferred over SMOTE here because the dataset is tabular with mixed feature types. Setting class_weight='balanced' in sklearn will automatically adjust.",
  "implementation_notes": "Use class_weight='balanced' in LogisticRegression/RandomForest, or compute weights as n_samples / (n_classes * n_samples_per_class)"
}
```

## Grading Criteria

1. **Correct ratio calculation** - Math is right
2. **Appropriate severity assessment** - Matches the ratio
3. **Strategy matches severity** - Don't oversample balanced data
4. **Reasoning quality** - Explains why this strategy

## Common Mistakes

- Oversampling before train/test split (causes leakage)
- Using SMOTE on very high-dimensional data
- Ignoring severe imbalance entirely
- Over-engineering balanced datasets
