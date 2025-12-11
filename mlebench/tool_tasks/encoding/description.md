# Categorical Encoding Choices

## Task

Analyze categorical features and choose appropriate encoding methods.

## Instructions

1. **Load the training data** from `/home/data/train.csv`

2. **Identify categorical columns:**
   - Object/string dtype columns
   - Integer columns that are actually categories
   - Check cardinality (number of unique values)

3. **Choose encoding based on cardinality:**
   | Cardinality | Recommended Encoding |
   |-------------|---------------------|
   | 2 (binary) | Label encoding or one-hot |
   | 3-10 (low) | One-hot encoding |
   | 10-100 (medium) | Target or frequency encoding |
   | 100+ (high) | Target, frequency, or hash encoding |

4. **Consider model type:**
   - **Tree models**: Can use label encoding directly
   - **Linear models**: Need one-hot or target encoding
   - **Neural networks**: Embeddings for high cardinality

5. **Watch for leakage:**
   - Target encoding must be done with CV to prevent leakage
   - Fit encoder on train only

6. **Write your analysis** to `encoding_analysis.json`:

```json
{
  "categorical_columns": {
    "city": {"cardinality": 500, "dtype": "object"},
    "gender": {"cardinality": 2, "dtype": "object"},
    "category": {"cardinality": 15, "dtype": "object"}
  },
  "encoding_choices": {
    "city": "target",
    "gender": "onehot",
    "category": "onehot"
  },
  "reasoning": {
    "city": "High cardinality (500) - one-hot would create 500 columns. Target encoding with CV fold to prevent leakage.",
    "gender": "Binary - simple one-hot or label encoding works.",
    "category": "Low cardinality (15) - one-hot is fine, creates 15 columns."
  },
  "leakage_prevention": "Using sklearn's TargetEncoder with cv=5 for city column",
  "model_type": "xgboost"
}
```

## Grading Criteria

1. **Found all categoricals** - Didn't miss any
2. **Cardinality awareness** - Checked unique values
3. **Encoding matches cardinality** - No one-hot for 1000 categories
4. **Leakage awareness** - Target encoding done safely

## Common Mistakes

- One-hot encoding 10,000+ categories (explosion)
- Target encoding without CV (severe leakage)
- Label encoding ordinal data incorrectly
- Forgetting to handle unseen categories in test
