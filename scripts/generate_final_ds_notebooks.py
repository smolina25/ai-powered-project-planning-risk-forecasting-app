from __future__ import annotations

import textwrap
from pathlib import Path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook


REPO_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS_DIR = REPO_ROOT / "notebooks"


def md(text: str):
    return new_markdown_cell(textwrap.dedent(text).strip() + "\n")


def code(text: str):
    return new_code_cell(textwrap.dedent(text).strip() + "\n")


COMMON_SETUP = """
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from IPython.display import Markdown, display

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path.cwd()
if not (PROJECT_ROOT / "data").exists():
    PROJECT_ROOT = PROJECT_ROOT.parent

DATA_DIR = PROJECT_ROOT / "data"

pd.set_option("display.max_columns", 50)
pd.set_option("display.float_format", lambda value: f"{value:,.2f}")
sns.set_theme(style="whitegrid", context="notebook")
"""


def build_notebook_01() -> nbformat.NotebookNode:
    project_column_definitions = [
        ("Project_ID", "Unique project identifier."),
        ("Portfolio_Segment", "Business segment or project type."),
        ("Region", "Geographic delivery region."),
        ("Delivery_Model", "Delivery approach used by the project."),
        ("Planning_Mode", "Planning workflow such as Manual, Spreadsheet, or AI-Assisted."),
        ("Complexity_Score", "Composite complexity rating from 0 to 100."),
        ("Planned_Duration_Days", "Original planned duration at kickoff."),
        ("Actual_Duration_Days", "Observed total duration at completion."),
        ("Delay_Days", "Actual duration minus planned duration."),
        ("Delay_Flag", "Binary indicator for delayed vs on-time delivery."),
        ("Planned_Budget_USD", "Planned project budget."),
        ("Actual_Budget_USD", "Observed total cost."),
        ("Budget_Overrun_Pct", "Percentage budget overrun vs planned budget."),
        ("Team_Size", "Team headcount assigned to the project."),
        ("Critical_Path_Task_Count", "Number of tasks on the critical path."),
        ("Vendor_Count", "Number of external vendors involved."),
        ("Change_Order_Count", "Count of change orders raised during execution."),
        ("Resource_Buffer_Pct", "Planned resource buffer percentage."),
        ("Weather_Risk_Index", "Weather-related execution risk index."),
        ("Procurement_Risk_Index", "Procurement and supply-chain risk index."),
        ("Stakeholder_Alignment_Score", "Cross-functional alignment score."),
        ("Requirements_Volatility_Score", "Requirements change volatility score."),
        ("Forecast_Error_Days", "Absolute planning forecast error in days."),
        ("Outcome_Risk_Level", "Observed project risk class: Low, Medium, or High."),
    ]
    monitoring_column_definitions = [
        ("Snapshot_Month", "Monthly monitoring snapshot date."),
        ("Project_ID", "Project identifier linked back to the portfolio dataset."),
        ("Portfolio_Segment", "Portfolio segment for grouped monitoring analysis."),
        ("Model_Version", "Version of the deployed advisory model."),
        ("Predicted_Risk_Level", "Model-predicted risk label."),
        ("Actual_Risk_Level", "Observed risk label used for monitoring."),
        ("Prediction_Confidence", "Model confidence score for the predicted class."),
        ("P80_Forecast_Days", "P80 duration forecast used for schedule commitment."),
        ("Actual_Completion_Days", "Observed total completion duration."),
        ("Absolute_Forecast_Error_Days", "Absolute difference between P80 forecast and actual outcome."),
        ("Drift_Score", "Monitoring score indicating potential data drift."),
        ("Alerts_Open", "Count of monitoring alerts triggered for the project snapshot."),
    ]

    return new_notebook(
        cells=[
            md(
                """
                # 01 Business Understanding and Data Audit

                **Project:** certAIn Product Intelligence  
                **Product:** AI-powered Project Planning & Risk Forecasting App

                This notebook frames the capstone business problem and audits the project-level analytics and monitoring datasets used throughout the forecasting workflow:

                - `data/project_portfolio_history.csv`
                - `data/risk_monitoring_snapshot.csv`

                The task-level advisory classifier training dataset, `data/construction_dataset.csv`, is tracked separately in the training pipeline and model metrics. The checked-in file aligns with the Kaggle `Construction Project Management Dataset` listing.
                """
            ),
            md(
                """
                ## Business Problem Definition

                Project teams often commit to delivery dates and budgets using deterministic plans. That creates three business problems:

                1. schedule risk is discovered too late,
                2. mitigation decisions are reactive instead of proactive,
                3. stakeholder updates are not backed by probability-based evidence.

                certAIn Product Intelligence addresses that gap by combining structured project data, risk classification, and Monte Carlo forecasting into one planning workflow.
                """
            ),
            md(
                """
                ## Business Questions

                The capstone focuses on four business questions:

                1. Which project characteristics are associated with higher delay and risk outcomes?
                2. Can we predict project risk level early enough to support planning decisions?
                3. How reliable are P80-based forecasts compared with actual completion durations?
                4. How can simulation outputs improve commitment quality for project managers and stakeholders?
                """
            ),
            code(COMMON_SETUP),
            code(
                """
                project_df = pd.read_csv(DATA_DIR / "project_portfolio_history.csv")
                monitoring_df = pd.read_csv(DATA_DIR / "risk_monitoring_snapshot.csv")

                dataset_overview = pd.DataFrame(
                    {
                        "dataset": ["project_portfolio_history", "risk_monitoring_snapshot"],
                        "rows": [len(project_df), len(monitoring_df)],
                        "columns": [project_df.shape[1], monitoring_df.shape[1]],
                    }
                )

                display(dataset_overview)
                """
            ),
            md("## Dataset Overview"),
            code(
                """
                display(project_df.head(3))
                display(monitoring_df.head(3))
                """
            ),
            md("## Column Definitions"),
            code(
                f"""
                project_columns = pd.DataFrame({project_column_definitions}, columns=["column", "definition"])
                monitoring_columns = pd.DataFrame({monitoring_column_definitions}, columns=["column", "definition"])

                display(project_columns)
                display(monitoring_columns)
                """
            ),
            md("## Missing Values, Duplicates, and Data Types"),
            code(
                """
                def audit_frame(name: str, frame: pd.DataFrame, id_column: str) -> pd.DataFrame:
                    return pd.DataFrame(
                        {
                            "dataset": [name],
                            "rows": [len(frame)],
                            "columns": [frame.shape[1]],
                            "missing_values": [int(frame.isna().sum().sum())],
                            "duplicate_rows": [int(frame.duplicated().sum())],
                            f"duplicate_{id_column}": [int(frame[id_column].duplicated().sum())],
                        }
                    )

                audit_summary = pd.concat(
                    [
                        audit_frame("project_portfolio_history", project_df, "Project_ID"),
                        audit_frame("risk_monitoring_snapshot", monitoring_df, "Project_ID"),
                    ],
                    ignore_index=True,
                )

                dtype_summary = pd.concat(
                    {
                        "project_portfolio_history": project_df.dtypes.astype(str),
                        "risk_monitoring_snapshot": monitoring_df.dtypes.astype(str),
                    },
                    axis=1,
                ).reset_index().rename(columns={"index": "column"})

                display(audit_summary)
                display(dtype_summary)
                """
            ),
            md("## Basic Statistics"),
            code(
                """
                display(project_df.describe(include="all").transpose())
                display(monitoring_df.describe(include="all").transpose())
                """
            ),
            md("## Initial Observations"),
            code(
                """
                delayed_share = (project_df["Delay_Flag"] == "Delayed").mean()
                avg_delay = project_df["Delay_Days"].mean()
                avg_budget_overrun = project_df["Budget_Overrun_Pct"].mean()
                planning_mode_delay = project_df.groupby("Planning_Mode")["Delay_Days"].mean().sort_values()
                monitoring_accuracy = (
                    monitoring_df["Predicted_Risk_Level"] == monitoring_df["Actual_Risk_Level"]
                ).mean()
                avg_forecast_error = monitoring_df["Absolute_Forecast_Error_Days"].mean()
                high_drift_share = (monitoring_df["Drift_Score"] > 0.55).mean()

                display(
                    Markdown(
                        f'''
                        **Key audit findings**

                        - The portfolio dataset contains **{len(project_df)} projects** with no missing values and no duplicate project IDs.
                        - **{delayed_share:.1%}** of projects were delayed, with an average delay of **{avg_delay:.1f} days**.
                        - Average budget overrun is **{avg_budget_overrun:.1f}%**, showing that schedule risk and cost risk co-exist in the portfolio.
                        - Planning mode matters: the lowest mean delay in this snapshot comes from **{planning_mode_delay.index[0]}** planning.
                        - The monitoring dataset shows **{monitoring_accuracy:.1%}** agreement between predicted and actual risk labels.
                        - Average absolute P80 forecast error is **{avg_forecast_error:.1f} days**, and **{high_drift_share:.1%}** of monitoring rows are above the drift-alert threshold.
                        '''
                    )
                )
                """
            ),
            md(
                """
                ## Audit Conclusion

                The two datasets are clean enough for capstone analysis. The business value comes from linking them:

                - `project_portfolio_history.csv` supports EDA, project-level benchmarking, and forecasting context,
                - `risk_monitoring_snapshot.csv` supports post-model monitoring and forecast reliability analysis.

                The bundled task-level advisory classifier used by the app is trained separately from `construction_dataset.csv`, the repo training CSV aligned with the Kaggle `Construction Project Management Dataset` listing.

                The next notebook focuses on pattern discovery across delays, complexity, team composition, and risk outcomes.
                """
            ),
        ],
        metadata={
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
        },
    )


