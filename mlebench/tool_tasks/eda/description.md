# Exploratory Data Analysis Notebook

## Task

Create a comprehensive EDA notebook for the dataset.

## Instructions

1. **Create `eda.ipynb`** with the following sections:

### Required Sections

**1. Data Loading**
```python
import pandas as pd
train = pd.read_csv('/home/data/train.csv')
```

**2. Basic Statistics**
- Shape (rows, columns)
- Data types
- `df.describe()` for numeric columns
- `df.info()` for memory usage

**3. Missing Value Analysis**
- Count missing per column
- Visualize missingness patterns
- Note any columns with >50% missing

**4. Target/Label Distribution**
- Value counts for classification
- Histogram for regression
- Check for class imbalance

**5. Feature Exploration**
- Histograms for 3-5 key numeric features
- Bar plots for important categorical features
- Correlation heatmap (if applicable)

**6. Issues Identified**
- List any data quality issues found
- Potential problems for modeling

2. **Save plots** to `plots/` directory

3. **Write summary to `/home/submission/eda_analysis.json`:

```json
{
  "num_rows": 10000,
  "num_cols": 25,
  "target_column": "label",
  "target_type": "binary",
  "missing_columns": ["Age", "Cabin"],
  "high_missing": ["Cabin"],
  "class_distribution": {"0": 0.65, "1": 0.35},
  "numeric_features": ["age", "fare", "sibsp"],
  "categorical_features": ["sex", "embarked", "pclass"],
  "issues": [
    "Cabin has 77% missing values",
    "Age has 20% missing - needs imputation",
    "Some negative fares found (data error?)"
  ],
  "plots_saved": ["label_dist.png", "age_hist.png", "correlation.png"]
}
```

## Grading Criteria

1. **Notebook exists and runs** - No errors
2. **All sections present** - Data loading through issues
3. **Plots saved** - At least 3 visualizations
4. **Issues identified** - Found real problems in data
5. **Summary JSON complete** - All required fields

## Tips

- Use `matplotlib` or `seaborn` for plots
- Save figures with `plt.savefig('plots/name.png')`
- Be specific about issues - not just "data looks okay"
