from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from joblib import dump
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


TARGET_COLUMN = "Risk_Level"
ID_COLUMN = "Task_ID"
FEATURE_COLUMNS = [
    "Task_Duration_Days",
    "Labor_Required",
    "Equipment_Units",
    "Material_Cost_USD",
    "Start_Constraint",
    "Resource_Constraint_Score",
    "Site_Constraint_Score",
    "Dependency_Count",
]


@dataclass(frozen=True)
class CandidateResult:
    name: str
    test_accuracy: float
    test_macro_f1: float
    test_weighted_f1: float
    cv_macro_f1_mean: float
    cv_macro_f1_std: float
    classification_report: dict[str, Any]
    confusion_matrix: list[list[int]]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train certAIn Project Intelligence risk classifier and save model + metrics metadata."
    )
    parser.add_argument(
        "--dataset",
        default="data/construction_dataset.csv",
        help="Path to the training CSV dataset.",
    )
    parser.add_argument(
        "--model-out",
        default="models/risk_classifier.joblib",
        help="Path to output model artifact.",
    )
    parser.add_argument(
        "--metrics-out",
        default="models/risk_model_metrics.json",
        help="Path to output metrics JSON.",
    )
    parser.add_argument(
        "--model-version",
        default="",
        help="Optional model version override (default: generated timestamp-based version).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible split and model training.",
    )
    return parser.parse_args()


def _sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(8192)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _validate_dataset(df: pd.DataFrame) -> None:
    required_columns = [ID_COLUMN, TARGET_COLUMN, *FEATURE_COLUMNS]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Dataset missing required columns: {missing}")
    if df[TARGET_COLUMN].nunique() < 2:
        raise ValueError("Target column must contain at least 2 classes.")


def _build_candidate_models(seed: int) -> dict[str, Pipeline]:
    scaled_numeric = ColumnTransformer(
        [("numeric", StandardScaler(), FEATURE_COLUMNS)],
        remainder="drop",
    )
    return {
        "logistic_regression": Pipeline(
            steps=[
                ("scaler", scaled_numeric),
                (
                    "classifier",
                    LogisticRegression(
                        max_iter=2000,
                        class_weight="balanced",
                        solver="lbfgs",
                    ),
                ),
            ]
        ),
        "random_forest": Pipeline(
            steps=[
                (
                    "classifier",
                    RandomForestClassifier(
                        n_estimators=400,
                        max_depth=None,
                        min_samples_leaf=2,
                        class_weight="balanced",
                        random_state=seed,
                        n_jobs=-1,
                    ),
                )
            ]
        ),
        "extra_trees": Pipeline(
            steps=[
                (
                    "classifier",
                    ExtraTreesClassifier(
                        n_estimators=500,
                        max_depth=None,
                        min_samples_leaf=2,
                        class_weight="balanced",
                        random_state=seed,
                        n_jobs=-1,
                    ),
                )
            ]
        ),
        "hist_gradient_boosting": Pipeline(
            steps=[
                (
                    "classifier",
                    HistGradientBoostingClassifier(
                        learning_rate=0.06,
                        max_depth=6,
                        max_iter=250,
                        random_state=seed,
                    ),
                )
            ]
        ),
    }


def _cross_val_macro_f1(
    model: Pipeline,
    X: pd.DataFrame,
    y: pd.Series,
    cv: StratifiedKFold,
) -> np.ndarray:
    try:
        return cross_val_score(model, X, y, cv=cv, scoring="f1_macro", n_jobs=-1)
    except Exception as exc:  # noqa: BLE001
        print(f"Parallel CV failed ({type(exc).__name__}: {exc}). Retrying with n_jobs=1.")
        return cross_val_score(model, X, y, cv=cv, scoring="f1_macro", n_jobs=1)


def _evaluate_candidate(
    name: str,
    model: Pipeline,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    X: pd.DataFrame,
    y: pd.Series,
    cv: StratifiedKFold,
) -> CandidateResult:
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    cv_scores = _cross_val_macro_f1(model, X, y, cv)
    labels = sorted(str(item) for item in y.unique())
    confusion = confusion_matrix(y_test, predictions, labels=labels)
    report = classification_report(
        y_test,
        predictions,
        labels=labels,
        output_dict=True,
        zero_division=0,
    )
    return CandidateResult(
        name=name,
        test_accuracy=float(accuracy_score(y_test, predictions)),
        test_macro_f1=float(f1_score(y_test, predictions, average="macro")),
        test_weighted_f1=float(f1_score(y_test, predictions, average="weighted")),
        cv_macro_f1_mean=float(cv_scores.mean()),
        cv_macro_f1_std=float(cv_scores.std()),
        classification_report=report,
        confusion_matrix=[[int(value) for value in row] for row in confusion.tolist()],
    )


