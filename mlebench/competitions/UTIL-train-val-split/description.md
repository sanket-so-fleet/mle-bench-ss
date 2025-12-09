# Train–Validation Split Task (Dummy Version)

You are given a labeled dataset `raw.csv` containing:

- `id`: unique identifier
- `y`: binary class label

Your goal (in a real agent scenario) would be to:

1. Create a Python module `split_data.py` in the submission directory.
2. Implement a function `make_split(raw_path: str, out_dir: str)` that:
   - reads `raw.csv`
   - produces `train.csv` and `val.csv` in `out_dir`
   - places approximately 80% of rows in `train.csv`
   - ensures no overlap between train and validation sets

This is a **dummy task** for testing MLE-bench integration.  
The dummy agent will not produce correct splits — this is expected.