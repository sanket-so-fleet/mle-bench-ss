# Data Leakage Detection

## Task

Analyze the dataset to identify features that may leak information about the target variable.

## Instructions

1. **Load the training data** from `/home/data/train.csv`

2. **Analyze each feature for potential leakage:**
   - **Target leakage**: Features derived from the target (e.g., "days_since_churn" when predicting churn)
   - **Temporal leakage**: Future information not available at prediction time
   - **Train-test leakage**: Features that differ systematically between train/test
   - **Proxy leakage**: Features highly correlated with target due to data collection process

3. **Red flags to look for:**
   - Features with suspiciously high correlation with target (>0.9)
   - Features containing "target", "label", "outcome" in name
   - Date features that might be after the event
   - ID-like features that encode target information
   - Aggregated features that include target in calculation

4. **Write your analysis** to `leakage_analysis.json`:

```json
{
  "features_analyzed": ["feature1", "feature2", "..."],
  "leaky_features": [
    {
      "feature": "days_until_churn",
      "leakage_type": "target_leakage",
      "evidence": "Correlation with target is 0.98, feature name suggests post-hoc calculation",
      "recommendation": "remove"
    }
  ],
  "safe_features": ["feature3", "feature4"],
  "reasoning_per_feature": {
    "feature1": "Safe - demographic data available at signup",
    "feature2": "Suspicious but likely okay - timestamp is before target event"
  },
  "recommended_action": "Remove days_until_churn before training"
}
```

## Grading Criteria

1. **Completeness** - All features analyzed
2. **Detection accuracy** - Found the leaky features (if any)
3. **False positive rate** - Didn't flag safe features as leaky
4. **Evidence quality** - Provided concrete evidence (correlations, patterns)
5. **Actionable recommendations** - Clear next steps

## Common Leakage Patterns

| Pattern | Example | Why It Leaks |
|---------|---------|--------------|
| Direct encoding | `is_churned` when predicting churn | Literally the target |
| Time travel | `purchase_after_ad` for ad conversion | Future info |
| Aggregation | `avg_rating` includes test samples | Train-test leak |
| ID encoding | `user_id` correlates with target | Memorization |
