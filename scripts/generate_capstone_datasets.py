from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate synthetic capstone-style datasets for local certAIn experimentation."
    )
    parser.add_argument("--out-dir", default="data", help="Directory for generated CSV files.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument(
        "--task-rows",
        type=int,
        default=2400,
        help="Number of rows for the task-level ML dataset.",
    )
    parser.add_argument(
        "--project-rows",
        type=int,
        default=360,
        help="Number of rows for the project portfolio dataset.",
    )
    parser.add_argument(
        "--monitor-rows",
        type=int,
        default=270,
        help="Number of rows for the monitoring snapshot dataset.",
    )
    return parser.parse_args()


def _scaled_sigmoid(values: np.ndarray, low: float, high: float) -> np.ndarray:
    sigmoid = 1.0 / (1.0 + np.exp(-values))
    return np.clip(low + (high - low) * sigmoid, low, high)


def generate_task_risk_dataset(rng: np.random.Generator, n_rows: int) -> pd.DataFrame:
    complexity = rng.normal(0, 1, n_rows)
    resource_stress = rng.normal(0, 1, n_rows)
    site_exposure = rng.normal(0, 1, n_rows)

    task_duration = np.clip(
        np.round(28 + 12 * complexity + 4.5 * site_exposure + rng.normal(0, 6, n_rows)),
        2,
        120,
    ).astype(int)
    labor_required = np.clip(
        np.round(7 + 2.8 * complexity + 2.3 * resource_stress + rng.normal(0, 2, n_rows)),
        2,
        24,
    ).astype(int)
    equipment_units = np.clip(
        np.round(3 + 1.2 * complexity + 1.0 * site_exposure + rng.normal(0, 1.2, n_rows)),
        1,
        12,
    ).astype(int)
    material_cost = np.clip(
        18000
        + 8500 * complexity
        + 6000 * site_exposure
        + 3000 * resource_stress
        + labor_required * 1700
        + equipment_units * 3600
        + rng.normal(0, 12000, n_rows),
        3000,
        180000,
    )
    start_constraint = np.clip(
        np.round(6 + 4.5 * resource_stress + 2.5 * site_exposure + rng.normal(0, 4, n_rows)),
        0,
        35,
    ).astype(int)
    resource_constraint = _scaled_sigmoid(
        0.9 * resource_stress + 0.35 * complexity + rng.normal(0, 0.6, n_rows),
        0.10,
        0.99,
    )
    site_constraint = _scaled_sigmoid(
        1.0 * site_exposure + 0.25 * complexity + rng.normal(0, 0.6, n_rows),
        0.08,
        0.99,
    )
    dependency_count = np.clip(
        np.round(1.8 + 0.9 * complexity + 0.5 * site_exposure + rng.normal(0, 1.1, n_rows)),
        0,
        6,
    ).astype(int)

    duration_z = (task_duration - task_duration.mean()) / task_duration.std()
    labor_z = (labor_required - labor_required.mean()) / labor_required.std()
    equipment_z = (equipment_units - equipment_units.mean()) / equipment_units.std()
    cost_z = (material_cost - material_cost.mean()) / material_cost.std()
    start_z = (start_constraint - start_constraint.mean()) / start_constraint.std()
    dependency_z = (dependency_count - dependency_count.mean()) / dependency_count.std()

    resource_site_interaction = (
        (resource_constraint > 0.70) & (site_constraint > 0.68)
    ).astype(float) * 0.32
    bottleneck_interaction = (
        (dependency_count >= 4) & (task_duration >= 55)
    ).astype(float) * 0.24
    risk_score = (
        0.18 * duration_z
        + 0.10 * labor_z
        + 0.06 * equipment_z
        + 0.12 * cost_z
        + 0.06 * start_z
        + 0.12 * resource_constraint
        + 0.11 * site_constraint
        + 0.04 * dependency_z
        + 0.16 * (resource_constraint * site_constraint)
        + 0.12 * np.maximum(duration_z, 0) * np.maximum(dependency_z, 0)
        + resource_site_interaction
        + bottleneck_interaction
        + rng.normal(0, 0.38, n_rows)
    )

    low_cutoff, high_cutoff = np.quantile(risk_score, [0.50, 0.80])
    risk_level = np.where(
        risk_score >= high_cutoff,
        "High",
        np.where(risk_score >= low_cutoff, "Medium", "Low"),
    )

    return pd.DataFrame(
        {
            "Task_ID": [f"T{index + 1}" for index in range(n_rows)],
            "Task_Duration_Days": task_duration,
            "Labor_Required": labor_required,
            "Equipment_Units": equipment_units,
            "Material_Cost_USD": np.round(material_cost, 2),
            "Start_Constraint": start_constraint,
            "Risk_Level": risk_level,
            "Resource_Constraint_Score": np.round(resource_constraint, 2),
            "Site_Constraint_Score": np.round(site_constraint, 2),
            "Dependency_Count": dependency_count,
        }
    )


