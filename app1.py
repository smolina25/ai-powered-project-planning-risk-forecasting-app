from __future__ import annotations

import copy
import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from textwrap import dedent
from typing import Any

import pandas as pd
import streamlit as st

from src.ai.task_generator import generate_task_plan
from src.analytics.metrics import compute_metrics
from src.analytics.risk_drivers import rank_delay_drivers
from src.analytics.scenarios import scenario_comparison
from src.config import settings
from src.ml.predictor import RiskModelStatus, load_risk_model
from src.ml.service import build_default_feature_df, score_tasks
from src.modeling.critical_path import critical_path_by_mean
from src.modeling.graph_builder import build_project_graph
from src.simulation.monte_carlo import run_monte_carlo
from src.utils.errors import GraphValidationError, TaskGenerationError
from src.visualization.charts import (
    completion_histogram,
    dependency_graph_figure,
    risk_drivers_bar,
    scenario_comparison_chart,
)


st.set_page_config(
    page_title="certAIn | SaaS Experience",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="collapsed",
)


NAV_ITEMS = [
    ("home", "Home"),
    ("product", "Product"),
    ("forecasting", "AI Forecasting"),
    ("monte-carlo", "Monte Carlo"),
    ("pricing", "Pricing"),
    ("dashboard", "Dashboard"),
    ("about", "About Us"),
]

PAGE_TITLES = {key: label for key, label in NAV_ITEMS}
PAGE_TITLES["login"] = "Login"

DEFAULT_SAMPLE = "Digital Product Launch"

SAMPLE_SCENARIOS: dict[str, dict[str, Any]] = {
    "Digital Product Launch": {
        "description": (
            "Launch a B2B analytics SaaS with SSO, subscription billing, AI forecast pages, "
            "and an executive dashboard for pilot customers."
        ),
        "deadline": 96.0,
        "iterations": 1200,
        "max_tasks": 10,
        "tasks": [
            {"id": "T1", "name": "Product scope and requirements", "mean_duration": 6, "std_dev": 1.4, "dependencies": [], "risk_factor": 0.24},
            {"id": "T2", "name": "Platform architecture and security design", "mean_duration": 8, "std_dev": 2.0, "dependencies": ["T1"], "risk_factor": 0.33},
            {"id": "T3", "name": "Core application build", "mean_duration": 18, "std_dev": 4.5, "dependencies": ["T2"], "risk_factor": 0.44},
            {"id": "T4", "name": "Billing and subscription workflow", "mean_duration": 10, "std_dev": 3.0, "dependencies": ["T2"], "risk_factor": 0.48},
            {"id": "T5", "name": "SSO and identity controls", "mean_duration": 9, "std_dev": 2.6, "dependencies": ["T2"], "risk_factor": 0.4},
            {"id": "T6", "name": "AI forecasting experience", "mean_duration": 12, "std_dev": 3.1, "dependencies": ["T3"], "risk_factor": 0.46},
            {"id": "T7", "name": "Integration and data contracts", "mean_duration": 11, "std_dev": 3.7, "dependencies": ["T3", "T4", "T5"], "risk_factor": 0.56},
            {"id": "T8", "name": "Pilot QA and hardening", "mean_duration": 13, "std_dev": 4.0, "dependencies": ["T6", "T7"], "risk_factor": 0.59},
            {"id": "T9", "name": "Executive reporting and rollout", "mean_duration": 6, "std_dev": 1.8, "dependencies": ["T8"], "risk_factor": 0.28},
        ],
    },
    "ERP Transformation": {
        "description": (
            "Roll out an ERP transformation across finance, procurement, and operations with "
            "data migration, vendor coordination, training, and cutover readiness."
        ),
        "deadline": 142.0,
        "iterations": 1400,
        "max_tasks": 11,
        "tasks": [
            {"id": "T1", "name": "Program charter and scope alignment", "mean_duration": 9, "std_dev": 1.7, "dependencies": [], "risk_factor": 0.21},
            {"id": "T2", "name": "Current-state process mapping", "mean_duration": 12, "std_dev": 2.5, "dependencies": ["T1"], "risk_factor": 0.31},
            {"id": "T3", "name": "ERP configuration blueprint", "mean_duration": 16, "std_dev": 3.2, "dependencies": ["T2"], "risk_factor": 0.39},
            {"id": "T4", "name": "Data migration design", "mean_duration": 14, "std_dev": 3.8, "dependencies": ["T2"], "risk_factor": 0.47},
            {"id": "T5", "name": "Vendor and integration build", "mean_duration": 18, "std_dev": 4.3, "dependencies": ["T3"], "risk_factor": 0.52},
            {"id": "T6", "name": "Master data cleansing", "mean_duration": 15, "std_dev": 4.1, "dependencies": ["T4"], "risk_factor": 0.55},
            {"id": "T7", "name": "User training and change management", "mean_duration": 11, "std_dev": 2.4, "dependencies": ["T3"], "risk_factor": 0.34},
            {"id": "T8", "name": "System integration testing", "mean_duration": 13, "std_dev": 3.6, "dependencies": ["T5", "T6"], "risk_factor": 0.61},
            {"id": "T9", "name": "Cutover rehearsal", "mean_duration": 8, "std_dev": 2.2, "dependencies": ["T7", "T8"], "risk_factor": 0.43},
            {"id": "T10", "name": "Go-live and stabilization", "mean_duration": 10, "std_dev": 2.8, "dependencies": ["T9"], "risk_factor": 0.37},
        ],
    },
    "Infrastructure Modernization": {
        "description": (
            "Modernize a smart operations platform with edge sensors, data pipelines, a command "
            "dashboard, and a phased deployment across multiple sites."
        ),
        "deadline": 128.0,
        "iterations": 1100,
        "max_tasks": 10,
        "tasks": [
            {"id": "T1", "name": "Site discovery and rollout sequencing", "mean_duration": 8, "std_dev": 1.8, "dependencies": [], "risk_factor": 0.26},
            {"id": "T2", "name": "Network and platform architecture", "mean_duration": 11, "std_dev": 2.3, "dependencies": ["T1"], "risk_factor": 0.34},
            {"id": "T3", "name": "Sensor procurement and logistics", "mean_duration": 13, "std_dev": 3.4, "dependencies": ["T1"], "risk_factor": 0.49},
            {"id": "T4", "name": "Data ingestion pipeline build", "mean_duration": 15, "std_dev": 3.1, "dependencies": ["T2"], "risk_factor": 0.42},
            {"id": "T5", "name": "Control dashboard implementation", "mean_duration": 14, "std_dev": 2.9, "dependencies": ["T2"], "risk_factor": 0.37},
            {"id": "T6", "name": "Site installation wave one", "mean_duration": 16, "std_dev": 4.6, "dependencies": ["T3"], "risk_factor": 0.57},
            {"id": "T7", "name": "Telemetry integration and validation", "mean_duration": 12, "std_dev": 3.0, "dependencies": ["T4", "T6"], "risk_factor": 0.51},
            {"id": "T8", "name": "Alerting and forecasting layer", "mean_duration": 11, "std_dev": 2.4, "dependencies": ["T5", "T7"], "risk_factor": 0.45},
            {"id": "T9", "name": "Site deployment wave two", "mean_duration": 14, "std_dev": 4.3, "dependencies": ["T7"], "risk_factor": 0.54},
            {"id": "T10", "name": "Operational handover", "mean_duration": 7, "std_dev": 1.5, "dependencies": ["T8", "T9"], "risk_factor": 0.25},
        ],
    },
}

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@400;500;600;700;800&display=swap');