def build_notebook_02() -> nbformat.NotebookNode:
    return new_notebook(
        cells=[
            md(
                """
                # 02 Exploratory Data Analysis

                This notebook explores the portfolio dataset to understand patterns in project duration, delay risk, and project complexity. It supports the business story and exploratory project-level modeling, while the bundled task-level advisory classifier is trained separately from `construction_dataset.csv`, the repo training CSV aligned with the Kaggle `Construction Project Management Dataset` listing.
                """
            ),
            code(COMMON_SETUP),
            code(
                """
                project_df = pd.read_csv(DATA_DIR / "project_portfolio_history.csv")
                project_df["Delay_Probability_Flag"] = (project_df["Delay_Flag"] == "Delayed").astype(int)
                project_df["Planning_Mode"] = pd.Categorical(
                    project_df["Planning_Mode"],
                    categories=["Manual", "Spreadsheet", "AI-Assisted"],
                    ordered=True,
                )

                project_df.head()
                """
            ),
            md("## 1. Project Duration Distribution"),
            code(
                """
                fig, axes = plt.subplots(1, 2, figsize=(15, 5))

                sns.histplot(project_df["Actual_Duration_Days"], bins=24, kde=True, ax=axes[0], color="#1f77b4")
                axes[0].set_title("Actual Project Duration Distribution")
                axes[0].set_xlabel("Actual Duration (days)")

                sns.boxplot(data=project_df, x="Planning_Mode", y="Actual_Duration_Days", ax=axes[1], palette="Set2")
                axes[1].set_title("Actual Duration by Planning Mode")
                axes[1].set_xlabel("Planning Mode")
                axes[1].set_ylabel("Actual Duration (days)")

                plt.tight_layout()
                plt.show()
                """
            ),
            md(
                """
                The portfolio includes both medium-length and long-running projects. Comparing distributions by planning mode gives early evidence on whether AI-assisted planning changes schedule outcomes.
                """
            ),
            md("## 2. Delay Distribution"),
            code(
                """
                fig, axes = plt.subplots(1, 2, figsize=(15, 5))

                sns.histplot(project_df["Delay_Days"], bins=24, kde=True, ax=axes[0], color="#d62728")
                axes[0].axvline(project_df["Delay_Days"].median(), color="black", linestyle="--", label="Median delay")
                axes[0].set_title("Delay Distribution")
                axes[0].set_xlabel("Delay (days)")
                axes[0].legend()

                sns.boxplot(data=project_df, x="Outcome_Risk_Level", y="Delay_Days", ax=axes[1], palette="coolwarm")
                axes[1].set_title("Delay by Outcome Risk Level")
                axes[1].set_xlabel("Outcome Risk Level")
                axes[1].set_ylabel("Delay (days)")

                plt.tight_layout()
                plt.show()
                """
            ),
            md("## 3. Risk Level Distribution"),
            code(
                """
                risk_counts = project_df["Outcome_Risk_Level"].value_counts().reindex(["Low", "Medium", "High"])

                plt.figure(figsize=(8, 5))
                sns.countplot(data=project_df, x="Outcome_Risk_Level", order=["Low", "Medium", "High"], palette="viridis")
                plt.title("Outcome Risk Level Distribution")
                plt.xlabel("Risk Level")
                plt.ylabel("Project Count")
                plt.show()

                display(risk_counts.to_frame(name="count"))
                """
            ),
            md("## 4. Correlation Matrix"),
            code(
                """
                numeric_columns = [
                    "Complexity_Score",
                    "Planned_Duration_Days",
                    "Actual_Duration_Days",
                    "Delay_Days",
                    "Planned_Budget_USD",
                    "Actual_Budget_USD",
                    "Budget_Overrun_Pct",
                    "Team_Size",
                    "Critical_Path_Task_Count",
                    "Vendor_Count",
                    "Change_Order_Count",
                    "Resource_Buffer_Pct",
                    "Weather_Risk_Index",
                    "Procurement_Risk_Index",
                    "Stakeholder_Alignment_Score",
                    "Requirements_Volatility_Score",
                    "Forecast_Error_Days",
                ]

                correlation_matrix = project_df[numeric_columns].corr()

                plt.figure(figsize=(14, 10))
                sns.heatmap(correlation_matrix, cmap="RdBu_r", center=0, annot=False)
                plt.title("Correlation Matrix for Numeric Project Variables")
                plt.show()
                """
            ),
            md("## 5. Complexity vs Delay Relationship"),
            code(
                """
                plt.figure(figsize=(10, 6))
                sns.scatterplot(
                    data=project_df,
                    x="Complexity_Score",
                    y="Delay_Days",
                    hue="Outcome_Risk_Level",
                    size="Planned_Budget_USD",
                    palette="coolwarm",
                    alpha=0.75,
                )
                sns.regplot(
                    data=project_df,
                    x="Complexity_Score",
                    y="Delay_Days",
                    scatter=False,
                    color="black",
                    line_kws={"linewidth": 2, "linestyle": "--"},
                )
                plt.title("Complexity Score vs Delay Days")
                plt.show()
                """
            ),
            md("## 6. Team Size vs Delay Probability"),
            code(
                """
                team_delay = (
                    project_df.assign(team_band=pd.qcut(project_df["Team_Size"], q=5, duplicates="drop"))
                    .groupby("team_band", observed=False)
                    .agg(
                        avg_team_size=("Team_Size", "mean"),
                        delay_probability=("Delay_Probability_Flag", "mean"),
                        project_count=("Project_ID", "count"),
                    )
                    .reset_index()
                )

                fig, ax1 = plt.subplots(figsize=(10, 6))
                sns.lineplot(data=team_delay, x="avg_team_size", y="delay_probability", marker="o", ax=ax1, color="#9467bd")
                ax1.set_title("Average Team Size vs Delay Probability")
                ax1.set_xlabel("Average Team Size in Quantile Bin")
                ax1.set_ylabel("Delay Probability")
                ax1.set_ylim(0, 1)
                plt.show()

                display(team_delay)
                """
            ),
            md("## 7. Project Type Analysis"),
            code(
                """
                segment_summary = (
                    project_df.groupby("Portfolio_Segment")
                    .agg(
                        project_count=("Project_ID", "count"),
                        avg_delay_days=("Delay_Days", "mean"),
                        delayed_share=("Delay_Probability_Flag", "mean"),
                        avg_budget_overrun_pct=("Budget_Overrun_Pct", "mean"),
                    )
                    .sort_values("avg_delay_days", ascending=False)
                    .reset_index()
                )

                fig, axes = plt.subplots(1, 2, figsize=(16, 5))
                sns.barplot(data=segment_summary, x="Portfolio_Segment", y="avg_delay_days", ax=axes[0], palette="Blues_d")
                axes[0].set_title("Average Delay by Portfolio Segment")
                axes[0].tick_params(axis="x", rotation=35)
                axes[0].set_ylabel("Average Delay (days)")

                sns.barplot(data=segment_summary, x="Portfolio_Segment", y="avg_budget_overrun_pct", ax=axes[1], palette="Oranges_d")
                axes[1].set_title("Average Budget Overrun by Segment")
                axes[1].tick_params(axis="x", rotation=35)
                axes[1].set_ylabel("Average Budget Overrun (%)")

                plt.tight_layout()
                plt.show()

                display(segment_summary)
                """
            ),
            md("## 8. Interactive Exploration with Plotly"),
            code(
                """
                interactive_fig = px.scatter(
                    project_df,
                    x="Complexity_Score",
                    y="Delay_Days",
                    color="Outcome_Risk_Level",
                    symbol="Planning_Mode",
                    size="Planned_Budget_USD",
                    hover_data=["Project_ID", "Portfolio_Segment", "Team_Size", "Vendor_Count"],
                    title="Interactive View: Complexity, Delay, and Risk",
                    template="plotly_white",
                )
                interactive_fig.show()
                """
            ),
            md("## 9. EDA Takeaways"),
            code(
                """
                top_delay_segment = segment_summary.iloc[0]
                correlation = project_df[["Complexity_Score", "Delay_Days"]].corr().iloc[0, 1]
                planning_mode_summary = project_df.groupby("Planning_Mode")["Delay_Days"].mean().sort_values()

                display(
                    Markdown(
                        f'''
                        **EDA summary**

                        - Complexity and delay are positively related in this portfolio (correlation **{correlation:.2f}**).
                        - The segment with the highest average delay is **{top_delay_segment['Portfolio_Segment']}** at **{top_delay_segment['avg_delay_days']:.1f} days**.
                        - AI-assisted planning has the lowest average delay in the current data snapshot at **{planning_mode_summary.iloc[0]:.1f} days**.
                        - Delay and budget overrun move together across segments, which supports the case for earlier risk forecasting.
                        '''
                    )
                )
                """
            ),
        ],
        metadata={
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
        },
    )