def generate_project_portfolio_dataset(rng: np.random.Generator, n_rows: int) -> pd.DataFrame:
    segments = np.array(["Infrastructure", "Commercial", "Industrial", "Public Sector", "Energy"])
    regions = np.array(["North", "South", "East", "West", "Central"])
    delivery_models = np.array(["Design-Bid-Build", "Design-Build", "EPC", "Agile Hybrid"])
    planning_modes = np.array(["Manual", "Spreadsheet", "AI-Assisted"])
    planning_mode_prob = np.array([0.28, 0.42, 0.30])

    segment = rng.choice(segments, size=n_rows, p=[0.24, 0.22, 0.18, 0.18, 0.18])
    region = rng.choice(regions, size=n_rows)
    delivery_model = rng.choice(delivery_models, size=n_rows, p=[0.34, 0.28, 0.20, 0.18])
    planning_mode = rng.choice(planning_modes, size=n_rows, p=planning_mode_prob)

    segment_complexity_bias = {
        "Infrastructure": 8,
        "Commercial": 2,
        "Industrial": 10,
        "Public Sector": 5,
        "Energy": 12,
    }
    planning_effect = {"Manual": 1.15, "Spreadsheet": 1.00, "AI-Assisted": 0.82}

    complexity_score = []
    planned_duration = []
    actual_duration = []
    planned_budget = []
    actual_budget = []
    team_size = []
    critical_path_tasks = []
    vendor_count = []
    change_orders = []
    resource_buffer_pct = []
    weather_risk = []
    procurement_risk = []
    stakeholder_alignment = []
    requirements_volatility = []
    forecast_error_days = []
    outcome_risk = []

    for idx in range(n_rows):
        base_complexity = (
            55
            + segment_complexity_bias[segment[idx]]
            + rng.normal(0, 11)
        )
        complexity = int(np.clip(round(base_complexity), 18, 96))
        weather = float(np.clip(rng.beta(2.0, 3.5) * 100, 5, 95))
        procurement = float(np.clip(rng.beta(2.3, 2.8) * 100, 7, 97))
        alignment = float(np.clip(82 - 0.35 * complexity + rng.normal(0, 9), 18, 96))
        volatility = float(np.clip(24 + 0.38 * complexity + rng.normal(0, 10), 6, 98))
        team = int(np.clip(round(9 + complexity / 5 + rng.normal(0, 4)), 5, 40))
        vendors = int(np.clip(round(3 + complexity / 17 + rng.normal(0, 2)), 1, 18))
        cp_tasks = int(np.clip(round(4 + complexity / 10 + rng.normal(0, 2)), 3, 18))
        change_order_count = int(
            np.clip(round(1 + volatility / 18 + rng.normal(0, 1.5)), 0, 16)
        )
        buffer = float(np.clip(18 - complexity / 7 + rng.normal(0, 4), 2, 22))

        planned_days = int(
            np.clip(
                round(85 + complexity * 2.4 + cp_tasks * 4 + rng.normal(0, 18)),
                60,
                420,
            )
        )
        budget = float(
            np.clip(
                550000
                + complexity * 42000
                + team * 55000
                + vendors * 22000
                + rng.normal(0, 240000),
                350000,
                7800000,
            )
        )

        delay_pressure = (
            0.28 * (complexity / 100)
            + 0.16 * (weather / 100)
            + 0.18 * (procurement / 100)
            + 0.14 * (volatility / 100)
            + 0.10 * (change_order_count / 12)
            + 0.12 * (1 - alignment / 100)
        )
        adjusted_delay = delay_pressure * planning_effect[planning_mode[idx]]
        delay_days = int(
            np.clip(
                round(-20 + adjusted_delay * planned_days * 0.22 + rng.normal(0, 15)),
                -30,
                165,
            )
        )
        actual_days = max(planned_days + delay_days, 35)

        cost_pressure = (
            0.22 * (complexity / 100)
            + 0.16 * (procurement / 100)
            + 0.18 * (volatility / 100)
            + 0.12 * (weather / 100)
            + 0.14 * (change_order_count / 12)
            + 0.12 * (1 - alignment / 100)
            - 0.10 * (buffer / 100)
        )
        budget_overrun_pct = np.clip(
            -4 + cost_pressure * 42 * planning_effect[planning_mode[idx]] + rng.normal(0, 4),
            -9,
            34,
        )
        actual_cost = budget * (1 + budget_overrun_pct / 100)

        forecast_error = int(
            np.clip(
                round(abs(delay_days) * planning_effect[planning_mode[idx]] + rng.normal(0, 4)),
                1,
                90,
            )
        )
        outcome_score = (
            0.32 * (delay_days > 30)
            + 0.20 * (budget_overrun_pct > 10)
            + 0.18 * (weather > 65)
            + 0.16 * (procurement > 60)
            + 0.14 * (alignment < 50)
        )
        if outcome_score >= 0.58:
            risk_label = "High"
        elif outcome_score >= 0.28:
            risk_label = "Medium"
        else:
            risk_label = "Low"

        complexity_score.append(complexity)
        planned_duration.append(planned_days)
        actual_duration.append(actual_days)
        planned_budget.append(round(budget, 2))
        actual_budget.append(round(actual_cost, 2))
        team_size.append(team)
        critical_path_tasks.append(cp_tasks)
        vendor_count.append(vendors)
        change_orders.append(change_order_count)
        resource_buffer_pct.append(round(buffer, 1))
        weather_risk.append(round(weather, 1))
        procurement_risk.append(round(procurement, 1))
        stakeholder_alignment.append(round(alignment, 1))
        requirements_volatility.append(round(volatility, 1))
        forecast_error_days.append(forecast_error)
        outcome_risk.append(risk_label)

    df = pd.DataFrame(
        {
            "Project_ID": [f"P{index + 1:03d}" for index in range(n_rows)],
            "Portfolio_Segment": segment,
            "Region": region,
            "Delivery_Model": delivery_model,
            "Planning_Mode": planning_mode,
            "Complexity_Score": complexity_score,
            "Planned_Duration_Days": planned_duration,
            "Actual_Duration_Days": actual_duration,
            "Planned_Budget_USD": planned_budget,
            "Actual_Budget_USD": actual_budget,
            "Team_Size": team_size,
            "Critical_Path_Task_Count": critical_path_tasks,
            "Vendor_Count": vendor_count,
            "Change_Order_Count": change_orders,
            "Resource_Buffer_Pct": resource_buffer_pct,
            "Weather_Risk_Index": weather_risk,
            "Procurement_Risk_Index": procurement_risk,
            "Stakeholder_Alignment_Score": stakeholder_alignment,
            "Requirements_Volatility_Score": requirements_volatility,
            "Forecast_Error_Days": forecast_error_days,
            "Outcome_Risk_Level": outcome_risk,
        }
    )
    df["Delay_Days"] = df["Actual_Duration_Days"] - df["Planned_Duration_Days"]
    df["Delay_Flag"] = np.where(df["Delay_Days"] > 0, "Delayed", "On Time")
    df["Budget_Overrun_Pct"] = np.round(
        ((df["Actual_Budget_USD"] - df["Planned_Budget_USD"]) / df["Planned_Budget_USD"]) * 100,
        2,
    )
    ordered_columns = [
        "Project_ID",
        "Portfolio_Segment",
        "Region",
        "Delivery_Model",
        "Planning_Mode",
        "Complexity_Score",
        "Planned_Duration_Days",
        "Actual_Duration_Days",
        "Delay_Days",
        "Delay_Flag",
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
        "Outcome_Risk_Level",
    ]
    return df[ordered_columns]