:root {
  --bg: #020711;
  --bg-soft: #071321;
  --bg-card: rgba(7, 18, 31, 0.74);
  --bg-card-strong: rgba(10, 20, 34, 0.92);
  --line: rgba(109, 165, 255, 0.17);
  --line-strong: rgba(109, 165, 255, 0.28);
  --text: #f4f8ff;
  --muted: #9eb0cb;
  --blue: #64a2ff;
  --blue-strong: #4c8af4;
  --cyan: #76e7ff;
  --teal: #18d1c7;
  --gold: #f5c56b;
  --rose: #ff7f8c;
  --shadow: 0 28px 90px rgba(0, 0, 0, 0.46);
  --radius-xl: 30px;
  --radius-lg: 24px;
  --radius-md: 18px;
  --radius-sm: 14px;
  --max-width: 1240px;
}

html, body, [class*="css"] {
  font-family: "Manrope", sans-serif;
}

body {
  color: var(--text);
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
#MainMenu,
footer {
  display: none !important;
  visibility: hidden !important;
}

[data-testid="stSidebar"] {
  display: none !important;
}

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {
  background:
    radial-gradient(circle at 18% 12%, rgba(24, 110, 255, 0.14), transparent 24%),
    radial-gradient(circle at 80% 24%, rgba(25, 210, 201, 0.12), transparent 20%),
    linear-gradient(180deg, #030811 0%, #02060d 100%) !important;
  color: var(--text) !important;
}

.block-container {
  max-width: var(--max-width) !important;
  padding-top: 1.1rem !important;
  padding-bottom: 4rem !important;
}

.saas-shell {
  position: relative;
  min-height: 100vh;
}

.starfield {
  position: fixed;
  inset: 0;
  z-index: -2;
  pointer-events: none;
  opacity: 0.55;
  background-image:
    radial-gradient(circle, rgba(196, 221, 255, 0.85) 0 1px, transparent 1.45px),
    radial-gradient(circle, rgba(196, 221, 255, 0.38) 0 1px, transparent 1.7px),
    radial-gradient(circle, rgba(91, 157, 255, 0.22) 0 1px, transparent 2px);
  background-size: 220px 220px, 310px 310px, 420px 420px;
  background-position: 0 0, 90px 120px, 180px 60px;
}

.ambient-orb {
  position: fixed;
  border-radius: 999px;
  filter: blur(90px);
  opacity: 0.48;
  z-index: -1;
  pointer-events: none;
}

.orb-a {
  width: 16rem;
  height: 16rem;
  top: 7rem;
  left: 7%;
  background: rgba(40, 110, 255, 0.24);
}

.orb-b {
  width: 20rem;
  height: 20rem;
  top: 18rem;
  right: 7%;
  background: rgba(25, 210, 201, 0.14);
}

.nav-shell,
.hero-shell,
.page-shell,
.footer-shell {
  width: min(100%, var(--max-width));
  margin-inline: auto;
}

.nav-shell {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 0.7rem 0 1rem;
  backdrop-filter: blur(18px);
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  color: var(--text);
}

.brand-mark {
  width: 46px;
  height: 46px;
  border-radius: 14px;
  position: relative;
  display: grid;
  place-items: center;
  background: linear-gradient(180deg, rgba(5, 10, 19, 0.96), rgba(2, 7, 17, 0.88));
  border: 1px solid rgba(112, 165, 255, 0.16);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
}

.brand-mark.small {
  width: 40px;
  height: 40px;
}

.brand-triangle {
  position: absolute;
  width: 18px;
  height: 21px;
  background: linear-gradient(180deg, rgba(73, 134, 255, 0.95), rgba(72, 223, 255, 0.78));
  clip-path: polygon(50% 0%, 100% 100%, 0% 100%);
  top: 8px;
}

.brand-core {
  position: absolute;
  bottom: 6px;
  font-family: "Sora", sans-serif;
  font-size: 0.8rem;
  font-weight: 700;
  color: rgba(230, 241, 255, 0.84);
}

.brand-word {
  font-family: "Sora", sans-serif;
  font-weight: 700;
  font-size: 1.8rem;
  letter-spacing: -0.04em;
}

.nav-pills,
.cta-row,
.stats-strip,
.trust-row,
.footer-meta,
.footer-grid,
.feature-grid,
.split-grid,
.quote-grid,
.pricing-grid,
.scenario-card-grid {
  display: flex;
}

.nav-pills {
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  padding: 10px 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 999px;
  background: rgba(5, 12, 24, 0.54);
}

.nav-pills a,
.footer-grid a,
.footer-grid span,
.text-link {
  color: var(--muted);
  text-decoration: none;
}

.nav-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 15px;
  border-radius: 14px;
  transition: background 160ms ease, color 160ms ease, transform 160ms ease;
}

.nav-link:hover,
.nav-link.active {
  color: var(--text);
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-1px);
}

.nav-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.text-link {
  font-weight: 600;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 0 20px;
  border-radius: 16px;
  text-decoration: none;
  font-weight: 700;
  transition: transform 160ms ease, box-shadow 160ms ease, background 160ms ease;
}

.btn:hover {
  transform: translateY(-1px);
}

.btn-primary {
  color: #fff;
  background: linear-gradient(180deg, var(--blue) 0%, var(--blue-strong) 100%);
  box-shadow: 0 16px 40px rgba(77, 137, 245, 0.34);
}

.btn-secondary {
  color: var(--text);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.hero-shell {
  padding-top: 1.6rem;
}

.hero-grid,
.page-grid,
.dashboard-hero-grid {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 22px;
}

.glass {
  border: 1px solid var(--line);
  border-radius: var(--radius-xl);
  background: linear-gradient(180deg, rgba(10, 20, 34, 0.92), rgba(5, 12, 24, 0.74));
  box-shadow: var(--shadow);
}

.hero-card {
  padding: 2.4rem;
}

.kicker {
  display: inline-flex;
  align-items: center;
  padding: 0.34rem 0.7rem;
  border-radius: 999px;
  border: 1px solid rgba(118, 231, 255, 0.22);
  color: var(--cyan);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hero-title,
.page-title {
  margin: 1rem 0 0.8rem;
  font-family: "Sora", sans-serif;
  font-size: clamp(2.6rem, 5vw, 4.2rem);
  line-height: 1.02;
  letter-spacing: -0.06em;
}

.page-title {
  font-size: clamp(2rem, 4vw, 3rem);
}

.hero-subtitle,
.page-copy,
.section-copy,
.eyebrow-copy {
  color: var(--muted);
  font-size: 1.04rem;
  line-height: 1.75;
}

.cta-row {
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 1.6rem;
}

.stats-strip {
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 1.6rem;
}

.stat-pill,
.mini-pill,
.status-chip,
.plan-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0.72rem 0.95rem;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.07);
  background: rgba(255, 255, 255, 0.03);
}

.stat-pill strong,
.metric-card strong,
.workspace-card strong,
.timeline-card strong,
.scenario-mini-card strong {
  display: block;
  font-family: "Sora", sans-serif;
}

.insight-card {
  padding: 2rem;
}