def _compute_feature_importance(
    model: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    seed: int,
) -> pd.DataFrame:
    estimator = model.named_steps.get("classifier", model)

    if hasattr(estimator, "feature_importances_"):
        importances = np.asarray(estimator.feature_importances_, dtype=float)
    elif hasattr(estimator, "coef_"):
        coefficients = np.asarray(estimator.coef_, dtype=float)
        importances = np.mean(np.abs(coefficients), axis=0)
    else:
        permutation = permutation_importance(
            model,
            X_test,
            y_test,
            scoring="f1_macro",
            n_repeats=15,
            random_state=seed,
            n_jobs=1,
        )
        importances = np.asarray(permutation.importances_mean, dtype=float)

    return pd.DataFrame(
        {"feature": FEATURE_COLUMNS, "importance": importances}
    ).sort_values("importance", ascending=False)


def main() -> None:
    args = _parse_args()

    dataset_path = Path(args.dataset)
    model_out = Path(args.model_out)
    metrics_out = Path(args.metrics_out)

    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    model_out.parent.mkdir(parents=True, exist_ok=True)
    metrics_out.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(dataset_path)
    _validate_dataset(df)

    X = df[FEATURE_COLUMNS].copy()
    y = df[TARGET_COLUMN].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=args.seed,
        stratify=y,
    )

    baseline = DummyClassifier(strategy="most_frequent")
    baseline.fit(X_train, y_train)
    baseline_pred = baseline.predict(X_test)
    baseline_acc = accuracy_score(y_test, baseline_pred)
    baseline_f1_macro = f1_score(y_test, baseline_pred, average="macro")

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=args.seed)
    candidate_models = _build_candidate_models(args.seed)
    candidate_results: list[CandidateResult] = []
    for name, model in candidate_models.items():
        result = _evaluate_candidate(
            name=name,
            model=model,
            X_train=X_train,
            X_test=X_test,
            y_train=y_train,
            y_test=y_test,
            X=X,
            y=y,
            cv=cv,
        )
        candidate_results.append(result)

    candidate_results.sort(
        key=lambda item: (
            item.cv_macro_f1_mean,
            item.test_macro_f1,
            item.test_accuracy,
        ),
        reverse=True,
    )
    selected_result = candidate_results[0]
    selected_model = candidate_models[selected_result.name]
    selected_model.fit(X_train, y_train)
    final_predictions = selected_model.predict(X_test)
    final_acc = accuracy_score(y_test, final_predictions)
    final_f1_macro = f1_score(y_test, final_predictions, average="macro")
    importance_df = _compute_feature_importance(selected_model, X_test, y_test, args.seed)

    dump(selected_model, model_out)

    trained_at = datetime.now(tz=UTC).isoformat()
    default_version = datetime.now(tz=UTC).strftime("v%Y.%m.%d.%H%M")
    model_version = args.model_version or default_version
    dataset_hash = _sha256_of_file(dataset_path)

    payload = {
        "model_version": model_version,
        "trained_at_utc": trained_at,
        "dataset_path": str(dataset_path.resolve()),
        "dataset_sha256": dataset_hash,
        "n_rows": int(df.shape[0]),
        "n_features": int(len(FEATURE_COLUMNS)),
        "feature_columns": FEATURE_COLUMNS,
        "target_column": TARGET_COLUMN,
        "seed": int(args.seed),
        "selection_metric": "cv_macro_f1_mean",
        "selection_reason": (
            "Winner selected by highest cross-validated macro F1 so minority risk classes "
            "matter alongside overall accuracy."
        ),
        "selected_model_name": selected_result.name,
        "baseline_accuracy": float(baseline_acc),
        "baseline_macro_f1": float(baseline_f1_macro),
        "final_accuracy": float(final_acc),
        "final_macro_f1": float(final_f1_macro),
        "cv_macro_f1_mean": float(selected_result.cv_macro_f1_mean),
        "cv_macro_f1_std": float(selected_result.cv_macro_f1_std),
        "classification_report": selected_result.classification_report,
        "confusion_matrix": {
            "labels": sorted(str(item) for item in y.unique()),
            "values": selected_result.confusion_matrix,
        },
        "feature_importance": importance_df.to_dict(orient="records"),
        "model_comparison": [
            {
                "model_name": item.name,
                "test_accuracy": float(item.test_accuracy),
                "test_macro_f1": float(item.test_macro_f1),
                "test_weighted_f1": float(item.test_weighted_f1),
                "cv_macro_f1_mean": float(item.cv_macro_f1_mean),
                "cv_macro_f1_std": float(item.cv_macro_f1_std),
            }
            for item in candidate_results
        ],
        "artifacts": {
            "model_path": str(model_out.resolve()),
            "metrics_path": str(metrics_out.resolve()),
        },
    }

    metrics_out.write_text(json.dumps(payload, indent=2))

    print("Training complete.")
    print(f"model_version={model_version}")
    print(f"selected_model={selected_result.name}")
    print(f"dataset_sha256={dataset_hash}")
    print(f"final_accuracy={final_acc:.4f}")
    print(f"final_macro_f1={final_f1_macro:.4f}")
    print(f"cv_macro_f1_mean={selected_result.cv_macro_f1_mean:.4f}")
    print(f"model_out={model_out.resolve()}")
    print(f"metrics_out={metrics_out.resolve()}")


if __name__ == "__main__":
    main()