def build_notebook_03() -> nbformat.NotebookNode:
    return new_notebook(
        cells=[
            md(
                """
                # 03 Bundled Advisory Model Review

                This notebook focuses only on the current task-level advisory model bundled with the app. It uses `data/construction_dataset.csv` together with `models/risk_model_metrics.json` so the notebook reflects the same model lineage shown in the dashboard and presentation.
                """
            ),
            code(
                """
                from pathlib import Path
                import json
                import warnings

                import pandas as pd
                import matplotlib.pyplot as plt
                import seaborn as sns
                from IPython.display import Markdown, display

                warnings.filterwarnings("ignore")

                PROJECT_ROOT = Path.cwd()
                if not (PROJECT_ROOT / "data").exists():
                    PROJECT_ROOT = PROJECT_ROOT.parent

                DATA_DIR = PROJECT_ROOT / "data"
                MODELS_DIR = PROJECT_ROOT / "models"
                sns.set_theme(style="whitegrid", context="notebook")
                pd.set_option("display.max_columns", 50)
                pd.set_option("display.float_format", lambda value: f"{value:,.3f}")
                """
            ),
            md(
                """
                ## 1. Load the Current Training Dataset and Metrics

                The goal here is consistency with the bundled advisory model artifact. Instead of replaying older exploratory model comparisons, this notebook reads the current task-level training CSV and the saved metrics JSON produced by the training pipeline.
                """
            ),
            code(
                """
                task_df = pd.read_csv(DATA_DIR / "construction_dataset.csv")
                metrics = json.loads((MODELS_DIR / "risk_model_metrics.json").read_text())
                selected_metrics = next(
                    item
                    for item in metrics["model_comparison"]
                    if item["model_name"] == metrics["selected_model_name"]
                )
                selected_model_name = metrics["selected_model_name"]

                summary_df = pd.DataFrame(
                    {
                        "item": [
                            "rows",
                            "columns",
                            "target_column",
                            "selected_model_name",
                            "selection_metric",
                            "model_version",
                        ],
                        "value": [
                            len(task_df),
                            task_df.shape[1],
                            metrics["target_column"],
                            metrics["selected_model_name"],
                            metrics["selection_metric"],
                            metrics["model_version"],
                        ],
                    }
                )

                display(summary_df)
                """
            ),
            md("## 2. Dataset Overview"),
            code(
                """
                display(task_df.head())

                target_counts = (
                    task_df[metrics["target_column"]]
                    .value_counts()
                    .rename_axis("risk_level")
                    .reset_index(name="count")
                )
                display(target_counts)

                feature_columns = pd.DataFrame(
                    {"feature_column": metrics["feature_columns"]}
                )
                display(feature_columns)
                """
            ),
            md(
                """
                ## 3. Selected Model Summary

                The training pipeline evaluated multiple candidates, but this notebook surfaces only the model that is actually bundled with the app.
                """
            ),
            code(
                """
                selected_metrics_df = pd.DataFrame(
                    [
                        {
                            "Selected Model": selected_model_name,
                            "Selection Metric": metrics["selection_metric"],
                            "Test Accuracy": selected_metrics["test_accuracy"],
                            "Macro F1": selected_metrics["test_macro_f1"],
                            "Weighted F1": selected_metrics["test_weighted_f1"],
                            "CV Macro F1": selected_metrics["cv_macro_f1_mean"],
                            "CV Macro F1 Std": selected_metrics["cv_macro_f1_std"],
                        }
                    ]
                )

                selection_note_df = pd.DataFrame(
                    {
                        "field": ["selection_reason", "trained_at_utc"],
                        "value": [metrics["selection_reason"], metrics["trained_at_utc"]],
                    }
                )

                display(selected_metrics_df)
                display(selection_note_df)
                """
            ),
            md("## 4. Selected Model Metrics"),
            code(
                """
                metric_plot_df = pd.DataFrame(
                    {
                        "metric": ["Test Accuracy", "Macro F1", "Weighted F1", "CV Macro F1"],
                        "value": [
                            selected_metrics["test_accuracy"],
                            selected_metrics["test_macro_f1"],
                            selected_metrics["test_weighted_f1"],
                            selected_metrics["cv_macro_f1_mean"],
                        ],
                    }
                )

                plt.figure(figsize=(8, 5))
                sns.barplot(data=metric_plot_df, x="metric", y="value", palette="Blues_d")
                plt.title(f"Selected Model Metrics: {selected_model_name}")
                plt.xlabel("")
                plt.ylabel("Score")
                plt.ylim(0, 1)
                plt.xticks(rotation=20)
                plt.tight_layout()
                plt.show()
                """
            ),
            md("## 5. Selected Model Confusion Matrix"),
            code(
                """
                confusion = metrics["confusion_matrix"]
                labels = confusion["labels"]
                confusion_df = pd.DataFrame(
                    confusion["values"],
                    index=labels,
                    columns=labels,
                )

                plt.figure(figsize=(6, 5))
                sns.heatmap(confusion_df, annot=True, fmt="d", cmap="Blues", cbar=False)
                plt.title(f"Confusion Matrix: {metrics['selected_model_name']}")
                plt.xlabel("Predicted")
                plt.ylabel("Actual")

                plt.show()
                """
            ),
            md("## 6. Feature Importance"),
            code(
                """
                feature_importance_df = pd.DataFrame(metrics["feature_importance"]).sort_values(
                    "importance",
                    ascending=False,
                )

                plt.figure(figsize=(8, 5))
                sns.barplot(
                    data=feature_importance_df.head(8),
                    x="importance",
                    y="feature",
                    palette="viridis",
                )
                plt.title("Top Feature Importance Values")
                plt.xlabel("Permutation Importance")
                plt.ylabel("Feature")
                plt.tight_layout()
                plt.show()
                """
            ),
            md("## 7. Interpretation"),
            code(
                """
                display(
                    Markdown(
                        f'''
                        **Current bundled model summary**

                        - The selected bundled model is **{metrics['selected_model_name']}**, chosen by **{metrics['selection_metric']}**.
                        - The selected model records **{selected_metrics['cv_macro_f1_mean']:.3f}** cross-validated macro F1 and **{selected_metrics['test_macro_f1']:.3f}** test macro F1.
                        - The dashboard, slide deck, and metrics file now point to the same bundled model and dataset lineage.
                        - This notebook intentionally omits non-runtime candidate models so it stays aligned with what the app actually uses.
                        '''
                    )
                )
                """
            ),
        ],
        metadata={
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
        },
    )


