# Model Comparison Summary

## Evaluation Setup
- Dataset: `data/construction_dataset.csv`
- Split: stratified `80/20` train/test
- Seed: `42`
- Selection metric: cross-validated macro F1
- Reason for metric choice: macro F1 gives balanced weight to `Low`, `Medium`, and `High` classes instead of over-valuing the majority class

## Baseline
- Baseline model: `DummyClassifier(strategy="most_frequent")`
- Baseline accuracy: `0.5077`
- Baseline macro F1: `0.2245`

The baseline wins on raw accuracy because the dataset is imbalanced, but it performs poorly once all three classes matter equally.

## Candidate Models Tried

| Model | Test Accuracy | Test Macro F1 | Test Weighted F1 | CV Macro F1 Mean | CV Macro F1 Std |
|---|---:|---:|---:|---:|---:|
| HistGradientBoosting | 0.3962 | 0.3077 | 0.3744 | 0.3028 | 0.0153 |
| ExtraTrees | 0.4231 | 0.2897 | 0.3749 | 0.2803 | 0.0168 |
| LogisticRegression | 0.3346 | 0.3304 | 0.3419 | 0.2752 | 0.0121 |
| RandomForest | 0.4346 | 0.2643 | 0.3585 | 0.2737 | 0.0039 |

## Selected Advisory Model
- Selected model: `HistGradientBoosting`
- Saved version: `v1-advisory-multimodel`
- Selection rule: highest cross-validated macro F1

## Why This Model Was Chosen
- `RandomForest` had the best raw accuracy, but weaker macro F1.
- `LogisticRegression` had the strongest single-split macro F1, but weaker cross-validation stability.
- `HistGradientBoosting` produced the best cross-validated macro F1, so it was the most defensible choice for balanced multiclass performance on this dataset snapshot.

## Interpretation For The Capstone
- The classifier is useful for advisory task-level scoring.
- The model is not strong enough to replace the simulation engine.
- This supports the current product positioning: Monte Carlo is the main forecasting engine; ML is a secondary decision-support signal.

## Artifact Links
- Training script: `scripts/train_risk_model.py`
- Saved metrics: `models/risk_model_metrics.json`
- Saved model: `models/risk_classifier.joblib`