.insight-stack {
  display: grid;
  gap: 14px;
}

.info-block,
.feature-card,
.quote-card,
.pricing-card,
.detail-card,
.workspace-card,
.timeline-card,
.scenario-mini-card,
.history-card {
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.03);
}

.info-block,
.workspace-card,
.timeline-card,
.scenario-mini-card,
.history-card,
.detail-card {
  padding: 1.2rem 1.25rem;
}

.section-label {
  margin: 2.4rem 0 0.8rem;
  color: var(--cyan);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.section-heading {
  margin: 0 0 0.55rem;
  font-family: "Sora", sans-serif;
  font-size: clamp(1.6rem, 3vw, 2.25rem);
  letter-spacing: -0.04em;
}

.section-copy {
  margin-top: 0;
}

.feature-grid,
.quote-grid,
.pricing-grid,
.scenario-card-grid {
  flex-wrap: wrap;
  gap: 16px;
}

.feature-card,
.quote-card,
.pricing-card {
  flex: 1 1 220px;
  padding: 1.4rem;
}

.feature-card h3,
.quote-card h3,
.pricing-card h3,
.detail-card h3 {
  margin: 0.5rem 0;
  font-family: "Sora", sans-serif;
  font-size: 1.05rem;
}

.feature-card p,
.quote-card p,
.pricing-card p,
.detail-card p,
.detail-card li,
.info-block p {
  color: var(--muted);
  line-height: 1.7;
}

.badge-dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  background: linear-gradient(180deg, var(--teal), var(--blue));
  box-shadow: 0 0 0 8px rgba(25, 210, 201, 0.09);
}

.quote-card span,
.pricing-tag,
.eyebrow {
  color: var(--cyan);
  font-weight: 700;
  font-size: 0.86rem;
}

.page-shell {
  padding-top: 1.2rem;
}

.page-hero-card {
  padding: 2rem 2.1rem;
}

.detail-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.dashboard-banner {
  padding: 1.6rem 1.8rem;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin: 1.5rem 0;
}

.metric-card {
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.03);
  padding: 1rem 1.1rem;
}

.metric-card span {
  color: var(--muted);
  font-size: 0.88rem;
}

.metric-card strong {
  margin-top: 0.38rem;
  font-size: 1.75rem;
  letter-spacing: -0.05em;
}

.metric-card small {
  display: block;
  margin-top: 0.5rem;
  color: var(--muted);
}

.status-chip {
  width: fit-content;
  padding: 0.4rem 0.8rem;
  border-radius: 999px;
  font-weight: 700;
}

.chip-high {
  color: #ffd4d8;
  border-color: rgba(255, 127, 140, 0.28);
  background: rgba(255, 127, 140, 0.12);
}

.chip-medium {
  color: #ffe7bc;
  border-color: rgba(245, 197, 107, 0.28);
  background: rgba(245, 197, 107, 0.11);
}

.chip-low {
  color: #cbfff7;
  border-color: rgba(24, 209, 199, 0.22);
  background: rgba(24, 209, 199, 0.11);
}

.workspace-card p,
.timeline-card p,
.history-card p {
  color: var(--muted);
  line-height: 1.65;
}

.data-pair {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  padding: 0.55rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.data-pair:last-child {
  border-bottom: none;
}

.timeline-grid,
.workspace-grid {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 16px;
}

.task-list {
  display: grid;
  gap: 12px;
}

.task-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 0.85rem 1rem;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  background: rgba(255, 255, 255, 0.025);
}

.task-item span {
  color: var(--muted);
}

.scenario-card-grid {
  margin-top: 0.8rem;
}

.scenario-mini-card h4 {
  margin: 0.2rem 0 0.45rem;
  font-family: "Sora", sans-serif;
}

.scenario-mini-card p {
  margin: 0;
}

.history-list {
  display: grid;
  gap: 12px;
}

.history-item {
  padding: 0.95rem 1rem;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(255, 255, 255, 0.03);
}

.history-item strong {
  display: block;
  font-family: "Sora", sans-serif;
}

.history-item span {
  color: var(--muted);
  font-size: 0.94rem;
}

.footer-shell {
  margin-top: 3rem;
  padding: 1.6rem 0 0.6rem;
}

.footer-card {
  padding: 1.6rem;
}

.footer-grid {
  justify-content: space-between;
  gap: 22px;
  flex-wrap: wrap;
}

.footer-grid div {
  min-width: 150px;
}

.footer-grid h4 {
  margin: 0 0 0.6rem;
  font-family: "Sora", sans-serif;
  font-size: 0.98rem;
}

.footer-grid a,
.footer-grid span {
  display: block;
  margin-top: 0.45rem;
}

.footer-meta {
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  margin-top: 1.2rem;
  color: var(--muted);
}

.dashboard-note {
  margin-top: 0.6rem;
  color: var(--muted);
  line-height: 1.75;
}

.login-panel {
  padding: 1.7rem;
}

div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] textarea {
  background: rgba(255, 255, 255, 0.03) !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  color: var(--text) !important;
  border-radius: 16px !important;
}

div[data-testid="stTextArea"] label,
div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stRadio"] label {
  color: var(--text) !important;
  font-weight: 600 !important;
}

div[data-testid="stNumberInput"] button {
  color: var(--muted) !important;
}

div.stButton > button,
div.stDownloadButton > button {
  min-height: 48px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: white;
  background: linear-gradient(180deg, var(--blue) 0%, var(--blue-strong) 100%);
  box-shadow: 0 14px 38px rgba(77, 137, 245, 0.22);
  font-weight: 700;
}

div.stButton > button[kind="secondary"] {
  background: rgba(255, 255, 255, 0.04);
  box-shadow: none;
}

div[data-testid="stMarkdownContainer"] p code {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text);
}

div[data-testid="stPlotlyChart"] {
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.03);
  padding: 0.6rem;
}

div[data-testid="stDataFrame"] {
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 24px;
  overflow: hidden;
}

div[data-testid="stAlert"] {
  border-radius: 18px;
}

@media (max-width: 1100px) {
  .nav-shell,
  .hero-grid,
  .page-grid,
  .dashboard-hero-grid,
  .timeline-grid,
  .workspace-grid {
    grid-template-columns: 1fr;
  }

  .nav-shell {
    position: relative;
    flex-direction: column;
    align-items: flex-start;
  }

  .nav-pills,
  .nav-actions {
    width: 100%;
  }
}

