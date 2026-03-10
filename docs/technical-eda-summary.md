# Technical EDA Summary

## Dataset Snapshot
- Dataset: `data/construction_dataset.csv`
- Snapshot date: March 9, 2026
- Rows: `1300`
- Modeling features: `8`
- Target: `Risk_Level` (`Low`, `Medium`, `High`)

## Data Quality Checks

| Check | Result | Interpretation |
|---|---|---|
| Missing values | `0` across all columns | No null-imputation step was required |
| Duplicate rows | `0` | No duplicated training records were found |
| Duplicate `Task_ID` values | `0` | Identifier uniqueness is preserved |
| Numeric outliers by IQR rule | `0` across numeric columns | The dataset is already tightly bounded and normalized |

## Class Distribution

| Risk Level | Count | Share |
|---|---:|---:|
| Low | 660 | 50.77% |
| Medium | 377 | 29.00% |
| High | 263 | 20.23% |

The target is imbalanced, so macro F1 is a better model-selection metric than raw accuracy. Accuracy alone would over-reward models that favor the majority `Low` class.

## Descriptive Statistics

| Feature | Mean | Median | Std | Min | Max |
|---|---:|---:|---:|---:|---:|
| Task_Duration_Days | 43.44 | 43.00 | 25.72 | 1.00 | 89.00 |
| Labor_Required | 10.01 | 10.00 | 5.45 | 1.00 | 19.00 |
| Equipment_Units | 4.98 | 5.00 | 2.60 | 1.00 | 9.00 |
| Material_Cost_USD | 49525.11 | 49328.34 | 28409.87 | 1003.04 | 99956.21 |
| Start_Constraint | 14.77 | 15.00 | 8.59 | 0.00 | 29.00 |
| Resource_Constraint_Score | 0.59 | 0.59 | 0.23 | 0.20 | 1.00 |
| Site_Constraint_Score | 0.48 | 0.47 | 0.23 | 0.10 | 0.90 |
| Dependency_Count | 2.03 | 2.00 | 1.42 | 0.00 | 4.00 |

## Correlation and Separation Findings
- Pairwise feature correlations are weak. The largest absolute correlation in the dataset is about `0.07`.
- Weak feature correlation means multicollinearity is not a major problem.
- It also means the supervised learning task has limited separable signal in the current feature set.

Examples of very small class-level differences:

| Feature | High Mean | Low Mean | Medium Mean |
|---|---:|---:|---:|
| Task_Duration_Days | 43.86 | 43.46 | 43.10 |
| Resource_Constraint_Score | 0.58 | 0.59 | 0.60 |
| Dependency_Count | 2.00 | 2.00 | 2.12 |

These near-identical class means explain why the ML model should be positioned as advisory only. The dataset is clean, but the classes are not strongly separated by the available predictors.

## EDA Conclusions
- The main challenge is not data cleanliness; it is limited class signal.
- Macro F1 should be the lead model metric because the `High` risk minority class matters most for decision-making.
- The Monte Carlo engine remains the primary forecasting method, while ML adds task-level directional guidance.