def build_notebook_04() -> nbformat.NotebookNode:
    return new_notebook(
        cells=[
            md(
                """
                # 04 Risk Forecasting Simulation

                This notebook connects the classical data-science workflow to the product itself. It converts a real project row into a task network, runs Monte Carlo simulation, and turns the output into schedule commitment metrics.
                """
            ),
            code(
                """
                from pathlib import Path
                import warnings

                import numpy as np
                import pandas as pd
                import matplotlib.pyplot as plt
                import seaborn as sns
                from IPython.display import Markdown, display

                from src.analytics.metrics import compute_metrics
                from src.modeling.critical_path import critical_path_by_mean
                from src.modeling.graph_builder import build_project_graph
                from src.simulation.monte_carlo import run_monte_carlo

                warnings.filterwarnings("ignore")

                PROJECT_ROOT = Path.cwd()
                if not (PROJECT_ROOT / "data").exists():
                    PROJECT_ROOT = PROJECT_ROOT.parent

                DATA_DIR = PROJECT_ROOT / "data"
                sns.set_theme(style="whitegrid", context="notebook")
                pd.set_option("display.max_columns", 50)
                """
            ),
            md("## 1. Load Portfolio and Monitoring Data"),
            code(
                """
                project_df = pd.read_csv(DATA_DIR / "project_portfolio_history.csv")
                monitoring_df = pd.read_csv(DATA_DIR / "risk_monitoring_snapshot.csv")

                monitoring_accuracy = (
                    monitoring_df["Predicted_Risk_Level"] == monitoring_df["Actual_Risk_Level"]
                ).mean()
                avg_forecast_error = monitoring_df["Absolute_Forecast_Error_Days"].mean()

                display(
                    Markdown(
                        f'''
                        Monitoring snapshot:

                        - prediction agreement: **{monitoring_accuracy:.1%}**
                        - average absolute P80 forecast error: **{avg_forecast_error:.1f} days**
                        '''
                    )
                )
                """
            ),
            md(
                """
                ## 2. Select a Representative High-Risk Project

                To demonstrate schedule simulation, we select one high-risk project whose delay is close to the median delay for high-risk projects. This avoids choosing an extreme outlier.
                """
            ),
            code(
                """
                high_risk_projects = project_df[project_df["Outcome_Risk_Level"] == "High"].copy()
                reference_delay = high_risk_projects["Delay_Days"].median()
                selected_project = high_risk_projects.iloc[
                    (high_risk_projects["Delay_Days"] - reference_delay).abs().argsort().iloc[0]
                ]

                selected_project.to_frame(name="value")
                """
            ),
            md("## 3. Convert the Project Row into a Task Graph"),
            code(
                """
                def project_to_tasks(project_row: pd.Series, scenario: str = "baseline") -> list[dict]:
                    shares = {
                        "T1": ("Discovery", 0.08),
                        "T2": ("Design", 0.15),
                        "T3": ("Procurement", 0.18),
                        "T4": ("Site Preparation", 0.12),
                        "T5": ("Execution", 0.28),
                        "T6": ("QA and Commissioning", 0.12),
                        "T7": ("Handover", 0.07),
                    }

                    dependencies = {
                        "T1": [],
                        "T2": ["T1"],
                        "T3": ["T1"],
                        "T4": ["T2"],
                        "T5": ["T3", "T4"],
                        "T6": ["T5"],
                        "T7": ["T6"],
                    }

                    complexity_factor = project_row["Complexity_Score"] / 100
                    weather_factor = project_row["Weather_Risk_Index"] / 100
                    procurement_factor = project_row["Procurement_Risk_Index"] / 100
                    volatility_factor = project_row["Requirements_Volatility_Score"] / 100
                    alignment_gap = (100 - project_row["Stakeholder_Alignment_Score"]) / 100
                    buffer_factor = project_row["Resource_Buffer_Pct"] / 100
                    planning_adjustment = {
                        "AI-Assisted": -0.03,
                        "Spreadsheet": 0.00,
                        "Manual": 0.02,
                    }[project_row["Planning_Mode"]]

                    base_uplift = (
                        0.04 * complexity_factor
                        + 0.03 * weather_factor
                        + 0.03 * procurement_factor
                        + 0.02 * volatility_factor
                        - 0.02 * buffer_factor
                        + planning_adjustment
                    )

                    if scenario == "mitigated":
                        mean_multiplier = 1 + max(base_uplift - 0.03, 0)
                        std_multiplier = 0.80
                    else:
                        mean_multiplier = 1 + max(base_uplift, 0)
                        std_multiplier = 1.00

                    std_lookup = {
                        "T1": 0.10 + 0.12 * volatility_factor,
                        "T2": 0.12 + 0.16 * volatility_factor,
                        "T3": 0.14 + 0.18 * procurement_factor,
                        "T4": 0.11 + 0.14 * weather_factor,
                        "T5": 0.18 + 0.18 * max(weather_factor, procurement_factor) + 0.10 * complexity_factor,
                        "T6": 0.10 + 0.10 * alignment_gap,
                        "T7": 0.08 + 0.08 * (project_row["Vendor_Count"] / max(project_df["Vendor_Count"].max(), 1)),
                    }

                    tasks = []
                    for task_id, (task_name, share) in shares.items():
                        mean_duration = project_row["Planned_Duration_Days"] * share * mean_multiplier
                        std_dev = mean_duration * std_lookup[task_id] * std_multiplier
                        tasks.append(
                            {
                                "id": task_id,
                                "name": task_name,
                                "dependencies": dependencies[task_id],
                                "mean_duration": round(float(mean_duration), 2),
                                "std_dev": round(float(std_dev), 2),
                            }
                        )

                    return tasks


                baseline_tasks = project_to_tasks(selected_project, scenario="baseline")
                mitigated_tasks = project_to_tasks(selected_project, scenario="mitigated")

                task_frame = pd.DataFrame(baseline_tasks)
                display(task_frame)
                """
            ),
            md("## 4. Run Monte Carlo Simulation"),
            code(
                """
                baseline_graph = build_project_graph(baseline_tasks)
                mitigated_graph = build_project_graph(mitigated_tasks)

                baseline_path, baseline_mean_duration = critical_path_by_mean(baseline_graph)
                mitigated_path, mitigated_mean_duration = critical_path_by_mean(mitigated_graph)

                baseline_samples = run_monte_carlo(baseline_graph, iterations=5000, seed=42)
                mitigated_samples = run_monte_carlo(mitigated_graph, iterations=5000, seed=42)

                deadline = float(selected_project["Planned_Duration_Days"])
                baseline_metrics = compute_metrics(baseline_samples, deadline_days=deadline)
                mitigated_metrics = compute_metrics(mitigated_samples, deadline_days=deadline)

                project_start = pd.Timestamp("2026-04-01")
                summary = pd.DataFrame(
                    [
                        {
                            "scenario": "Baseline",
                            "critical_path": " -> ".join(baseline_path),
                            "mean_duration_days": baseline_mean_duration,
                            "p50_days": baseline_metrics["p50"],
                            "p80_days": baseline_metrics["p80"],
                            "delay_probability": baseline_metrics["delay_probability"],
                            "p50_completion_date": project_start + pd.to_timedelta(round(baseline_metrics["p50"]), unit="D"),
                            "p80_completion_date": project_start + pd.to_timedelta(round(baseline_metrics["p80"]), unit="D"),
                        },
                        {
                            "scenario": "Mitigated",
                            "critical_path": " -> ".join(mitigated_path),
                            "mean_duration_days": mitigated_mean_duration,
                            "p50_days": mitigated_metrics["p50"],
                            "p80_days": mitigated_metrics["p80"],
                            "delay_probability": mitigated_metrics["delay_probability"],
                            "p50_completion_date": project_start + pd.to_timedelta(round(mitigated_metrics["p50"]), unit="D"),
                            "p80_completion_date": project_start + pd.to_timedelta(round(mitigated_metrics["p80"]), unit="D"),
                        },
                    ]
                )

                display(summary)
                """
            ),
            md("## 5. Visualize Completion-Time Uncertainty"),
            code(
                """
                plt.figure(figsize=(12, 6))
                sns.histplot(baseline_samples, bins=40, stat="density", color="#1f77b4", alpha=0.55, label="Baseline")
                sns.histplot(mitigated_samples, bins=40, stat="density", color="#2ca02c", alpha=0.40, label="Mitigated")
                plt.axvline(deadline, color="black", linestyle="--", linewidth=2, label="Planned deadline")
                plt.axvline(baseline_metrics["p50"], color="#1f77b4", linestyle=":", linewidth=2, label="Baseline P50")
                plt.axvline(baseline_metrics["p80"], color="#1f77b4", linestyle="-.", linewidth=2, label="Baseline P80")
                plt.axvline(mitigated_metrics["p80"], color="#2ca02c", linestyle="-.", linewidth=2, label="Mitigated P80")
                plt.title("Monte Carlo Completion-Time Distribution")
                plt.xlabel("Completion Time (days)")
                plt.ylabel("Density")
                plt.legend()
                plt.show()
                """
            ),
            md("## 6. Compare Simulation Output with Monitoring Data"),
            code(
                """
                monitoring_slice = monitoring_df[monitoring_df["Project_ID"] == selected_project["Project_ID"]]
                display(monitoring_slice)
                """
            ),
            md("## 7. Decision Interpretation"),
            code(
                """
                baseline_p80_date = summary.loc[summary["scenario"] == "Baseline", "p80_completion_date"].iloc[0]
                mitigated_p80_date = summary.loc[summary["scenario"] == "Mitigated", "p80_completion_date"].iloc[0]
                baseline_delay_probability = summary.loc[summary["scenario"] == "Baseline", "delay_probability"].iloc[0]
                mitigated_delay_probability = summary.loc[summary["scenario"] == "Mitigated", "delay_probability"].iloc[0]

                display(
                    Markdown(
                        f'''
                        **Simulation summary for project {selected_project['Project_ID']}**

                        - Planned duration: **{int(deadline)} days**
                        - Baseline P50 / P80: **{baseline_metrics['p50']:.1f} / {baseline_metrics['p80']:.1f} days**
                        - Baseline P80 completion date: **{baseline_p80_date.date()}**
                        - Baseline delay probability: **{baseline_delay_probability:.1%}**
                        - Mitigated P80 completion date: **{mitigated_p80_date.date()}**
                        - Mitigated delay probability: **{mitigated_delay_probability:.1%}**

                        This is the core decision-support idea of the product: instead of committing to one deterministic date, the team can compare scenarios and choose the option with the lower probability of delay.
                        '''
                    )
                )
                """
            ),
        ],
        metadata={
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
        },
    )


def write_notebook(path: Path, notebook: nbformat.NotebookNode) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(notebook, path)


def execute_notebook(path: Path) -> None:
    with path.open("r", encoding="utf-8") as handle:
        notebook = nbformat.read(handle, as_version=4)

    executor = ExecutePreprocessor(timeout=600, kernel_name="python3")
    executor.preprocess(notebook, {"metadata": {"path": str(REPO_ROOT)}})

    with path.open("w", encoding="utf-8") as handle:
        nbformat.write(notebook, handle)


def main() -> None:
    notebook_builders = {
        NOTEBOOKS_DIR / "01_business_understanding_and_data_audit.ipynb": build_notebook_01,
        NOTEBOOKS_DIR / "02_exploratory_data_analysis.ipynb": build_notebook_02,
        NOTEBOOKS_DIR / "03_baseline_and_model_comparison.ipynb": build_notebook_03,
        NOTEBOOKS_DIR / "04_risk_forecasting_dag_monte_carlo.ipynb": build_notebook_04,
    }

    for path, builder in notebook_builders.items():
        write_notebook(path, builder())
        execute_notebook(path)
        print(f"Generated and executed {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