def generate_monitoring_dataset(
    rng: np.random.Generator,
    portfolio_df: pd.DataFrame,
    n_rows: int,
) -> pd.DataFrame:
    sample = portfolio_df.sample(n=min(n_rows, len(portfolio_df)), replace=n_rows > len(portfolio_df), random_state=42)
    months = pd.date_range("2025-07-01", periods=9, freq="MS")
    chosen_months = rng.choice(months, size=n_rows)
    actual_risk = sample["Outcome_Risk_Level"].to_numpy()

    confidence = np.clip(
        0.58 + 0.22 * (sample["Planning_Mode"].eq("AI-Assisted")).astype(float).to_numpy()
        + rng.normal(0, 0.07, n_rows),
        0.40,
        0.97,
    )

    predicted_risk = actual_risk.copy()
    risk_order = np.array(["Low", "Medium", "High"])
    for idx in range(n_rows):
        if rng.random() > confidence[idx]:
            current = int(np.where(risk_order == actual_risk[idx])[0][0])
            shift = rng.choice([-1, 1])
            predicted_risk[idx] = risk_order[int(np.clip(current + shift, 0, 2))]

    p80_forecast_days = (
        sample["Planned_Duration_Days"].to_numpy()
        + sample["Forecast_Error_Days"].to_numpy()
        + rng.integers(4, 14, size=n_rows)
    )
    actual_completion_days = sample["Actual_Duration_Days"].to_numpy()
    absolute_forecast_error = np.abs(p80_forecast_days - actual_completion_days)

    drift_score = np.clip(
        0.18
        + 0.24 * sample["Procurement_Risk_Index"].to_numpy() / 100
        + 0.20 * sample["Requirements_Volatility_Score"].to_numpy() / 100
        + rng.normal(0, 0.05, n_rows),
        0.05,
        0.95,
    )
    alerts_open = np.where(drift_score > 0.55, rng.integers(1, 4, size=n_rows), 0)

    return pd.DataFrame(
        {
            "Snapshot_Month": pd.to_datetime(chosen_months).strftime("%Y-%m-%d"),
            "Project_ID": sample["Project_ID"].to_numpy(),
            "Portfolio_Segment": sample["Portfolio_Segment"].to_numpy(),
            "Model_Version": "v1-advisory-multimodel",
            "Predicted_Risk_Level": predicted_risk,
            "Actual_Risk_Level": actual_risk,
            "Prediction_Confidence": np.round(confidence, 3),
            "P80_Forecast_Days": p80_forecast_days.astype(int),
            "Actual_Completion_Days": actual_completion_days.astype(int),
            "Absolute_Forecast_Error_Days": absolute_forecast_error.astype(int),
            "Drift_Score": np.round(drift_score, 3),
            "Alerts_Open": alerts_open.astype(int),
        }
    ).sort_values(["Snapshot_Month", "Project_ID"]).reset_index(drop=True)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def main() -> None:
    args = parse_args()
    rng = np.random.default_rng(args.seed)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    task_df = generate_task_risk_dataset(rng, args.task_rows)
    portfolio_df = generate_project_portfolio_dataset(rng, args.project_rows)
    monitoring_df = generate_monitoring_dataset(rng, portfolio_df, args.monitor_rows)

    task_path = out_dir / "construction_dataset.csv"
    portfolio_path = out_dir / "project_portfolio_history.csv"
    monitoring_path = out_dir / "risk_monitoring_snapshot.csv"

    write_csv(task_df, task_path)
    write_csv(portfolio_df, portfolio_path)
    write_csv(monitoring_df, monitoring_path)

    print(f"Wrote {task_path} rows={len(task_df)}")
    print(task_df['Risk_Level'].value_counts().sort_index().to_string())
    print(f"\nWrote {portfolio_path} rows={len(portfolio_df)}")
    print(portfolio_df['Delay_Flag'].value_counts().to_string())
    print(f"\nWrote {monitoring_path} rows={len(monitoring_df)}")
    match_rate = (monitoring_df["Predicted_Risk_Level"] == monitoring_df["Actual_Risk_Level"]).mean()
    print(f"monitoring_match_rate={match_rate:.3f}")


if __name__ == "__main__":
    main()
