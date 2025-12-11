# Missing Value Strategy

## Task

Analyze missing data patterns and choose an appropriate imputation strategy.

## Instructions

1. **Load the training data** from `/home/data/train.csv`

2. **Analyze missingness:**
   - Which columns have missing values?
   - What percentage is missing?
   - Is missingness random or systematic?

3. **Diagnose the missingness pattern:**
   - **MCAR** (Missing Completely At Random): Missingness unrelated to any variable
   - **MAR** (Missing At Random): Missingness depends on observed variables
   - **MNAR** (Missing Not At Random): Missingness depends on the missing value itself

4. **Choose a strategy:**
   | Strategy | When to Use |
   |----------|-------------|
   | `drop_rows` | Very few missing (<5%), MCAR |
   | `drop_cols` | Column mostly missing (>50%) |
   | `mean_impute` | Numeric, MCAR, symmetric distribution |
   | `median_impute` | Numeric, MCAR, skewed distribution |
   | `mode_impute` | Categorical |
   | `knn_impute` | MAR, similar samples have similar values |
   | `model_impute` | MAR, complex relationships |
   | `indicator_flag` | MNAR, missingness itself is informative |

5. **Write your analysis** to `missing_analysis.json`:

```json
{
  "missing_summary": {
    "Age": {"count": 177, "percent": 19.9},
    "Cabin": {"count": 687, "percent": 77.1}
  },
  "total_rows": 891,
  "columns_with_missing": ["Age", "Cabin", "Embarked"],
  "missingness_pattern": {
    "Age": "MAR",
    "Cabin": "MNAR",
    "Embarked": "MCAR"
  },
  "pattern_evidence": {
    "Age": "Missing age correlates with passenger class - higher classes have fewer missing",
    "Cabin": "Cabin info likely not recorded for cheaper tickets - missingness is informative",
    "Embarked": "Only 2 missing, appears random"
  },
  "chosen_strategy": {
    "Age": "median_impute",
    "Cabin": "indicator_flag",
    "Embarked": "mode_impute"
  },
  "reasoning": "Age is MAR (correlates with class) so median by class would be ideal. Cabin is MNAR - the absence of cabin info is informative about ticket class, so we add an indicator. Embarked has only 2 missing, use mode."
}
```

## Grading Criteria

1. **Correct missingness detection** - Found all columns with missing
2. **Pattern diagnosis** - Identified MCAR/MAR/MNAR correctly
3. **Strategy matches pattern** - Chose appropriate method for each pattern
4. **Evidence provided** - Explained how you determined the pattern

## Common Mistakes

- Using mean imputation on skewed data
- Dropping rows when missingness is informative (MNAR)
- Not adding indicator flags for MNAR
- Imputing before train/test split (causes leakage)