@media (max-width: 900px) {
  .kpi-grid,
  .detail-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .block-container {
    padding-left: 0.9rem !important;
    padding-right: 0.9rem !important;
  }

  .nav-link {
    width: calc(50% - 6px);
  }

  .nav-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .kpi-grid,
  .detail-grid {
    grid-template-columns: 1fr;
  }

  .hero-card,
  .insight-card,
  .page-hero-card,
  .dashboard-banner {
    padding: 1.45rem;
  }
}
</style>
"""


def _get_query_param(name: str, default: str) -> str:
    try:
        value = st.query_params.get(name, default)
    except Exception:
        legacy = st.experimental_get_query_params()
        value = legacy.get(name, [default])

    if isinstance(value, list):
        return str(value[0]) if value else default
    return str(value)


def _set_query_page(page: str) -> None:
    try:
        st.query_params["page"] = page
    except Exception:
        st.experimental_set_query_params(page=page)


def _resolve_page() -> str:
    page = _get_query_param("page", "home").strip().lower() or "home"
    return page if page in PAGE_TITLES else "home"


def _href(page: str) -> str:
    return f"?page={page}"


def _inject_styles() -> None:
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <div class="saas-shell">
          <div class="starfield" aria-hidden="true"></div>
          <div class="ambient-orb orb-a"></div>
          <div class="ambient-orb orb-b"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_nav(active_page: str) -> None:
    nav_links = "".join(
        f'<a href="{_href(page)}" class="nav-link {"active" if page == active_page else ""}">{label}</a>'
        for page, label in NAV_ITEMS
    )
    st.markdown(
        dedent(
            f"""
            <div class="nav-shell">
              <a class="brand" href="{_href("home")}">
                <div class="brand-mark" aria-hidden="true">
                  <span class="brand-triangle"></span>
                  <span class="brand-core">A</span>
                </div>
                <span class="brand-word">certAIn</span>
              </a>
              <div class="nav-pills">{nav_links}</div>
              <div class="nav-actions">
                <a href="{_href("login")}" class="text-link">Login</a>
                <a href="{_href("dashboard")}" class="btn btn-primary">Start Free Trial</a>
              </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def _render_footer() -> None:
    st.markdown(
        dedent(
            f"""
            <div class="footer-shell">
              <div class="glass footer-card">
                <div class="footer-grid">
                  <div>
                    <a class="brand" href="{_href("home")}">
                      <div class="brand-mark small" aria-hidden="true">
                        <span class="brand-triangle"></span>
                        <span class="brand-core">A</span>
                      </div>
                      <span class="brand-word">certAIn</span>
                    </a>
                    <p class="dashboard-note">
                      AI-powered forecasting with Monte Carlo simulation, workflow reasoning,
                      and stakeholder-ready decision support.
                    </p>
                  </div>
                  <div>
                    <h4>Product</h4>
                    <a href="{_href("product")}">Features</a>
                    <a href="{_href("forecasting")}">AI Forecasting</a>
                    <a href="{_href("monte-carlo")}">Monte Carlo</a>
                    <a href="{_href("dashboard")}">Dashboard</a>
                  </div>
                  <div>
                    <h4>Company</h4>
                    <a href="{_href("about")}">About Us</a>
                    <a href="{_href("pricing")}">Pricing</a>
                    <a href="{_href("login")}">Login</a>
                  </div>
                  <div>
                    <h4>Use Case</h4>
                    <span>Capstone presentation</span>
                    <span>Portfolio demo</span>
                    <span>Live product walkthrough</span>
                  </div>
                </div>
                <div class="footer-meta">
                  <span>&copy; 2026 certAIn</span>
                  <span>AI Planning</span>
                  <span>Risk Forecasting</span>
                  <span>Scenario Lab</span>
                </div>
              </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def _section_intro(label: str, title: str, body: str) -> None:
    st.markdown(
        dedent(
            f"""
            <div class="page-shell">
              <div class="section-label">{label}</div>
              <h2 class="section-heading">{title}</h2>
              <p class="section-copy">{body}</p>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def _risk_level(delay_probability: float) -> str:
    if delay_probability < 0.25:
        return "low"
    if delay_probability < 0.55:
        return "medium"
    return "high"


def _confidence_score(metrics: dict[str, float]) -> float:
    spread_penalty = max(0.0, metrics["p80"] - metrics["p50"]) * 0.42
    delay_penalty = metrics["delay_probability"] * 48.0
    confidence = 96.0 - spread_penalty - delay_penalty
    return round(max(58.0, min(96.0, confidence)), 1)


def _narrative(metrics: dict[str, float], top_driver: str | None) -> str:
    risk = _risk_level(metrics["delay_probability"]).upper()
    driver_text = f" Primary pressure point: {top_driver}." if top_driver else ""
    return (
        f"Forecast posture: {risk}. The model estimates a {metrics['delay_probability'] * 100:.1f}% chance "
        f"of missing the target date. A safer stakeholder commitment is {metrics['p80']:.1f} days.{driver_text}"
    )


def _theme_chart(figure: Any) -> Any:
    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font_color="#f4f8ff",
        margin=dict(l=30, r=20, t=70, b=30),
    )
    figure.update_xaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.08)",
    )
    figure.update_yaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.08)",
    )
    return figure


def _init_state() -> None:
    defaults = {
        "saas_selected_sample": DEFAULT_SAMPLE,
        "saas_project_text": SAMPLE_SCENARIOS[DEFAULT_SAMPLE]["description"],
        "saas_mode": "mock",
        "saas_deadline": SAMPLE_SCENARIOS[DEFAULT_SAMPLE]["deadline"],
        "saas_iterations": SAMPLE_SCENARIOS[DEFAULT_SAMPLE]["iterations"],
        "saas_max_tasks": SAMPLE_SCENARIOS[DEFAULT_SAMPLE]["max_tasks"],
        "saas_seed": 17,
        "saas_payload": None,
        "saas_history": [],
        "saas_user_email": "team@certain.ai",
        "saas_bootstrapped": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


@st.cache_resource
def _load_risk_model_bundle() -> tuple[Any | None, RiskModelStatus]:
    model_path = settings.risk_model_path_file
    if not model_path.is_absolute():
        model_path = Path.cwd() / model_path

    return load_risk_model(
        enabled=settings.risk_model_enabled,
        model_path=model_path,
        model_version=settings.risk_model_version,
    )


def _load_selected_sample() -> None:
    sample = SAMPLE_SCENARIOS.get(st.session_state.saas_selected_sample)
    if not sample:
        return
    st.session_state.saas_project_text = sample["description"]
    st.session_state.saas_deadline = sample["deadline"]
    st.session_state.saas_iterations = sample["iterations"]
    st.session_state.saas_max_tasks = sample["max_tasks"]


def _build_tasks() -> list[dict[str, Any]]:
    selected_sample = st.session_state.saas_selected_sample
    if st.session_state.saas_mode == "mock" and selected_sample in SAMPLE_SCENARIOS:
        return copy.deepcopy(SAMPLE_SCENARIOS[selected_sample]["tasks"])

    plan = generate_task_plan(
        st.session_state.saas_project_text,
        max_tasks=int(st.session_state.saas_max_tasks),
        mode=st.session_state.saas_mode,
    )
    return [task.model_dump() for task in plan.tasks]


def _run_ml_scoring(
    tasks: list[dict[str, Any]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, RiskModelStatus]:
    model, status = _load_risk_model_bundle()
    features_df = build_default_feature_df(tasks)
    if model is None or not status.available:
        return (
            features_df,
            pd.DataFrame(),
            pd.DataFrame(columns=["Risk_Level", "Count"]),
            status,
        )

    validated_df, scored_df, summary_df = score_tasks(model, features_df)
    return validated_df, scored_df, summary_df, status


def _serialize_payload(payload: dict[str, Any]) -> str:
    safe_payload = {
        "project_text": payload["project_text"],
        "sample": payload["sample"],
        "mode": payload["mode"],
        "deadline_days": payload["deadline_days"],
        "iterations": payload["iterations"],
        "seed": payload["seed"],
        "metrics": payload["metrics"],
        "critical_path": payload["critical_path"],
        "drivers": payload["drivers"],
        "scenarios": payload["scenarios_df"].to_dict(orient="records"),
        "tasks": payload["tasks"],
        "ml_predictions": payload["ml_predictions_df"].to_dict(orient="records"),
        "model_status": payload["model_status"],
    }
    return json.dumps(safe_payload, indent=2)


def _run_forecast() -> None:
    project_text = st.session_state.saas_project_text.strip()
    if not project_text:
        st.error("Project description is required.")
        return

    try:
        with st.spinner("Designing the plan and running the forecast..."):
            tasks = _build_tasks()
            graph = build_project_graph(tasks)
            critical_path, critical_days = critical_path_by_mean(graph)
            completion = run_monte_carlo(
                graph,
                iterations=int(st.session_state.saas_iterations),
                seed=int(st.session_state.saas_seed),
            )
            metrics = compute_metrics(completion, float(st.session_state.saas_deadline))
            drivers = rank_delay_drivers(
                graph,
                iterations=min(500, int(st.session_state.saas_iterations)),
                seed=int(st.session_state.saas_seed),
            )
            scenarios_df = scenario_comparison(
                build_project_graph,
                tasks,
                deadline_days=float(st.session_state.saas_deadline),
                iterations=int(st.session_state.saas_iterations),
                seed=int(st.session_state.saas_seed),
            )
            ml_features_df, ml_predictions_df, ml_summary_df, model_status = _run_ml_scoring(tasks)

        payload = {
            "project_text": project_text,
            "sample": st.session_state.saas_selected_sample,
            "mode": st.session_state.saas_mode,
            "deadline_days": float(st.session_state.saas_deadline),
            "iterations": int(st.session_state.saas_iterations),
            "max_tasks": int(st.session_state.saas_max_tasks),
            "seed": int(st.session_state.saas_seed),
            "tasks": tasks,
            "graph": graph,
            "critical_path": critical_path,
            "critical_path_days": critical_days,
            "completion": completion,
            "metrics": metrics,
            "drivers": drivers,
            "scenarios_df": scenarios_df,
            "ml_features_df": ml_features_df,
            "ml_predictions_df": ml_predictions_df,
            "ml_summary_df": ml_summary_df,
            "model_status": asdict(model_status),
        }
        st.session_state.saas_payload = payload

        top_driver = drivers[0]["task_name"] if drivers else "No dominant driver"
        history_item = {
            "timestamp": datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M UTC"),
            "sample": payload["sample"],
            "title": project_text[:60] + ("..." if len(project_text) > 60 else ""),
            "delay_probability": metrics["delay_probability"],
            "p80": metrics["p80"],
            "top_driver": top_driver,
        }
        st.session_state.saas_history = [history_item, *st.session_state.saas_history[:5]]
    except TaskGenerationError as exc:
        st.error(str(exc))
    except GraphValidationError as exc:
        st.error(f"Generated task graph is invalid: {exc}")
    except Exception as exc:  # noqa: BLE001
        st.error(f"Unable to generate the forecast workspace: {exc}")


def _ensure_demo_payload() -> None:
    if st.session_state.saas_bootstrapped or st.session_state.saas_payload is not None:
        return
    _run_forecast()
    st.session_state.saas_bootstrapped = True


def _history_markup() -> str:
    if not st.session_state.saas_history:
        return "<div class='history-card'><p>No workspaces yet. Launch one from the console.</p></div>"

    items = "".join(
        f"""
        <div class="history-item">
          <strong>{item['sample']}</strong>
          <span>{item['timestamp']}</span>
          <span>{item['delay_probability'] * 100:.1f}% delay risk · P80 {item['p80']:.1f}d</span>
          <span>Primary driver: {item['top_driver']}</span>
        </div>
        """
        for item in st.session_state.saas_history
    )
    return f"<div class='history-list'>{items}</div>"


def _render_home() -> None:
    st.markdown(
        dedent(
            f"""
            <div class="hero-shell">
              <div class="hero-grid">
                <div class="glass hero-card">
                  <span class="kicker">Forecast-first planning</span>
                  <h1 class="hero-title">A SaaS-style planning platform for <span style="color:var(--cyan)">risky delivery decisions</span></h1>
                  <p class="hero-subtitle">
                    certAIn helps teams move from a project brief to an executive-ready commitment
                    using AI planning, Monte Carlo forecasting, risk scoring, and scenario comparison.
                  </p>
                  <div class="cta-row">
                    <a href="{_href("dashboard")}" class="btn btn-primary">Open Live Dashboard</a>
                    <a href="{_href("product")}" class="btn btn-secondary">Explore Product Tour</a>
                  </div>
                  <div class="stats-strip">
                    <div class="stat-pill"><span>Decision cycle</span><strong>&lt; 15 min</strong></div>
                    <div class="stat-pill"><span>Forecast posture</span><strong>P50 / P80 / Risk</strong></div>
                    <div class="stat-pill"><span>Use case</span><strong>PMO + Exec</strong></div>
                  </div>
                </div>
                <div class="glass insight-card">
                  <span class="eyebrow">Command view</span>
                  <div class="insight-stack">
                    <div class="info-block">
                      <strong>Delay probability</strong>
                      <p>Quantify deadline exposure instead of reporting one optimistic date.</p>
                    </div>
                    <div class="info-block">
                      <strong>Scenario recommendation</strong>
                      <p>Compare baseline, mitigation, and acceleration before leadership commits.</p>
                    </div>
                    <div class="info-block">
                      <strong>Explainable signals</strong>
                      <p>Show stakeholders why the plan is fragile and where mitigation is worth it.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    _section_intro(
        "Platform story",
        "Built to feel like a modern SaaS, but grounded in your actual capstone engine",
        "Use this version for judges, coaches, and live walkthroughs when you want the product story and the analytics to feel connected.",
    )

    st.markdown(
        dedent(
            f"""
            <div class="feature-grid">
              <div class="feature-card">
                <div class="badge-dot"></div>
                <h3>AI Project Planning</h3>
                <p>Transform a plain-language brief into structured tasks, dependencies, and risk assumptions.</p>
                <a href="{_href("forecasting")}" class="text-link">Learn more</a>
              </div>
              <div class="feature-card">
                <div class="badge-dot"></div>
                <h3>Monte Carlo Forecasting</h3>
                <p>Simulate schedule outcomes at scale to produce P50, P80, and delay probability.</p>
                <a href="{_href("monte-carlo")}" class="text-link">Learn more</a>
              </div>
              <div class="feature-card">
                <div class="badge-dot"></div>
                <h3>Executive Dashboard</h3>
                <p>Package risk, confidence, scenarios, and actions into presentation-ready outputs.</p>
                <a href="{_href("dashboard")}" class="text-link">Open dashboard</a>
              </div>
              <div class="feature-card">
                <div class="badge-dot"></div>
                <h3>Capstone-ready product layer</h3>
                <p>Present the same visual language across the prototype, live app, and final slides.</p>
                <a href="{_href("about")}" class="text-link">Why it works</a>
              </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    _section_intro(
        "What teams say",
        "Presentation-ready messaging built around risk-aware commitments",
        "The copy below is intentionally product-oriented so the app can double as a presentation surface.",
    )

    st.markdown(
        """
        <div class="quote-grid">
          <div class="quote-card">
            <span>Planning signal</span>
            <p>“The dashboard answers the question stakeholders always ask first: are we still on track?”</p>
          </div>
          <div class="quote-card">
            <span>Forecast signal</span>
            <p>“Monte Carlo replaces a single optimistic deadline with a range we can actually defend.”</p>
          </div>
          <div class="quote-card">
            <span>Decision signal</span>
            <p>“The scenario view makes mitigation tradeoffs clear before the team locks a risky date.”</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        dedent(
            f"""
            <div class="glass dashboard-banner">
              <span class="kicker">Ready for the live walkthrough?</span>
              <h2 class="section-heading">Jump into the interactive workspace and present it like a real product.</h2>
              <p class="dashboard-note">
                The dashboard page uses your forecasting engine, scenario logic, and ML advisory layer to create
                a stronger SaaS-style experience than a static prototype alone.
              </p>
              <div class="cta-row">
                <a href="{_href("dashboard")}" class="btn btn-primary">Launch Workspace</a>
                <a href="{_href("pricing")}" class="btn btn-secondary">See Plans</a>
              </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def _render_product() -> None:
    st.markdown(
        dedent(
            f"""
            <div class="page-shell">
              <div class="page-grid">
                <div class="glass page-hero-card">
                  <span class="kicker">Product</span>
                  <h1 class="page-title">Plan, forecast, and explain risk from one workflow.</h1>
                  <p class="page-copy">
                    certAIn connects project intake, dependency modeling, simulation, advisory ML, and scenario comparison
                    in one SaaS-style interface.
                  </p>
                  <div class="cta-row">
                    <a href="{_href("dashboard")}" class="btn btn-primary">Open Dashboard</a>
                    <a href="{_href("pricing")}" class="btn btn-secondary">View Pricing</a>
                  </div>
                </div>
                <div class="glass page-hero-card">
                  <span class="eyebrow">Core flow</span>
                  <div class="data-pair"><span>1. Project brief</span><strong>AI-assisted intake</strong></div>
                  <div class="data-pair"><span>2. Task graph</span><strong>Dependency reasoning</strong></div>
                  <div class="data-pair"><span>3. Simulation</span><strong>Monte Carlo</strong></div>
                  <div class="data-pair"><span>4. Scenarios</span><strong>Decision-ready</strong></div>
                  <div class="data-pair"><span>5. Executive brief</span><strong>Presentation-safe</strong></div>
                </div>
              </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    _section_intro(
        "Modules",
        "The platform is structured like a SaaS product, not just a notebook demo",
        "Each part of the interface tells a different part of the value story while staying anchored in the same underlying logic.",
    )

    st.markdown(
        dedent(
            f"""
            <div class="detail-grid">
              <div class="detail-card">
                <h3>Brief to plan</h3>
                <p>Generate structured project tasks with durations, dependencies, and risk factors.</p>
                <a href="{_href("forecasting")}" class="text-link">Go deeper</a>
              </div>
              <div class="detail-card">
                <h3>Workflow graph</h3>
                <p>Highlight the critical path and expose where sequence risk becomes schedule risk.</p>
                <a href="{_href("monte-carlo")}" class="text-link">Go deeper</a>
              </div>
              <div class="detail-card">
                <h3>Scenario lab</h3>
                <p>Compare baseline, mitigation, and acceleration paths before promising a deadline.</p>
                <a href="{_href("dashboard")}" class="text-link">Open module</a>
              </div>
              <div class="detail-card">
                <h3>Advisory signals</h3>
                <p>Overlay task-level risk scoring without replacing the probabilistic schedule view.</p>
                <a href="{_href("forecasting")}" class="text-link">Go deeper</a>
              </div>
              <div class="detail-card">
                <h3>Executive outputs</h3>
                <p>Present metrics, delay drivers, and safer commitments in business language.</p>
                <a href="{_href("dashboard")}" class="text-link">See in dashboard</a>
              </div>
              <div class="detail-card">
                <h3>Presentation handoff</h3>
                <p>Reuse the same product language in the prototype, Streamlit app, and final presentation.</p>
                <a href="{_href("about")}" class="text-link">Capstone framing</a>
              </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def _render_forecasting() -> None:
    st.markdown(
        """
        <div class="page-shell">
          <div class="page-grid">
            <div class="glass page-hero-card">
              <span class="kicker">AI Forecasting</span>
              <h1 class="page-title">Turn unstructured project context into forecastable plans.</h1>
              <p class="page-copy">
                The platform uses AI to structure work, expose weak assumptions, and prepare the plan
                for simulation, scenario comparison, and stakeholder discussion.
              </p>
            </div>
            <div class="glass page-hero-card">
              <span class="eyebrow">Forecast inputs</span>
              <div class="data-pair"><span>Tasks generated</span><strong>8-12 scoped items</strong></div>
              <div class="data-pair"><span>Dependencies mapped</span><strong>Directed workflow</strong></div>
              <div class="data-pair"><span>Risk factors prepared</span><strong>Task-level signals</strong></div>
              <div class="data-pair"><span>Model posture</span><strong>Advisory only</strong></div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _section_intro(
        "Why it matters",
        "The AI layer is only useful if it produces decision-safe structure",
        "In this product story, AI is not the outcome. It is the bridge between project ambiguity and a forecast teams can reason about.",
    )

    st.markdown(
        """
        <div class="detail-grid">
          <div class="detail-card">
            <h3>Plan generation</h3>
            <p>Project text becomes a structured task set with durations, dependency order, and assumptions.</p>
          </div>
          <div class="detail-card">
            <h3>Explainability</h3>
            <p>Signals stay readable enough to explain what is driving the forecast and why a mitigation helps.</p>
          </div>
          <div class="detail-card">
            <h3>Decision bridge</h3>
            <p>The output supports commitments, tradeoff discussions, and executive communication instead of just model scores.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_monte_carlo() -> None:
    st.markdown(
        """
        <div class="page-shell">
          <div class="page-grid">
            <div class="glass page-hero-card">
              <span class="kicker">Monte Carlo</span>
              <h1 class="page-title">Replace one optimistic date with a defensible range.</h1>
              <p class="page-copy">
                Run repeated simulations to estimate completion distributions, surface safer commitments,
                and identify how deadline risk changes under different scenarios.
              </p>
            </div>
            <div class="glass page-hero-card">
              <span class="eyebrow">Forecast anchors</span>
              <div class="data-pair"><span>P50 commitment</span><strong>Balanced target</strong></div>
              <div class="data-pair"><span>P80 commitment</span><strong>Safer promise</strong></div>
              <div class="data-pair"><span>Delay probability</span><strong>Leadership signal</strong></div>
              <div class="data-pair"><span>Main driver</span><strong>Mitigation focus</strong></div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _section_intro(
        "Simulation lens",
        "Monte Carlo is the credibility engine behind the dashboard",
        "It transforms schedule uncertainty into metrics the audience can understand: mean completion, P50, P80, and exposure to the chosen deadline.",
    )

    st.markdown(
        """
        <div class="feature-grid">
          <div class="feature-card"><h3>P50</h3><p>The most likely commitment point when normal delivery conditions hold.</p></div>
          <div class="feature-card"><h3>P80</h3><p>A safer promise for executive communication when teams want higher certainty.</p></div>
          <div class="feature-card"><h3>Delay drivers</h3><p>Critical-path frequency reveals which tasks deserve mitigation before launch.</p></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_pricing() -> None:
    st.markdown(
        dedent(
            f"""
            <div class="page-shell">
              <div class="glass page-hero-card">
                <span class="kicker">Pricing</span>
                <h1 class="page-title">Packaging ideas that make the product story feel complete.</h1>
                <p class="page-copy">
                  These plans are illustrative. They help the capstone feel like a SaaS platform with a believable go-to-market story.
                </p>
              </div>
            </div>
            <div class="pricing-grid">
              <div class="pricing-card">
                <span class="pricing-tag">Starter</span>
                <h3>Capstone Demo</h3>
                <p>For judges, coaches, and first walkthroughs.</p>
                <p>Static product story, live dashboard preview, and presentation flow.</p>
                <a href="{_href("dashboard")}" class="btn btn-secondary">Open Demo</a>
              </div>
              <div class="pricing-card">
                <span class="pricing-tag">Most Popular</span>
                <h3>Team Pilot</h3>
                <p>For delivery teams validating risk-aware commitments before launch.</p>
                <p>AI planning, Monte Carlo simulation, scenario comparison, and executive reporting.</p>
                <a href="{_href("login")}" class="btn btn-primary">Start Trial</a>
              </div>
              <div class="pricing-card">
                <span class="pricing-tag">Enterprise</span>
                <h3>Portfolio</h3>
                <p>For PMOs and sponsors coordinating multiple high-risk initiatives.</p>
                <p>Program views, governance reporting, and rollout support for decision forums.</p>
                <a href="{_href("about")}" class="btn btn-secondary">Talk to Team</a>
              </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def _render_about() -> None:
    st.markdown(
        """
        <div class="page-shell">
          <div class="page-grid">
            <div class="glass page-hero-card">
              <span class="kicker">About Us</span>
              <h1 class="page-title">certAIn started as a capstone and evolved into a product story.</h1>
              <p class="page-copy">
                The core question was simple: can teams move from a plain-language brief to a defensible,
                risk-aware commitment in a single planning session?
              </p>
            </div>
            <div class="glass page-hero-card">
              <span class="eyebrow">What it demonstrates</span>
              <div class="data-pair"><span>Business framing</span><strong>Clear questions</strong></div>
              <div class="data-pair"><span>Technical rigor</span><strong>EDA + modeling</strong></div>
              <div class="data-pair"><span>Decision support</span><strong>Scenarios + exports</strong></div>
              <div class="data-pair"><span>Presentation quality</span><strong>Demo-ready</strong></div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _section_intro(
        "Why this format works",
        "The app tells the story your coach wants to see",
        "It bridges business questions, technical modeling, monitoring, deployment, and a live dashboard in one coherent product narrative.",
    )

    st.markdown(
        """
        <div class="detail-grid">
          <div class="detail-card">
            <h3>Business question</h3>
            <p>How likely is the plan to miss the target date, and what safer commitment should be made?</p>
          </div>
          <div class="detail-card">
            <h3>Technical core</h3>
            <p>DAG modeling, Monte Carlo simulation, critical-path analysis, and advisory ML risk scoring.</p>
          </div>
          <div class="detail-card">
            <h3>Presentation outcome</h3>
            <p>A polished capstone product that feels like a SaaS platform rather than a notebook handoff.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_login() -> None:
    st.markdown(
        """
        <div class="page-shell">
          <div class="dashboard-hero-grid">
            <div class="glass login-panel">
              <span class="kicker">Login</span>
              <h1 class="page-title">Access the forecast console</h1>
              <p class="page-copy">
                This is a mock SaaS login experience for the capstone. It keeps the product flow believable
                while routing users directly into the live dashboard.
              </p>
            </div>
            <div class="glass login-panel">
              <span class="eyebrow">What happens next</span>
              <div class="data-pair"><span>Workspace loaded</span><strong>Live demo dashboard</strong></div>
              <div class="data-pair"><span>Default mode</span><strong>Mock-friendly</strong></div>
              <div class="data-pair"><span>Presentation use</span><strong>Click-through flow</strong></div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        email = st.text_input("Work email", value=st.session_state.saas_user_email, key="login_email")
        password = st.text_input("Password", value="demo-password", type="password", key="login_password")
        if st.button("Continue to Dashboard", type="primary", use_container_width=True):
            st.session_state.saas_user_email = email
            _set_query_page("dashboard")
            st.rerun()
    with right:
        st.markdown(
            """
            <div class="history-card">
              <strong style="font-family:Sora,sans-serif;">Why keep this page?</strong>
              <p>
                It makes the app feel like a real SaaS entry point during presentations and gives the
                navigation a complete product arc from landing page to dashboard.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_dashboard() -> None:
    _ensure_demo_payload()
    payload = st.session_state.saas_payload
    model_status = payload["model_status"] if payload else {}
    model_chip = (
        '<span class="status-chip chip-low">ML advisory ready</span>'
        if model_status.get("available", False)
        else '<span class="status-chip chip-medium">Monte Carlo mode</span>'
    )

    st.markdown(
        dedent(
            f"""
            <div class="page-shell">
              <div class="dashboard-hero-grid">
                <div class="glass dashboard-banner">
                  <span class="kicker">Forecast Console</span>
                  <h1 class="page-title">Operate the planning workspace like a real SaaS product.</h1>
                  <p class="page-copy">
                    Generate a plan, quantify deadline risk, compare scenarios, and present a stakeholder-safe recommendation
                    from a single interface.
                  </p>
                  <div class="cta-row">
                    {model_chip}
                    <span class="mini-pill">Default mode: {st.session_state.saas_mode.upper()}</span>
                    <span class="mini-pill">Workspace owner: {st.session_state.saas_user_email}</span>
                  </div>
                </div>
                <div class="glass dashboard-banner">
                  <span class="eyebrow">Workspace pulse</span>
                  <div class="data-pair"><span>Sample scenario</span><strong>{st.session_state.saas_selected_sample}</strong></div>
                  <div class="data-pair"><span>Iterations</span><strong>{int(st.session_state.saas_iterations):,}</strong></div>
                  <div class="data-pair"><span>Deadline</span><strong>{float(st.session_state.saas_deadline):.0f} days</strong></div>
                  <div class="data-pair"><span>Recent workspaces</span><strong>{len(st.session_state.saas_history)}</strong></div>
                </div>
              </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    _section_intro(
        "Launch workspace",
        "Control the briefing flow and run a fresh forecast",
        "Use demo scenarios for presentation speed, or switch to real mode with your Groq key for live task generation.",
    )

    left, right = st.columns([1.18, 0.82], gap="large")
    with left:
        st.selectbox(
            "Demo scenario",
            options=list(SAMPLE_SCENARIOS),
            key="saas_selected_sample",
        )
        st.text_area(
            "Project brief",
            key="saas_project_text",
            height=180,
            placeholder="Describe the project, scope, constraints, and what success looks like.",
        )
        st.radio(
            "Operating mode",
            options=["mock", "real"],
            key="saas_mode",
            horizontal=True,
        )
        if st.session_state.saas_mode == "real" and not settings.groq_api_key:
            st.info("`real` mode needs `GROQ_API_KEY`. Keep `mock` mode for presentation-safe demos.")
    with right:
        st.number_input("Deadline (days)", min_value=10.0, step=1.0, key="saas_deadline")
        st.number_input("Simulation runs", min_value=200, max_value=settings.max_iterations, step=100, key="saas_iterations")
        st.number_input("Max tasks", min_value=8, max_value=18, step=1, key="saas_max_tasks")
        st.number_input("Random seed", min_value=0, max_value=100_000, step=1, key="saas_seed")
        action_a, action_b = st.columns(2)
        with action_a:
            if st.button("Load demo brief", use_container_width=True):
                _load_selected_sample()
                st.rerun()
        with action_b:
            if st.button("Generate forecast", type="primary", use_container_width=True):
                _run_forecast()
                st.rerun()
        st.markdown(
            """
            <div class="history-card">
              <strong style="font-family:Sora,sans-serif;">Presentation tip</strong>
              <p>Open with a saved sample, then edit the brief live so the judges see both product polish and analytics depth.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if not payload:
        return

    metrics = payload["metrics"]
    drivers = payload["drivers"]
    top_driver = drivers[0]["task_name"] if drivers else None
    risk_level = _risk_level(metrics["delay_probability"])
    confidence = _confidence_score(metrics)
    critical_path = payload["critical_path"]
    ml_summary_df = payload["ml_summary_df"]
    scenarios_df = payload["scenarios_df"]
    recommendation = scenarios_df.sort_values("Delay Prob (%)", ascending=True).iloc[0]

    st.markdown(
        dedent(
            f"""
            <div class="kpi-grid">
              <div class="metric-card">
                <span>Delay probability</span>
                <strong>{metrics['delay_probability'] * 100:.1f}%</strong>
                <small>Risk posture: {risk_level.upper()}</small>
              </div>
              <div class="metric-card">
                <span>P80 commitment</span>
                <strong>{metrics['p80']:.1f}d</strong>
                <small>Recommended stakeholder date</small>
              </div>
              <div class="metric-card">
                <span>Forecast confidence</span>
                <strong>{confidence:.0f}%</strong>
                <small>Blends uncertainty spread and delay exposure</small>
              </div>
              <div class="metric-card">
                <span>Primary delay driver</span>
                <strong>{top_driver or "N/A"}</strong>
                <small>Most frequent critical-path pressure point</small>
              </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    summary_col, workspace_col = st.columns([1.16, 0.84], gap="large")
    with summary_col:
        st.markdown(
            dedent(
                f"""
                <div class="workspace-grid">
                  <div class="workspace-card">
                    <span class="eyebrow">Executive narrative</span>
                    <p>{_narrative(metrics, top_driver)}</p>
                  </div>
                  <div class="workspace-card">
                    <span class="eyebrow">Recommended scenario</span>
                    <strong>{recommendation['Scenario']}</strong>
                    <p>
                      Best observed tradeoff in this run. Delay risk drops to {float(recommendation['Delay Prob (%)']):.1f}%
                      with a projected P80 of {float(recommendation['P80 (days)']):.1f} days.
                    </p>
                  </div>
                </div>
                """
            ),
            unsafe_allow_html=True,
        )
    with workspace_col:
        st.markdown(
            f"""
            <div class="history-card">
              <strong style="font-family:Sora,sans-serif;">Recent workspaces</strong>
              {_history_markup()}
            </div>
            """,
            unsafe_allow_html=True,
        )

    hist_col, graph_col = st.columns([1.05, 0.95], gap="large")
    with hist_col:
        histogram = completion_histogram(
            payload["completion"],
            payload["deadline_days"],
            metrics["p50"],
            metrics["p80"],
        )
        st.plotly_chart(_theme_chart(histogram), use_container_width=True)
    with graph_col:
        graph_figure = dependency_graph_figure(payload["graph"], critical_path)
        st.plotly_chart(_theme_chart(graph_figure), use_container_width=True)

    driver_col, scenario_col = st.columns([1.0, 1.0], gap="large")
    with driver_col:
        drivers_df = pd.DataFrame(drivers)
        st.plotly_chart(_theme_chart(risk_drivers_bar(drivers_df)), use_container_width=True)
    with scenario_col:
        st.plotly_chart(_theme_chart(scenario_comparison_chart(scenarios_df)), use_container_width=True)

    path_col, scenario_cards_col = st.columns([0.95, 1.05], gap="large")
    with path_col:
        critical_markup = "".join(
            f"""
            <div class="task-item">
              <div>
                <strong>{task_id}</strong>
                <span>{payload['graph'].nodes[task_id].get('name', task_id)}</span>
              </div>
              <div style="text-align:right;">
                <strong>{float(payload['graph'].nodes[task_id].get('mean_duration', 0.0)):.1f}d</strong>
                <span>mean duration</span>
              </div>
            </div>
            """
            for task_id in critical_path
        )
        st.markdown(
            f"""
            <div class="timeline-card">
              <span class="eyebrow">Critical path</span>
              <strong>{payload['critical_path_days']:.1f} mean days</strong>
              <p>The baseline longest path through the dependency graph.</p>
              <div class="task-list">{critical_markup}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with scenario_cards_col:
        scenario_cards = "".join(
            f"""
            <div class="scenario-mini-card">
              <span class="eyebrow">{row['Scenario']}</span>
              <h4>{float(row['Delay Prob (%)']):.1f}% risk</h4>
              <p>P80 {float(row['P80 (days)']):.1f} days · Mean {float(row['Mean (days)']):.1f} days</p>
              <p class="dashboard-note">{row['Notes']}</p>
            </div>
            """
            for _, row in scenarios_df.iterrows()
        )
        st.markdown(
            f"""
            <div class="timeline-card">
              <span class="eyebrow">Scenario cards</span>
              <p>Use these callouts when presenting the mitigation logic.</p>
              <div class="scenario-card-grid">{scenario_cards}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    tabs = st.tabs(["Task plan", "ML advisory", "Export"])
    with tabs[0]:
        tasks_df = pd.DataFrame(payload["tasks"])
        st.dataframe(tasks_df, use_container_width=True, hide_index=True)
    with tabs[1]:
        if model_status.get("available", False):
            ml_cols = st.columns([0.85, 1.15], gap="large")
            with ml_cols[0]:
                st.dataframe(ml_summary_df, use_container_width=True, hide_index=True)
            with ml_cols[1]:
                st.dataframe(payload["ml_predictions_df"], use_container_width=True, hide_index=True)
        else:
            st.warning(
                "ML advisory scoring is unavailable in this environment. "
                f"Reason: {model_status.get('message', 'Unknown')}"
            )
            st.dataframe(payload["ml_features_df"], use_container_width=True, hide_index=True)
    with tabs[2]:
        st.download_button(
            "Download workspace summary",
            data=_serialize_payload(payload),
            file_name="certain_workspace_summary.json",
            mime="application/json",
            use_container_width=True,
        )
        st.markdown(
            """
            <div class="history-card">
              <strong style="font-family:Sora,sans-serif;">What is included</strong>
              <p>Project brief, metrics, critical path, delay drivers, scenarios, tasks, and ML scoring output.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    _init_state()
    _inject_styles()
    page = _resolve_page()
    _render_nav(page)

    if page == "home":
        _render_home()
    elif page == "product":
        _render_product()
    elif page == "forecasting":
        _render_forecasting()
    elif page == "monte-carlo":
        _render_monte_carlo()
    elif page == "pricing":
        _render_pricing()
    elif page == "about":
        _render_about()
    elif page == "login":
        _render_login()
    else:
        _render_dashboard()

    _render_footer()


if __name__ == "__main__":
    main()
