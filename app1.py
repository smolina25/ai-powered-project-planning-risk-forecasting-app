from __future__ import annotations

import base64
import copy
import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from textwrap import dedent
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
from src.storage.db import init_db
from src.storage.repository import get_run_details, list_recent_runs, save_session_run
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
    initial_sidebar_state="expanded",
)


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
NAV_LOGO_PNG_PATH = ASSETS / "logo-mark.png"
LOGO_PNG_PATH = ASSETS / "logo.png"
LEGACY_LOGO_PNG_PATH = ASSETS / "cetAIn logo.png"
LOGO_SVG_PATH = ASSETS / "logo.svg"


NAV_ITEMS = [
    ("home", "Home"),
    ("product", "Product"),
    ("forecasting", "AI Forecasting"),
    ("monte-carlo", "Monte Carlo"),
    ("pricing", "Pricing"),
    ("dashboard", "Dashboard"),
    ("about", "About Us"),
    ("contact", "Contact Us"),
    ("login", "Login"),
]

PAGE_TITLES = {key: label for key, label in NAV_ITEMS}

DASHBOARD_ITEMS = [
    ("guide", "User Guide"),
    ("decision-hub", "Decision Hub"),
    ("task-architect", "AI Task Architect"),
    ("risk-intelligence", "Risk Intelligence"),
    ("simulator", "Monte Carlo Simulator"),
    ("what-if", "What-If Scenarios"),
    ("history", "Version History"),
    ("summary", "Executive Summary"),
    ("upload", "Project Upload"),
    ("integrations", "Tools Integration"),
    ("settings-page", "Settings"),
]

for key, label in DASHBOARD_ITEMS:
    PAGE_TITLES[key] = label

DASHBOARD_PAGE_KEYS = {key for key, _ in DASHBOARD_ITEMS} | {"dashboard"}

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

HOME_TICKER_ITEMS = [
    "Risk model updated",
    "Schedule optimized",
    "3 anomalies detected",
    "Portfolio drift reviewed",
    "Executive summary refreshed",
    "Resource plan rebalanced",
]

HOME_METRICS = [
    ("Projects Optimized", "2,847", "+18% portfolio throughput"),
    ("Time Saved", "34%", "Planning cycle reduction"),
    ("Risk Accuracy", "94.7%", "Monitoring-backed signal quality"),
    ("Cost Reduction", "$2.1M", "Modeled efficiency upside"),
]

HOME_FEATURES = [
    ("AI Schedule Optimization", "Turn a raw brief into structured timelines, dependencies, and delivery logic."),
    ("Monte Carlo Simulation", "Show P50, P80, and delay probability with a presentation-ready forecast story."),
    ("Risk Intelligence Engine", "Blend advisory ML, portfolio history, and monitoring drift into one view."),
    ("Resource Optimization", "Spot overloaded workstreams and rebalance before the schedule slips."),
    ("Decision Intelligence", "Compare mitigation, baseline, and acceleration options side by side."),
    ("Predictive Analytics", "Connect historical portfolio evidence to your current plan and executive narrative."),
]

HOW_IT_WORKS_STEPS = [
    ("01", "Upload", "Import a brief, spreadsheet, or PM dataset and let certAIn structure the work."),
    ("02", "AI analyzes", "Generate tasks, score risk, simulate completion ranges, and identify fragile assumptions."),
    ("03", "Get insights", "Present dashboards, executive summaries, and scenario recommendations in one workflow."),
]

TRUSTED_BRANDS = [
    "Airbus",
    "Boeing",
    "Siemens",
    "Bosch",
    "Deloitte",
    "Accenture",
    "JPMorgan",
    "PwC",
]

FOOTER_LINK_COLUMNS = [
    (
        "Product",
        [
            ("Features", "product", None),
            ("AI Forecasting", "forecasting", None),
            ("Monte Carlo Simulation", "monte-carlo", None),
            ("Pricing", "pricing", None),
            ("Dashboard", "dashboard", None),
        ],
    ),
    (
        "Company",
        [
            ("About Us", "about", None),
            ("Careers", None, "Coming soon"),
            ("Blog", None, "Coming soon"),
            ("Contact Us", "contact", None),
        ],
    ),
    (
        "Resources",
        [
            ("Documentation", None, "Coming soon"),
            ("API Reference", None, "Coming soon"),
            ("Tools Integration", "integrations", None),
            ("User Guide", "guide", None),
        ],
    ),
    (
        "Legal",
        [
            ("Privacy Policy", None, None),
            ("Terms of Service", None, None),
            ("Cookie Policy", None, None),
            ("Security", None, None),
        ],
    ),
]

FOOTER_SOCIALS = [
    ("linkedin", "LinkedIn"),
    ("x", "X"),
    ("github", "GitHub"),
    ("youtube", "YouTube"),
]

FOOTER_COMPLIANCE = [
    ("ISO", "ISO 27001", "International"),
    ("S2", "SOC2", "USA"),
    ("CA", "CCPA", "California"),
    ("EU", "GDPR", "EU"),
    ("PI", "PIPEDA", "Canada"),
    ("LG", "LGPD", "Brazil"),
    ("AP", "APPI", "Japan"),
]

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@400;500;600;700;800&display=swap');

:root {
  --bg: #020711;
  --bg-soft: #071321;
  --bg-card: rgba(7, 18, 31, 0.74);
  --bg-card-strong: rgba(10, 20, 34, 0.92);
  --purple: #9b5cff;
  --purple-strong: #7a43ff;
  --line: rgba(109, 165, 255, 0.17);
  --line-strong: rgba(109, 165, 255, 0.28);
  --text: #f4f8ff;
  --muted: #9eb0cb;
  --blue: #64a2ff;
  --blue-strong: #4c8af4;
  --brand-blue-base: #0b6fd6;
  --brand-blue-accent: #5ca9ff;
  --cyan: #76e7ff;
  --teal: #18d1c7;
  --gold: #f5c56b;
  --rose: #ff7f8c;
  --shadow: 0 28px 90px rgba(0, 0, 0, 0.46);
  --radius-xl: 30px;
  --radius-lg: 24px;
  --radius-md: 18px;
  --radius-sm: 14px;
  --content-width: 1240px;
  --nav-width: 1760px;
  --max-width: var(--content-width);
}

::selection {
  background: rgba(100, 162, 255, 0.32);
  color: #ffffff;
}

html, body, [class*="css"] {
  font-family: "Manrope", sans-serif;
}

body {
  color: var(--text);
}

a {
  color: inherit;
}

@keyframes floatDrift {
  0% { transform: translate3d(0, 0, 0) scale(1); }
  50% { transform: translate3d(0, -14px, 0) scale(1.04); }
  100% { transform: translate3d(0, 0, 0) scale(1); }
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

@keyframes tickerSlide {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}

@keyframes scanDrift {
  0% { transform: translateY(-125%); opacity: 0; }
  20% { opacity: 0.55; }
  80% { opacity: 0.18; }
  100% { transform: translateY(130%); opacity: 0; }
}

@keyframes pulseGlow {
  0%, 100% { box-shadow: 0 0 0 rgba(122, 67, 255, 0); }
  50% { box-shadow: 0 0 0 1px rgba(155, 92, 255, 0.18), 0 24px 64px rgba(76, 138, 244, 0.22); }
}

@keyframes previewShellSweep {
  0% { transform: translateX(-120%); opacity: 0; }
  18% { opacity: 0.32; }
  55% { opacity: 0.14; }
  100% { transform: translateX(135%); opacity: 0; }
}

@keyframes previewCardFloat {
  0%, 100% { transform: translate3d(0, 0, 0); }
  50% { transform: translate3d(0, -8px, 0); }
}

@keyframes chartBarLift {
  0%, 100% { transform: translateY(0) scaleY(1); filter: brightness(1); }
  50% { transform: translateY(-4px) scaleY(1.05); filter: brightness(1.12); }
}

@keyframes alertSweep {
  0% { transform: translateX(-130%); opacity: 0; }
  20% { opacity: 0.2; }
  100% { transform: translateX(135%); opacity: 0; }
}

@keyframes alertPulse {
  0%, 100% { box-shadow: none; }
  50% { box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.04), 0 10px 24px rgba(0, 0, 0, 0.16); }
}

@keyframes alertDotBlink {
  0%, 100% { transform: scale(1); opacity: 0.95; }
  50% { transform: scale(1.18); opacity: 1; }
}

@keyframes timelineFlow {
  0% { background-position: 0% 50%; filter: brightness(0.98); }
  50% { background-position: 100% 50%; filter: brightness(1.1); }
  100% { background-position: 0% 50%; filter: brightness(0.98); }
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
  background: linear-gradient(180deg, rgba(5, 12, 24, 0.98), rgba(8, 18, 31, 0.96)) !important;
  border-right: 1px solid rgba(109, 165, 255, 0.14);
}

[data-testid="stSidebar"] > div:first-child {
  background: transparent !important;
}

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {
  background:
    radial-gradient(circle at 14% 10%, rgba(155, 92, 255, 0.16), transparent 26%),
    radial-gradient(circle at 32% 12%, rgba(24, 110, 255, 0.12), transparent 24%),
    radial-gradient(circle at 80% 24%, rgba(25, 210, 201, 0.12), transparent 20%),
    linear-gradient(180deg, #030811 0%, #02060d 100%) !important;
  color: var(--text) !important;
}

.block-container {
  max-width: var(--nav-width) !important;
  padding-top: 1.1rem !important;
  padding-bottom: 4rem !important;
}

.saas-shell {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 0;
  pointer-events: none;
  z-index: -3;
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
  animation: floatDrift 18s ease-in-out infinite;
}

.orb-a {
  width: 16rem;
  height: 16rem;
  top: 7rem;
  left: 7%;
  background: rgba(155, 92, 255, 0.22);
}

.orb-b {
  width: 20rem;
  height: 20rem;
  top: 18rem;
  right: 7%;
  background: rgba(25, 210, 201, 0.14);
  animation-delay: -6s;
}

.orb-c {
  width: 18rem;
  height: 18rem;
  top: 26rem;
  left: 34%;
  background: rgba(100, 162, 255, 0.16);
  animation-delay: -11s;
}

.hero-shell,
.page-shell {
  width: min(100%, var(--content-width));
  margin-inline: auto;
}

.nav-shell {
  width: min(100%, var(--nav-width));
  margin-inline: auto;
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem 1rem;
  backdrop-filter: blur(18px);
  border: 1px solid transparent;
  background:
    linear-gradient(rgba(8, 16, 29, 0.88), rgba(8, 16, 29, 0.82)) padding-box,
    linear-gradient(135deg, rgba(155, 92, 255, 0.34), rgba(100, 162, 255, 0.22), rgba(24, 209, 199, 0.26)) border-box;
  border-radius: 24px;
  overflow: hidden;
}

.nav-brand-zone,
.top-nav-links,
.top-nav-meta,
.sidebar-row-link,
.sidebar-preview-wrap {
  display: flex;
}

.nav-brand-zone {
  align-items: center;
  gap: 0.55rem;
  flex: 0 0 auto;
  text-decoration: none;
}

.top-nav-links {
  align-items: center;
  gap: 0.18rem;
  flex: 1 1 auto;
  min-width: 0;
  justify-content: flex-start;
  overflow-x: visible;
  scrollbar-width: none;
}

.top-nav-links::-webkit-scrollbar {
  display: none;
}

.top-nav-meta {
  align-items: center;
  gap: 0.5rem;
  flex: 0 0 auto;
  margin-left: auto;
}

.top-nav-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: 38px;
  padding: 0 0.9rem;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: var(--muted);
  font-size: 0.82rem;
  font-weight: 700;
  white-space: nowrap;
}

.top-nav-pill-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: #19d97c;
  box-shadow: 0 0 0 6px rgba(25, 217, 124, 0.12);
  flex: 0 0 auto;
}

.nav-brand-box {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 62px;
  height: 58px;
  padding: 0;
  border-radius: 0.35rem;
  border: 1px solid rgba(142, 97, 255, 0.16);
  background:
    linear-gradient(180deg, rgba(10, 14, 28, 0.98), rgba(6, 9, 18, 0.98));
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.015) inset,
    0 0 34px rgba(122, 67, 255, 0.34),
    0 18px 42px rgba(0, 0, 0, 0.28);
  position: relative;
  overflow: visible;
}

.nav-brand-box::before {
  content: "";
  position: absolute;
  inset: -10px;
  border-radius: 0.7rem;
  background:
    radial-gradient(circle, rgba(122, 67, 255, 0.38) 0%, rgba(91, 157, 255, 0.2) 36%, rgba(122, 67, 255, 0) 76%);
  filter: blur(14px);
  z-index: -1;
}

.nav-brand-icon {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 0.28rem;
  filter: drop-shadow(0 10px 24px rgba(91, 157, 255, 0.2));
}

.nav-brand-word {
  font-family: "Sora", sans-serif;
  font-size: 1.18rem;
  font-weight: 700;
  letter-spacing: -0.045em;
  white-space: nowrap;
  color: #eef5ff;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.22);
  text-decoration: none;
}

.nav-brand-word .nav-brand-accent {
  color: var(--brand-blue-accent);
  text-shadow: 0 0 18px rgba(92, 169, 255, 0.22);
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  color: var(--text);
}

.brand.brand-lockup {
  gap: 0.9rem;
}

.brand-media {
  display: inline-flex;
  align-items: center;
}

.brand-lockup.nav .brand-media {
  width: clamp(118px, 16vw, 168px);
}

.brand-lockup.sidebar {
  width: 100%;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.7rem;
}

.brand-lockup.sidebar .brand-media {
  width: min(100%, 220px);
}

.brand-lockup.footer .brand-media {
  width: min(100%, 180px);
}

.brand-logo {
  display: block;
  width: 100%;
  height: auto;
  filter: drop-shadow(0 14px 30px rgba(76, 138, 244, 0.2));
}

.brand-copy {
  display: flex;
  flex-direction: column;
  gap: 0.12rem;
}

.brand-caption {
  color: var(--muted);
  font-size: 0.82rem;
  line-height: 1.5;
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
  background: linear-gradient(180deg, rgba(155, 92, 255, 0.98), rgba(73, 134, 255, 0.9), rgba(72, 223, 255, 0.78));
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

.ai-gradient {
  background: linear-gradient(90deg, var(--purple) 0%, var(--blue) 52%, var(--teal) 100%);
  background-size: 200% 200%;
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation: gradientShift 8s linear infinite;
}

.topbar-stack {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.topbar-label {
  color: var(--cyan);
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.topbar-page-title {
  font-family: "Sora", sans-serif;
  font-size: 1.15rem;
  letter-spacing: -0.03em;
}

.topbar-sub {
  color: var(--muted);
  font-size: 0.9rem;
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
  padding: 0.72rem 0.8rem;
  border-radius: 14px;
  transition: background 160ms ease, color 160ms ease, transform 160ms ease;
  white-space: nowrap;
  font-size: 0.94rem;
}

.nav-link:hover,
.nav-link.active {
  color: var(--text);
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-1px);
}

.nav-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
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
  position: relative;
  overflow: hidden;
}

.btn:hover {
  transform: translateY(-1px);
}

.btn::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(110deg, transparent 0%, rgba(255, 255, 255, 0.16) 46%, transparent 100%);
  transform: translateX(-140%);
  transition: transform 320ms ease;
}

.btn:hover::after {
  transform: translateX(140%);
}

.btn-primary {
  color: #fff;
  background: linear-gradient(90deg, var(--purple-strong) 0%, var(--blue-strong) 52%, var(--teal) 100%);
  box-shadow: 0 16px 40px rgba(122, 67, 255, 0.28);
}

.btn-outline-cta {
  border: 1.5px solid transparent;
  color: #f5fbff;
  background:
    linear-gradient(180deg, rgba(5, 12, 24, 0.98), rgba(8, 18, 31, 0.96)) padding-box,
    linear-gradient(90deg, var(--purple-strong) 0%, var(--blue-strong) 52%, var(--teal) 100%) border-box;
  box-shadow: none;
}

.btn-outline-cta:hover {
  box-shadow: 0 0 0 1px rgba(117, 231, 255, 0.22);
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
  align-items: stretch;
}

.glass {
  border: 1px solid transparent;
  border-radius: var(--radius-xl);
  background:
    linear-gradient(180deg, rgba(10, 20, 34, 0.92), rgba(5, 12, 24, 0.74)) padding-box,
    linear-gradient(135deg, rgba(155, 92, 255, 0.34), rgba(100, 162, 255, 0.22), rgba(24, 209, 199, 0.24)) border-box;
  box-shadow: var(--shadow);
  position: relative;
  overflow: hidden;
}

.glass::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.045), transparent 24%);
  pointer-events: none;
}

.hero-card {
  padding: 2.4rem;
  animation: pulseGlow 9s ease-in-out infinite;
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

.home-hero-stage {
  width: min(100%, 1120px);
  margin-inline: auto;
  padding: clamp(2.8rem, 5vw, 5rem) 0 2.4rem;
  display: grid;
  justify-items: center;
  text-align: center;
}

.home-logo-stack {
  display: grid;
  justify-items: center;
  gap: 1.2rem;
}

.home-hero-ticker {
  width: min(100%, 1220px);
  margin: 0 auto 2rem;
}

.home-logo-frame {
  position: relative;
  width: min(100%, 268px);
  padding: 1.1rem 1.35rem;
  border-radius: 24px;
  background: linear-gradient(180deg, rgba(4, 5, 10, 0.99), rgba(1, 3, 8, 0.99));
  border: 1px solid rgba(122, 67, 255, 0.18);
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.03) inset,
    0 0 44px rgba(122, 67, 255, 0.38),
    0 28px 64px rgba(0, 0, 0, 0.34);
}

.home-logo-frame::before {
  content: "";
  position: absolute;
  inset: -18px;
  border-radius: 30px;
  background: radial-gradient(circle, rgba(122, 67, 255, 0.42) 0%, rgba(91, 157, 255, 0.16) 36%, rgba(122, 67, 255, 0) 74%);
  filter: blur(18px);
  z-index: -1;
}

.home-logo-image {
  display: block;
  width: 100%;
  height: auto;
}

.home-powered-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  min-height: 44px;
  padding: 0 1rem;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.035);
  color: var(--muted);
  font-size: 0.96rem;
}

.home-powered-glyph {
  color: #cfdcff;
  font-size: 0.95rem;
}

.home-powered-dot,
.home-live-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: #19d97c;
  box-shadow: 0 0 0 6px rgba(25, 217, 124, 0.12);
}

.home-hero-title {
  margin: 1.9rem 0 0;
  font-family: "Sora", sans-serif;
  font-size: clamp(3.1rem, 7vw, 5.8rem);
  line-height: 0.98;
  letter-spacing: -0.075em;
}

.home-hero-title span {
  display: block;
}

.home-hero-emphasis {
  background: linear-gradient(90deg, #a7c0ff 0%, #72a0ff 24%, #4f88ff 56%, #2f76ff 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.home-hero-copy {
  max-width: 760px;
  margin: 1.45rem auto 0;
  color: var(--muted);
  font-size: clamp(1.12rem, 1.8vw, 1.55rem);
  line-height: 1.5;
}

.home-live-pill {
  margin-top: 1.7rem;
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  min-height: 42px;
  padding: 0 1rem;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.03);
  color: var(--muted);
  font-size: 0.95rem;
}

.home-hero-actions {
  margin-top: 2.2rem;
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.home-hero-actions .btn {
  min-width: 190px;
  min-height: 54px;
  padding: 0 1.5rem;
}

.home-hero-actions .btn-secondary {
  background: rgba(255, 255, 255, 0.015);
}

.home-preview-shell {
  width: min(100%, 1040px);
  margin-top: 2.3rem;
  padding: 1rem;
  border-radius: 24px;
  border: 1px solid rgba(88, 226, 255, 0.55);
  background: rgba(7, 13, 24, 0.62);
  box-shadow: 0 0 0 1px rgba(122, 67, 255, 0.16), 0 18px 42px rgba(0, 0, 0, 0.22);
  position: relative;
  overflow: hidden;
}

.home-preview-shell::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(112, 220, 255, 0.16) 48%, transparent 100%);
  transform: translateX(-120%);
  animation: previewShellSweep 6.2s ease-in-out infinite;
  pointer-events: none;
}

.home-proof-strip {
  width: min(100%, 1120px);
  margin-top: 2.15rem;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1.4rem;
}

.home-proof-item {
  text-align: center;
}

.home-proof-value {
  font-family: "Sora", sans-serif;
  font-size: clamp(2.4rem, 4vw, 3.25rem);
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.06em;
  color: #6e7cff;
}

.home-proof-label {
  margin-top: 0.65rem;
  color: #eef5ff;
  font-size: 1.08rem;
  font-weight: 700;
}

.home-proof-copy {
  margin-top: 0.35rem;
  color: var(--muted);
  font-size: 0.98rem;
  line-height: 1.45;
}

.home-intelligence-shell {
  width: min(100%, 1220px);
  margin-top: 3.25rem;
  display: grid;
  gap: 1.8rem;
  justify-items: center;
}

.home-intelligence-head {
  max-width: 760px;
  display: grid;
  gap: 1rem;
  justify-items: center;
  text-align: center;
}

.home-intelligence-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  min-height: 42px;
  padding: 0 1rem;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.035);
  color: #b9c6dd;
  font-size: 0.95rem;
}

.home-intelligence-pill-glyph {
  color: #dbe7ff;
  font-size: 0.92rem;
}

.home-intelligence-title {
  margin: 0;
  font-family: "Sora", sans-serif;
  font-size: clamp(2.3rem, 4.8vw, 3.55rem);
  line-height: 1.08;
  letter-spacing: -0.06em;
}

.home-intelligence-copy {
  margin: 0;
  color: var(--muted);
  font-size: clamp(1.02rem, 1.7vw, 1.22rem);
  line-height: 1.6;
}

.home-intelligence-grid {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.45rem;
}

.home-intelligence-card {
  min-height: 214px;
  padding: 1.55rem;
  border-radius: 22px;
  border: 1px solid rgba(82, 218, 255, 0.65);
  background: rgba(5, 9, 15, 0.68);
  box-shadow:
    0 0 0 1px rgba(122, 67, 255, 0.22),
    0 18px 36px rgba(0, 0, 0, 0.24);
  text-align: left;
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
}

.home-intelligence-card:hover {
  transform: translateY(-4px);
  box-shadow:
    0 0 0 1px rgba(122, 67, 255, 0.28),
    0 24px 46px rgba(0, 0, 0, 0.28);
}

.home-intelligence-icon-shell {
  width: 42px;
  height: 42px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  background: radial-gradient(circle at 30% 25%, rgba(108, 71, 255, 0.28), rgba(35, 56, 110, 0.2) 70%);
  box-shadow: 0 0 18px rgba(104, 88, 255, 0.18);
  color: #eef5ff;
  font-size: 1.12rem;
}

.home-intelligence-card h3 {
  margin: 1.15rem 0 0.8rem;
  font-family: "Sora", sans-serif;
  font-size: 1.05rem;
  line-height: 1.35;
}

.home-intelligence-card p {
  margin: 0;
  color: var(--muted);
  font-size: 0.98rem;
  line-height: 1.6;
}

.home-testimonial-shell {
  width: min(100%, 1220px);
  margin: 0 auto 2.4rem;
}

.home-testimonial-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.35rem;
}

.home-testimonial-card {
  min-height: 176px;
  padding: 1.55rem 1.6rem;
  border-radius: 22px;
  border: 1px solid rgba(82, 218, 255, 0.62);
  background: rgba(6, 10, 16, 0.72);
  box-shadow:
    0 0 0 1px rgba(122, 67, 255, 0.18),
    0 18px 36px rgba(0, 0, 0, 0.22);
  text-align: left;
}

.home-testimonial-quote {
  margin: 0;
  color: #b2bccd;
  font-size: 0.98rem;
  line-height: 1.65;
  font-style: italic;
}

.home-testimonial-author {
  margin-top: 1.15rem;
  display: grid;
  gap: 0.15rem;
}

.home-testimonial-author strong {
  font-family: "Sora", sans-serif;
  font-size: 1.02rem;
  color: #eef5ff;
}

.home-testimonial-author span {
  color: var(--muted);
  font-size: 0.98rem;
}

.home-cta-shell {
  width: min(100%, 980px);
  margin: 0 auto 2.8rem;
  display: grid;
  gap: 1.2rem;
  justify-items: center;
  text-align: center;
}

.home-cta-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 42px;
  padding: 0 1rem;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.035);
  color: #b9c6dd;
  font-size: 0.95rem;
}

.home-cta-pill-glyph {
  color: #dbe7ff;
  font-size: 0.92rem;
}

.home-cta-title {
  margin: 0;
  font-family: "Sora", sans-serif;
  font-size: clamp(2.1rem, 4.8vw, 3.55rem);
  line-height: 1.08;
  letter-spacing: -0.06em;
}

.home-cta-copy {
  margin: 0;
  color: var(--muted);
  font-size: clamp(1.02rem, 1.7vw, 1.22rem);
  line-height: 1.55;
}

.home-cta-shell .btn {
  min-width: 190px;
}

.home-preview-grid,
.home-alert-item,
.home-timeline-row,
.home-chart-bars {
  display: flex;
}

.home-preview-grid {
  gap: 1rem;
}

.home-preview-card {
  flex: 1 1 0;
  min-height: 210px;
  padding: 1rem 1rem 0.95rem;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(10, 16, 28, 0.7);
  text-align: left;
  position: relative;
  overflow: hidden;
  animation: previewCardFloat 6.4s ease-in-out infinite;
}

.home-preview-card:nth-child(2) {
  animation-delay: 0.75s;
}

.home-preview-card:nth-child(3) {
  animation-delay: 1.5s;
}

.home-preview-head {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  color: var(--muted);
  font-size: 0.97rem;
}

.home-preview-icon {
  color: #d8e6fb;
  font-size: 0.92rem;
}

.home-chart-wrap {
  margin-top: 1.1rem;
  padding: 0.9rem 0.9rem 0.8rem;
  border-radius: 16px;
  background: rgba(6, 11, 21, 0.72);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.home-chart-bars {
  align-items: flex-end;
  gap: 0.38rem;
  min-height: 112px;
}

.home-chart-bar {
  flex: 1 1 0;
  min-height: 12px;
  border-radius: 8px 8px 4px 4px;
  background: linear-gradient(180deg, #2fe8ff 0%, #376dff 100%);
  box-shadow: 0 0 14px rgba(56, 170, 255, 0.22);
  transform-origin: center bottom;
  animation: chartBarLift 2.8s ease-in-out infinite;
}

.home-chart-bar:nth-child(1) { animation-delay: 0.05s; }
.home-chart-bar:nth-child(2) { animation-delay: 0.12s; }
.home-chart-bar:nth-child(3) { animation-delay: 0.19s; }
.home-chart-bar:nth-child(4) { animation-delay: 0.26s; }
.home-chart-bar:nth-child(5) { animation-delay: 0.33s; }
.home-chart-bar:nth-child(6) { animation-delay: 0.40s; }
.home-chart-bar:nth-child(7) { animation-delay: 0.47s; }
.home-chart-bar:nth-child(8) { animation-delay: 0.54s; }
.home-chart-bar:nth-child(9) { animation-delay: 0.61s; }
.home-chart-bar:nth-child(10) { animation-delay: 0.68s; }
.home-chart-bar:nth-child(odd) {
  animation-duration: 3.15s;
}

.home-chart-axis {
  margin-top: 0.8rem;
  height: 1px;
  background: rgba(102, 208, 255, 0.45);
}

.home-chart-caption {
  margin-top: 0.7rem;
  color: var(--muted);
  font-size: 0.96rem;
}

.home-alert-stack {
  display: grid;
  gap: 0.7rem;
  margin-top: 1rem;
}

.home-alert-item {
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 0.85rem;
  border-radius: 14px;
  border: 1px solid transparent;
  position: relative;
  overflow: hidden;
  animation: alertPulse 4.8s ease-in-out infinite;
}

.home-alert-item::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(100deg, transparent 0%, rgba(255, 255, 255, 0.12) 48%, transparent 100%);
  transform: translateX(-130%);
  animation: alertSweep 5.4s ease-in-out infinite;
  pointer-events: none;
}

.home-alert-item.high {
  background: rgba(111, 24, 24, 0.42);
  border-color: rgba(239, 68, 68, 0.25);
}

.home-alert-item.medium {
  background: rgba(94, 58, 9, 0.38);
  border-color: rgba(245, 158, 11, 0.22);
}

.home-alert-item.low {
  background: rgba(8, 80, 50, 0.34);
  border-color: rgba(52, 211, 153, 0.22);
}

.home-alert-item.medium {
  animation-delay: 0.8s;
}

.home-alert-item.low {
  animation-delay: 1.6s;
}

.home-alert-dot {
  width: 9px;
  height: 9px;
  border-radius: 999px;
  flex: 0 0 auto;
  animation: alertDotBlink 2.4s ease-in-out infinite;
}

.home-alert-item.high .home-alert-dot {
  background: #ef4444;
}

.home-alert-item.medium .home-alert-dot {
  background: #f59e0b;
}

.home-alert-item.low .home-alert-dot {
  background: #34d399;
}

.home-alert-copy {
  color: #e8f1ff;
  font-size: 0.98rem;
  line-height: 1.32;
}

.home-timeline-stack {
  display: grid;
  gap: 0.9rem;
  margin-top: 1rem;
}

.home-timeline-row {
  flex-direction: column;
  gap: 0.38rem;
}

.home-timeline-top {
  display: flex;
  justify-content: space-between;
  gap: 0.8rem;
  color: #e8f1ff;
  font-size: 0.97rem;
}

.home-timeline-bar {
  height: 8px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.09);
  overflow: hidden;
}

.home-timeline-bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #3e7bff 0%, #2fe8ff 100%);
  background-size: 200% 100%;
  box-shadow: 0 0 16px rgba(47, 232, 255, 0.18);
  animation: timelineFlow 4.6s linear infinite;
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

.ticker-shell {
  margin-top: 1rem;
  padding: 0.95rem 0;
}

.ticker-mask {
  overflow: hidden;
  white-space: nowrap;
}

.ticker-track {
  display: inline-flex;
  min-width: max-content;
  gap: 1rem;
  animation: tickerSlide 20s linear infinite;
}

.ticker-item {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.55rem 0.95rem;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(255, 255, 255, 0.035);
  color: var(--muted);
  font-size: 0.92rem;
}

.ticker-item::before {
  content: "";
  width: 0.55rem;
  height: 0.55rem;
  border-radius: 999px;
  background: linear-gradient(180deg, var(--purple), var(--teal));
  box-shadow: 0 0 0 6px rgba(24, 209, 199, 0.08);
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

.hero-visual {
  padding: 2rem;
  display: grid;
  gap: 1.1rem;
}

.hero-visual::after {
  content: "";
  position: absolute;
  inset: -20% 0 auto;
  height: 32%;
  background: linear-gradient(180deg, rgba(118, 231, 255, 0.22), rgba(118, 231, 255, 0));
  mix-blend-mode: screen;
  animation: scanDrift 8.5s ease-in-out infinite;
  pointer-events: none;
}

.hero-visual-head,
.hero-health-grid,
.hero-driver-item,
.brand-marquee,
.compliance-band,
.feature-card-top,
.process-card-head {
  display: flex;
}

.hero-visual-head {
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.hero-health-grid {
  gap: 12px;
  flex-wrap: wrap;
}

.hero-health-card {
  flex: 1 1 145px;
  padding: 1rem;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(255, 255, 255, 0.03);
}

.hero-health-card span,
.metric-showcase-card span,
.process-copy,
.logo-chip,
.feature-caption {
  color: var(--muted);
}

.hero-health-card strong {
  display: block;
  margin-top: 0.45rem;
  font-family: "Sora", sans-serif;
  font-size: 1.55rem;
  letter-spacing: -0.04em;
}

.hero-progress {
  display: grid;
  gap: 0.8rem;
}

.hero-progress-row {
  display: grid;
  gap: 0.4rem;
}

.hero-progress-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  color: var(--muted);
  font-size: 0.92rem;
}

.hero-progress-bar {
  height: 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.06);
  overflow: hidden;
}

.hero-progress-bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, rgba(155, 92, 255, 0.92), rgba(100, 162, 255, 0.92), rgba(24, 209, 199, 0.92));
  box-shadow: 0 10px 28px rgba(76, 138, 244, 0.2);
}

.hero-driver-list {
  display: grid;
  gap: 0.75rem;
}

.hero-driver-item {
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding: 0.8rem 0.95rem;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(255, 255, 255, 0.025);
}

.hero-driver-copy strong,
.process-title,
.metric-showcase-card strong {
  display: block;
  font-family: "Sora", sans-serif;
}

.hero-driver-copy p {
  margin: 0.25rem 0 0;
  color: var(--muted);
  font-size: 0.9rem;
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
  border: 1px solid transparent;
  border-radius: 22px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.03), rgba(255, 255, 255, 0.025)) padding-box,
    linear-gradient(135deg, rgba(155, 92, 255, 0.22), rgba(100, 162, 255, 0.12), rgba(24, 209, 199, 0.16)) border-box;
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
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
}

.feature-card:hover,
.quote-card:hover,
.pricing-card:hover,
.detail-card:hover,
.history-card:hover,
.workspace-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 28px 60px rgba(0, 0, 0, 0.24);
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

.metric-showcase-grid,
.process-grid {
  display: grid;
  gap: 16px;
}

.metric-showcase-grid {
  margin-top: 1.2rem;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.metric-showcase-card {
  padding: 1.15rem 1.2rem;
  border-radius: 22px;
  border: 1px solid transparent;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.035), rgba(255, 255, 255, 0.025)) padding-box,
    linear-gradient(135deg, rgba(155, 92, 255, 0.24), rgba(100, 162, 255, 0.18), rgba(24, 209, 199, 0.2)) border-box;
}

.metric-showcase-card strong {
  margin-top: 0.5rem;
  font-size: clamp(1.7rem, 3vw, 2.3rem);
  letter-spacing: -0.06em;
}

.metric-showcase-card small {
  display: block;
  margin-top: 0.65rem;
  color: var(--cyan);
  font-size: 0.88rem;
}

.brand-marquee,
.compliance-band {
  flex-wrap: wrap;
  gap: 12px;
}

.logo-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 54px;
  padding: 0 1rem;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(255, 255, 255, 0.03);
  font-family: "Sora", sans-serif;
  font-size: 0.95rem;
}

.process-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.process-card {
  padding: 1.45rem;
  border-radius: 24px;
  border: 1px solid transparent;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.035), rgba(255, 255, 255, 0.025)) padding-box,
    linear-gradient(135deg, rgba(155, 92, 255, 0.26), rgba(100, 162, 255, 0.16), rgba(24, 209, 199, 0.18)) border-box;
}

.process-card-head {
  justify-content: space-between;
  align-items: center;
  gap: 0.8rem;
}

.step-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 3rem;
  height: 3rem;
  border-radius: 1rem;
  background: linear-gradient(135deg, rgba(155, 92, 255, 0.18), rgba(24, 209, 199, 0.16));
  border: 1px solid rgba(118, 231, 255, 0.18);
  color: var(--text);
  font-family: "Sora", sans-serif;
  font-weight: 700;
}

.process-title {
  font-size: 1.1rem;
}

.process-copy {
  margin-top: 0.85rem;
  line-height: 1.7;
}

.feature-card-top {
  align-items: center;
  gap: 0.8rem;
}

.feature-icon-shell {
  width: 2.8rem;
  height: 2.8rem;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(155, 92, 255, 0.24), rgba(24, 209, 199, 0.2));
  border: 1px solid rgba(118, 231, 255, 0.15);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 1.15rem;
}

.feature-caption {
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

.sidebar-brand-card {
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding: 0.55rem 0 1rem;
  margin-bottom: 0.35rem;
}

.sidebar-mini-label {
  color: var(--muted);
  font-size: 0.8rem;
  line-height: 1.5;
}

.shortcut-stack {
  display: grid;
  gap: 0.55rem;
  justify-items: center;
}

.shortcut-caption {
  color: var(--muted);
  font-size: 0.8rem;
  line-height: 1.5;
  text-align: center;
}

.command-bar-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 1rem;
  align-items: center;
}

.command-bar-copy {
  min-width: 0;
}

.command-bar-status {
  display: flex;
  justify-content: flex-end;
}

.sidebar-shortcut-wrap {
  display: grid;
  justify-items: center;
  gap: 0.55rem;
  margin-top: 0.15rem;
}

.sidebar-shortcut-pill {
  min-width: 112px;
  min-height: 44px;
  justify-content: center;
  color: var(--text);
  font-family: "Sora", sans-serif;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.sidebar-shortcut-caption {
  text-align: center;
}

.sidebar-shortcut-key {
  color: var(--text);
  opacity: 1;
}

.floating-shortcut-wrap {
  position: fixed;
  left: 1.1rem;
  bottom: 1.2rem;
  z-index: 26;
  display: grid;
  justify-items: center;
  gap: 0.55rem;
  padding: 0.7rem 0.8rem 0.35rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.floating-shortcut-wrap .sidebar-shortcut-pill {
  min-width: 124px;
}

.floating-shortcut-wrap .sidebar-shortcut-caption {
  max-width: 150px;
}

.hero-shortcut-wrap {
  margin: 0.9rem 0 0.2rem;
}

.sidebar-section-label {
  margin: 1rem 0 0.7rem;
  color: var(--cyan);
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.sidebar-divider {
  width: 100%;
  height: 1px;
  margin: 1rem 0;
  background: rgba(255, 255, 255, 0.08);
}

.sidebar-row-link {
  align-items: center;
  min-height: 42px;
  padding: 0 0.55rem;
  border-radius: 12px;
  color: var(--muted);
  text-decoration: none;
  font-weight: 600;
  transition: background 150ms ease, color 150ms ease;
}

.sidebar-row-link:hover {
  background: rgba(255, 255, 255, 0.04);
  color: var(--text);
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
  width: min(100%, var(--nav-width));
  margin-inline: auto;
  margin-top: 4rem;
}

.footer-panel {
  position: relative;
  overflow: hidden;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  background:
    radial-gradient(circle at 12% 34%, rgba(24, 209, 199, 0.08), transparent 18%),
    radial-gradient(circle at 36% 78%, rgba(76, 138, 244, 0.12), transparent 16%),
    radial-gradient(circle at 58% 46%, rgba(122, 67, 255, 0.09), transparent 18%),
    radial-gradient(circle at 86% 22%, rgba(24, 209, 199, 0.08), transparent 14%),
    linear-gradient(180deg, rgba(3, 7, 14, 0.985), rgba(2, 6, 13, 0.995));
}

.footer-panel::before,
.footer-panel::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.footer-panel::before {
  background:
    linear-gradient(112deg, transparent 0 46%, rgba(100, 162, 255, 0.1) 46.3%, transparent 46.8%) 12% 18% / 340px 220px no-repeat,
    linear-gradient(80deg, transparent 0 48%, rgba(24, 209, 199, 0.1) 48.4%, transparent 48.9%) 72% 14% / 420px 260px no-repeat,
    linear-gradient(100deg, transparent 0 49%, rgba(122, 67, 255, 0.1) 49.4%, transparent 49.9%) 46% 60% / 360px 240px no-repeat;
  opacity: 0.28;
}

.footer-panel::after {
  background:
    radial-gradient(circle, rgba(76, 138, 244, 0.65) 0 1.5px, transparent 2px) 9% 34% / 240px 180px,
    radial-gradient(circle, rgba(24, 209, 199, 0.55) 0 1.5px, transparent 2px) 58% 62% / 300px 220px,
    radial-gradient(circle, rgba(76, 138, 244, 0.5) 0 1.5px, transparent 2px) 88% 20% / 260px 180px;
  opacity: 0.52;
}

.footer-content {
  position: relative;
  z-index: 1;
  width: min(calc(100% - 48px), var(--nav-width));
  margin-inline: auto;
  padding: 4rem 0 1.2rem;
}

.footer-top-grid,
.footer-mid-row,
.footer-bottom-row,
.footer-link-grid,
.footer-social-row,
.footer-subscribe-row,
.footer-compliance-row {
  display: flex;
}

.footer-top-grid,
.footer-mid-row {
  display: grid;
  gap: 2.75rem;
}

.footer-top-grid {
  grid-template-columns: minmax(280px, 1.05fr) minmax(0, 1.55fr);
}

.footer-brand-column {
  max-width: 31rem;
}

.footer-brand-row {
  display: inline-flex;
  align-items: center;
  gap: 0.95rem;
  text-decoration: none !important;
  border-bottom: none !important;
  box-shadow: none !important;
}

.footer-brand-row:hover,
.footer-brand-row:focus,
.footer-brand-row:visited {
  text-decoration: none !important;
  border-bottom: none !important;
  box-shadow: none !important;
}

.footer-brand-box {
  width: 64px;
  height: 64px;
  padding: 0.72rem;
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(6, 10, 20, 0.98), rgba(4, 8, 16, 0.96));
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 0 1px rgba(122, 67, 255, 0.18), 0 18px 42px rgba(76, 138, 244, 0.18);
  display: grid;
  place-items: center;
}

.footer-brand-icon {
  display: block;
  width: 100%;
  height: auto;
}

.footer-brand-wordmark {
  font-family: "Sora", sans-serif;
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: -0.045em;
  color: #eef5ff;
  text-decoration: none !important;
  border-bottom: none !important;
}

.footer-brand-accent {
  color: var(--brand-blue-accent);
  text-decoration: none !important;
  border-bottom: none !important;
}

.footer-brand-copy {
  margin: 1.45rem 0 0;
  color: var(--muted);
  font-size: 1.08rem;
  line-height: 1.72;
}

.footer-contact-stack {
  display: grid;
  gap: 0.9rem;
  margin-top: 1.5rem;
}

.footer-contact-row {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  color: var(--muted);
  text-decoration: none;
  font-size: 1.02rem;
}

.footer-contact-icon {
  width: 22px;
  height: 22px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  color: var(--blue-strong);
  background: rgba(76, 138, 244, 0.08);
  border: 1px solid rgba(76, 138, 244, 0.18);
  font-size: 0.8rem;
  font-weight: 700;
}

.footer-social-row {
  gap: 0.85rem;
  align-items: center;
  margin-top: 1.9rem;
}

.footer-social-pill {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #d8e6fb;
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.footer-social-icon {
  width: 18px;
  height: 18px;
  display: block;
}

.footer-social-icon svg {
  width: 100%;
  height: 100%;
  display: block;
}

.footer-link-grid {
  justify-content: space-between;
  gap: 1.8rem;
  flex-wrap: nowrap;
}

.footer-link-column {
  min-width: 132px;
  display: grid;
  gap: 0.92rem;
  align-content: start;
}

.footer-link-column h4 {
  margin: 0;
  font-family: "Sora", sans-serif;
  font-size: 1rem;
}

.footer-link-column a,
.footer-static-link {
  color: var(--muted);
  text-decoration: none;
  font-size: 1.01rem;
  line-height: 1.45;
}

.footer-link-column a:hover {
  color: var(--text);
}

.footer-link-note {
  color: rgba(158, 176, 203, 0.65);
  font-size: 0.82rem;
  font-style: italic;
}

.footer-mid-row {
  grid-template-columns: minmax(320px, 1fr) minmax(0, 1.2fr);
  align-items: center;
  margin-top: 3.25rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.07);
}

.footer-newsletter h4 {
  margin: 0;
  font-family: "Sora", sans-serif;
  font-size: 1.5rem;
}

.footer-newsletter p {
  margin: 0.7rem 0 0;
  color: var(--muted);
  font-size: 1rem;
}

.footer-subscribe-row {
  gap: 0.9rem;
  align-items: center;
  flex-wrap: wrap;
  margin-top: 1.35rem;
}

.footer-input-shell {
  min-height: 52px;
  min-width: 240px;
  flex: 1 1 260px;
  display: flex;
  align-items: center;
  padding: 0 1rem;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.03);
  color: rgba(158, 176, 203, 0.78);
}

.footer-subscribe-btn {
  min-width: 168px;
}

.footer-compliance-row {
  justify-content: flex-end;
  gap: 1rem;
  flex-wrap: wrap;
}

.footer-compliance-item {
  min-width: 62px;
  display: grid;
  justify-items: center;
  gap: 0.42rem;
  text-align: center;
}

.footer-compliance-mark {
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  color: #eef5ff;
}

.footer-compliance-mark svg {
  width: 100%;
  height: 100%;
  display: block;
}

.footer-compliance-mark .compliance-stroke {
  fill: rgba(255, 255, 255, 0.02);
  stroke: rgba(255, 255, 255, 0.9);
  stroke-width: 1.5;
}

.footer-compliance-mark .compliance-glyph {
  fill: #eef5ff;
  font-family: "Sora", sans-serif;
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.footer-compliance-mark .compliance-detail {
  fill: rgba(238, 245, 255, 0.9);
  stroke: rgba(255, 255, 255, 0.9);
  stroke-width: 1.25;
}

.footer-compliance-code {
  color: #eef5ff;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.01em;
}

.footer-compliance-region {
  color: rgba(158, 176, 203, 0.78);
  font-size: 0.72rem;
  line-height: 1.35;
}

.footer-bottom-row {
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.07);
  color: var(--muted);
}

.footer-language-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  min-height: 42px;
  padding: 0 0.95rem;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.02);
  color: #dbe7fa;
}

.footer-language-flag {
  min-width: 24px;
  height: 24px;
  padding: 0 0.35rem;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(76, 138, 244, 0.16);
  color: #eef5ff;
  font-size: 0.72rem;
  font-weight: 700;
}

.footer-language-caret {
  color: rgba(219, 231, 250, 0.72);
  font-size: 0.9rem;
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
  background: linear-gradient(90deg, var(--purple-strong) 0%, var(--blue-strong) 52%, var(--teal) 100%);
  box-shadow: 0 14px 38px rgba(122, 67, 255, 0.24);
  font-weight: 700;
}

[data-testid="stSidebar"] div.stButton > button {
  width: 100%;
  justify-content: center;
  min-height: 52px;
  padding: 0 1rem;
  border: 1.5px solid transparent !important;
  border-radius: 16px;
  color: #f5fbff !important;
  background-color: transparent !important;
  background:
    linear-gradient(180deg, rgba(5, 12, 24, 0.98), rgba(8, 18, 31, 0.96)) padding-box,
    linear-gradient(90deg, var(--purple-strong) 0%, var(--blue-strong) 52%, var(--teal) 100%) border-box !important;
  box-shadow: none !important;
  font-weight: 700;
  transition: transform 160ms ease, box-shadow 160ms ease, filter 160ms ease;
}

[data-testid="stSidebar"] div.stButton > button:hover {
  transform: translateY(-1px);
  filter: brightness(1.03);
  box-shadow: 0 0 0 1px rgba(117, 231, 255, 0.16) !important;
}

[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
  color: #ffffff;
  border-color: transparent !important;
  background-color: transparent !important;
  background:
    linear-gradient(180deg, rgba(5, 12, 24, 0.98), rgba(8, 18, 31, 0.96)) padding-box,
    linear-gradient(90deg, var(--purple-strong) 0%, var(--blue-strong) 52%, var(--teal) 100%) border-box !important;
  box-shadow: 0 0 0 1px rgba(117, 231, 255, 0.28) !important;
}

div.stButton > button[kind="secondary"] {
  background: rgba(255, 255, 255, 0.04);
  box-shadow: none;
}

[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
  color: #f5fbff !important;
  background-color: transparent !important;
  background:
    linear-gradient(180deg, rgba(5, 12, 24, 0.98), rgba(8, 18, 31, 0.96)) padding-box,
    linear-gradient(90deg, var(--purple-strong) 0%, var(--blue-strong) 52%, var(--teal) 100%) border-box !important;
  box-shadow: none !important;
}

div[data-testid="stMarkdownContainer"] p code {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text);
}

div[data-testid="stPlotlyChart"] {
  border: 1px solid transparent;
  border-radius: 24px;
  background:
    linear-gradient(180deg, rgba(10, 20, 34, 0.96), rgba(6, 12, 24, 0.88)) padding-box,
    linear-gradient(135deg, rgba(155, 92, 255, 0.32), rgba(100, 162, 255, 0.18), rgba(24, 209, 199, 0.18)) border-box;
  padding: 0.6rem;
  box-shadow: 0 26px 54px rgba(0, 0, 0, 0.22);
}

div[data-testid="stPlotlyChart"] > div {
  border-radius: 18px;
  overflow: hidden;
}

div[data-testid="stDataFrame"] {
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 24px;
  overflow: hidden;
}

div[data-testid="stAlert"] {
  border-radius: 18px;
}

div[data-testid="stExpander"] {
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.03);
}

@media (max-width: 1100px) {
  .nav-shell,
  .hero-grid,
  .page-grid,
  .dashboard-hero-grid,
  .timeline-grid,
  .workspace-grid,
  .footer-top-grid,
  .footer-mid-row {
    grid-template-columns: 1fr;
  }

  .metric-showcase-grid,
  .process-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .nav-shell {
    position: relative;
    flex-direction: column;
    align-items: flex-start;
  }

  .top-nav-links,
  .nav-actions,
  .top-nav-meta {
    width: 100%;
  }

  .home-preview-grid {
    flex-direction: column;
  }

  .home-proof-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .home-intelligence-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .home-testimonial-grid {
    grid-template-columns: 1fr;
  }

  .footer-link-grid {
    flex-wrap: wrap;
  }

  .footer-compliance-row {
    justify-content: flex-start;
  }
}

@media (max-width: 900px) {
  .kpi-grid,
  .detail-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .metric-showcase-grid,
  .process-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .command-bar-grid {
    grid-template-columns: 1fr;
    justify-items: center;
  }

  .command-bar-copy,
  .command-bar-status {
    text-align: center;
    justify-content: center;
  }

  .footer-content {
    width: min(calc(100% - 32px), var(--nav-width));
    padding-top: 3.3rem;
  }

  .footer-link-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .block-container {
    padding-left: 0.9rem !important;
    padding-right: 0.9rem !important;
  }

  .top-nav-meta,
  .nav-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .kpi-grid,
  .detail-grid,
  .metric-showcase-grid,
  .process-grid {
    grid-template-columns: 1fr;
  }

  .hero-card,
  .insight-card,
  .hero-visual,
  .page-hero-card,
  .dashboard-banner {
    padding: 1.45rem;
  }

  .footer-link-grid {
    grid-template-columns: 1fr;
  }

  .home-proof-strip {
    grid-template-columns: 1fr;
  }

  .home-intelligence-grid {
    grid-template-columns: 1fr;
  }

  .footer-subscribe-row {
    flex-direction: column;
    align-items: stretch;
  }

  .footer-input-shell,
  .footer-subscribe-btn {
    width: 100%;
  }

  .footer-bottom-row {
    align-items: flex-start;
  }

  .floating-shortcut-wrap {
    left: 0.7rem;
    bottom: 0.8rem;
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


def _is_dashboard_page(page: str) -> bool:
    return page in DASHBOARD_PAGE_KEYS


def _top_nav_active_key(page: str) -> str:
    return "dashboard" if _is_dashboard_page(page) else page


@st.cache_data
def _logo_data_uri() -> str:
    for path, mime_type in (
        (LOGO_PNG_PATH, "image/png"),
        (LEGACY_LOGO_PNG_PATH, "image/png"),
        (LOGO_SVG_PATH, "image/svg+xml"),
    ):
        if path.exists():
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            return f"data:{mime_type};base64,{encoded}"
    return ""


@st.cache_data
def _nav_logo_data_uri() -> str:
    for path in (NAV_LOGO_PNG_PATH, LOGO_PNG_PATH, LEGACY_LOGO_PNG_PATH):
        if path.exists():
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            return f"data:image/png;base64,{encoded}"
    return ""


def _brand_lockup(location: str, caption: str | None = None) -> str:
    logo_uri = _logo_data_uri()
    if logo_uri:
        media = (
            '<span class="brand-media">'
            f'<img src="{logo_uri}" class="brand-logo" alt="certAIn logo" />'
            "</span>"
        )
    else:
        media = (
            '<span class="brand-media">'
            '<span class="brand-mark" aria-hidden="true">'
            '<span class="brand-triangle"></span>'
            '<span class="brand-core">A</span>'
            "</span>"
            '<span class="brand-word">cert<span class="ai-gradient">AI</span>n</span>'
            "</span>"
        )

    caption_html = ""
    if caption:
        caption_html = f'<span class="brand-copy"><span class="brand-caption">{caption}</span></span>'

    return f'<a class="brand brand-lockup {location}" href="{_href("home")}">{media}{caption_html}</a>'


def _nav_brand_markup() -> str:
    logo_uri = _nav_logo_data_uri()
    if logo_uri:
        media = (
            '<span class="nav-brand-box">'
            f'<img src="{logo_uri}" class="nav-brand-icon" alt="certAIn logo" />'
            "</span>"
        )
    else:
        media = (
            '<span class="nav-brand-box">'
            '<span class="brand-mark" aria-hidden="true">'
            '<span class="brand-triangle"></span>'
            '<span class="brand-core">A</span>'
            "</span>"
            "</span>"
        )

    return (
        f'<a class="nav-brand-zone" href="{_href("home")}">'
        f"{media}"
        '<span class="nav-brand-word">cert<span class="nav-brand-accent">AI</span>n</span>'
        "</a>"
    )


def _footer_brand_markup() -> str:
    logo_uri = _nav_logo_data_uri()
    if logo_uri:
        media = (
            '<span class="footer-brand-box">'
            f'<img src="{logo_uri}" class="footer-brand-icon" alt="certAIn logo" />'
            "</span>"
        )
    else:
        media = (
            '<span class="footer-brand-box">'
            '<span class="brand-mark" aria-hidden="true">'
            '<span class="brand-triangle"></span>'
            '<span class="brand-core">A</span>'
            "</span>"
            "</span>"
        )

    return (
        f'<a class="footer-brand-row" href="{_href("home")}">'
        f"{media}"
        '<span class="footer-brand-wordmark">cert<span class="footer-brand-accent">AI</span>n</span>'
        "</a>"
    )


def _footer_social_icon_markup(platform: str, label: str) -> str:
    icons = {
        "linkedin": (
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/>'
            '<rect x="2" y="9" width="4" height="12"/>'
            '<circle cx="4" cy="4" r="2"/>'
            "</svg>"
        ),
        "x": (
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            '<path d="M4 4L20 20"/>'
            '<path d="M20 4L4 20"/>'
            "</svg>"
        ),
        "github": (
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            '<path d="M15 22v-4a4.8 4.8 0 0 0-1-3.75c3.14-.35 6.44-1.54 6.44-7a5.44 5.44 0 0 0-1.42-3.78A5.07 5.07 0 0 0 18.91 1S17.73.65 15 2.48a13.38 13.38 0 0 0-6 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.42 3.78c0 5.42 3.3 6.61 6.44 7A4.8 4.8 0 0 0 9 18v4"/>'
            '<path d="M9 18c-4.51 2-5-2-7-2"/>'
            "</svg>"
        ),
        "youtube": (
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            '<path d="M2.5 17a24.12 24.12 0 0 1 0-10 2 2 0 0 1 1.4-1.4 49.56 49.56 0 0 1 16.2 0 2 2 0 0 1 1.4 1.4 24.12 24.12 0 0 1 0 10 2 2 0 0 1-1.4 1.4 49.56 49.56 0 0 1-16.2 0 2 2 0 0 1-1.4-1.4"/>'
            '<path d="M10 15l5-3-5-3z"/>'
            "</svg>"
        ),
    }
    icon = icons.get(platform, "")
    return (
        f'<span class="footer-social-pill" aria-label="{label}" title="{label}">'
        f'<span class="footer-social-icon">{icon}</span>'
        "</span>"
    )


def _footer_compliance_logo_markup(mark: str) -> str:
    logos = {
        "ISO": (
            '<svg viewBox="0 0 48 48" aria-hidden="true">'
            '<circle class="compliance-stroke" cx="24" cy="24" r="12"/>'
            '<text class="compliance-glyph" x="24" y="27" text-anchor="middle">ISO</text>'
            "</svg>"
        ),
        "S2": (
            '<svg viewBox="0 0 48 48" aria-hidden="true">'
            '<path class="compliance-stroke" d="M24 7l11 4v9c0 8.2-5.4 14.7-11 17.8C18.4 34.7 13 28.2 13 20v-9l11-4z"/>'
            '<text class="compliance-glyph" x="24" y="27" text-anchor="middle">S2</text>'
            "</svg>"
        ),
        "CA": (
            '<svg viewBox="0 0 48 48" aria-hidden="true">'
            '<path class="compliance-stroke" d="M9 19h30l-4 8H13l-4-8z"/>'
            '<path class="compliance-detail" d="M13 30h22"/>'
            '<text class="compliance-glyph" x="24" y="18" text-anchor="middle">CA</text>'
            "</svg>"
        ),
        "EU": (
            '<svg viewBox="0 0 48 48" aria-hidden="true">'
            '<circle class="compliance-stroke" cx="24" cy="24" r="10"/>'
            '<circle class="compliance-detail" cx="24" cy="13" r="1.2"/>'
            '<circle class="compliance-detail" cx="32.5" cy="16.5" r="1.2"/>'
            '<circle class="compliance-detail" cx="35" cy="24" r="1.2"/>'
            '<circle class="compliance-detail" cx="32.5" cy="31.5" r="1.2"/>'
            '<circle class="compliance-detail" cx="24" cy="35" r="1.2"/>'
            '<circle class="compliance-detail" cx="15.5" cy="31.5" r="1.2"/>'
            '<circle class="compliance-detail" cx="13" cy="24" r="1.2"/>'
            '<circle class="compliance-detail" cx="15.5" cy="16.5" r="1.2"/>'
            '<text class="compliance-glyph" x="24" y="27" text-anchor="middle">EU</text>'
            "</svg>"
        ),
        "PI": (
            '<svg viewBox="0 0 48 48" aria-hidden="true">'
            '<path class="compliance-stroke" d="M24 8l11 6v10l-11 16-11-16V14l11-6z"/>'
            '<text class="compliance-glyph" x="24" y="27" text-anchor="middle">PI</text>'
            "</svg>"
        ),
        "LG": (
            '<svg viewBox="0 0 48 48" aria-hidden="true">'
            '<path class="compliance-stroke" d="M24 8l12 5v9c0 8.5-5.6 14.7-12 17.7C17.6 36.7 12 30.5 12 22v-9l12-5z"/>'
            '<path class="compliance-detail" d="M18 28h12"/>'
            '<text class="compliance-glyph" x="24" y="23" text-anchor="middle">LG</text>'
            "</svg>"
        ),
        "AP": (
            '<svg viewBox="0 0 48 48" aria-hidden="true">'
            '<path class="compliance-stroke" d="M24 8l13 5v11c0 8.3-5.7 14.2-13 16.8C16.7 38.2 11 32.3 11 24V13l13-5z"/>'
            '<path class="compliance-detail" d="M17 31h14"/>'
            '<text class="compliance-glyph" x="24" y="23" text-anchor="middle">AP</text>'
            "</svg>"
        ),
    }
    return logos.get(mark, mark)


def _inject_styles() -> None:
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <div class="saas-shell">
          <div class="starfield" aria-hidden="true"></div>
          <div class="ambient-orb orb-a"></div>
          <div class="ambient-orb orb-b"></div>
          <div class="ambient-orb orb-c"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _inject_layout_state(active_page: str) -> None:
    if not _is_dashboard_page(active_page):
        st.markdown(
            """
            <style>
            [data-testid="stSidebar"] {
              display: none !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )


def _render_nav(active_page: str) -> None:
    active_key = _top_nav_active_key(active_page)
    nav_links = "".join(
        f'<a class="nav-link {"active" if page == active_key else ""}" href="{_href(page)}">{label}</a>'
        for page, label in NAV_ITEMS
    )
    st.markdown(
        dedent(
            f"""
            <div class="nav-shell">
              {_nav_brand_markup()}
              <div class="top-nav-pill">
                <span class="top-nav-pill-dot"></span>
                <span>AI-Powered</span>
              </div>
              <div class="top-nav-links">
                {nav_links}
              </div>
              <div class="top-nav-meta">
                <a href="{_href("dashboard")}" class="btn btn-primary btn-outline-cta">Start Free Trial</a>
              </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def _render_sidebar(active_page: str) -> None:
    with st.sidebar:
        st.markdown(
            f"""
            <div class="sidebar-brand-card">
              {_brand_lockup("sidebar", "AI-Powered Project Management")}
              <div style="margin-top:0.85rem;" class="status-chip chip-low">AI Engine: Active</div>
              <div class="sidebar-mini-label" style="margin-top:0.7rem;">Forecasts, risk intelligence, and executive reporting in one workspace.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="sidebar-divider"></div>
            <div class="sidebar-section-label">Dashboard</div>
            """,
            unsafe_allow_html=True,
        )

        for page, label in DASHBOARD_ITEMS:
            button_type = "primary" if page == active_page else "secondary"
            if st.button(label, key=f"dashboard_{page}", use_container_width=True, type=button_type):
                _set_query_page(page)
                st.rerun()

        st.markdown(
            """
            <div class="sidebar-divider"></div>
            <div class="sidebar-shortcut-wrap">
              <div class="mini-pill sidebar-shortcut-pill"><span class="sidebar-shortcut-key">⌘K / Ctrl+K</span></div>
              <div class="sidebar-mini-label sidebar-shortcut-caption">Quick command search</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_command_bar() -> None:
    st.markdown(
        """
        <div class="glass" style="padding:1rem 1.2rem;margin-top:1rem;">
          <div class="command-bar-grid">
            <div class="command-bar-copy">
              <div class="kicker">AI command center</div>
              <div style="margin-top:0.55rem;color:var(--muted);">Project Spotlight available from anywhere in the workspace.</div>
            </div>
            <div class="command-bar-status">
              <div class="status-chip chip-low">AI Engine: Active</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_floating_shortcut(active_page: str) -> None:
    if _is_dashboard_page(active_page):
        return

    st.markdown(
        """
        <div class="floating-shortcut-wrap">
          <div class="mini-pill sidebar-shortcut-pill"><span class="sidebar-shortcut-key">⌘K / Ctrl+K</span></div>
          <div class="sidebar-mini-label sidebar-shortcut-caption">Quick command search</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_footer() -> None:
    link_columns_markup = []
    for title, items in FOOTER_LINK_COLUMNS:
        item_markup = []
        for label, page, note in items:
            note_markup = f' <span class="footer-link-note">({note})</span>' if note else ""
            if page:
                item_markup.append(f'<a href="{_href(page)}">{label}{note_markup}</a>')
            else:
                item_markup.append(f'<span class="footer-static-link">{label}{note_markup}</span>')
        link_columns_markup.append(
            "<div class=\"footer-link-column\">"
            f"<h4>{title}</h4>"
            + "".join(item_markup)
            + "</div>"
        )

    social_markup = "".join(
        _footer_social_icon_markup(platform, label)
        for platform, label in FOOTER_SOCIALS
    )
    compliance_markup = "".join(
        (
            '<div class="footer-compliance-item">'
            f'<div class="footer-compliance-mark">{_footer_compliance_logo_markup(mark)}</div>'
            f'<div class="footer-compliance-code">{code}</div>'
            f'<div class="footer-compliance-region">{region}</div>'
            "</div>"
        )
        for mark, code, region in FOOTER_COMPLIANCE
    )
    footer_html = dedent(
        f"""
        <div class="footer-shell">
          <div class="footer-panel">
            <div class="footer-content">
              <div class="footer-top-grid">
                <div class="footer-brand-column">
                  {_footer_brand_markup()}
                  <p class="footer-brand-copy">
                    AI-powered project forecasting using Monte Carlo simulation and dependency analysis.
                    Predict delays before they happen.
                  </p>
                  <div class="footer-contact-stack">
                    <a class="footer-contact-row" href="mailto:info@certain-pm.com">
                      <span class="footer-contact-icon">✉</span>
                      <span>info@certain-pm.com</span>
                    </a>
                    <div class="footer-contact-row">
                      <span class="footer-contact-icon">⌖</span>
                      <span>San Francisco, CA</span>
                    </div>
                  </div>
                  <div class="footer-social-row">{social_markup}</div>
                </div>
                <div class="footer-link-grid">{"".join(link_columns_markup)}</div>
              </div>
              <div class="footer-mid-row">
                <div class="footer-newsletter">
                  <h4>Stay up to date</h4>
                  <p>Get the latest on AI-powered project management.</p>
                  <div class="footer-subscribe-row">
                    <div class="footer-input-shell">Enter your email</div>
                    <a href="{_href("contact")}" class="btn btn-primary btn-outline-cta footer-subscribe-btn">Subscribe</a>
                  </div>
                </div>
                <div class="footer-compliance-row">{compliance_markup}</div>
              </div>
              <div class="footer-bottom-row">
                <span>&copy; 2026 certAIn. All rights reserved.</span>
                <div class="footer-language-pill">
                  <span class="footer-language-flag">US</span>
                  <span>English</span>
                  <span class="footer-language-caret">v</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        """
    ).strip()

    st.markdown(footer_html, unsafe_allow_html=True)


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
        template="plotly",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(5,12,24,0.58)",
        font=dict(color="#f4f8ff", family="Manrope, sans-serif", size=13),
        title=dict(x=0.02, xanchor="left", font=dict(color="#f4f8ff", family="Sora, sans-serif", size=22)),
        margin=dict(l=30, r=24, t=76, b=34),
        colorway=["#9b5cff", "#64a2ff", "#18d1c7", "#f5c56b", "#ff7f8c"],
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#9eb0cb"),
        ),
        hoverlabel=dict(
            bgcolor="rgba(5,12,24,0.96)",
            bordercolor="rgba(100,162,255,0.32)",
            font=dict(color="#f4f8ff", family="Manrope, sans-serif"),
        ),
        coloraxis_colorbar=dict(
            outlinewidth=0,
            tickfont=dict(color="#9eb0cb"),
            title=dict(font=dict(color="#f4f8ff")),
        ),
    )
    figure.update_xaxes(
        gridcolor="rgba(155,92,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.08)",
        linecolor="rgba(255,255,255,0.12)",
        showline=True,
        ticks="outside",
        tickfont=dict(color="#b9c9df"),
        title_font=dict(color="#dce9ff"),
    )
    figure.update_yaxes(
        gridcolor="rgba(100,162,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.08)",
        linecolor="rgba(255,255,255,0.12)",
        showline=True,
        ticks="outside",
        tickfont=dict(color="#b9c9df"),
        title_font=dict(color="#dce9ff"),
    )
    for trace in figure.data:
        trace_type = getattr(trace, "type", "")
        if trace_type in {"scatter", "scattergl"}:
            line_width = getattr(getattr(trace, "line", None), "width", None) or 0
            marker_size = getattr(getattr(trace, "marker", None), "size", None) or 7
            trace.update(
                line=dict(width=max(float(line_width), 3.0)),
                marker=dict(size=marker_size, line=dict(width=0)),
            )
        elif trace_type in {"bar", "histogram"}:
            marker = getattr(trace, "marker", None)
            marker_line = getattr(marker, "line", None)
            existing_line_color = getattr(marker_line, "color", None)
            existing_line_width = getattr(marker_line, "width", None)
            trace.update(
                opacity=0.92,
                marker_line_color=existing_line_color if existing_line_color is not None else "rgba(255,255,255,0.14)",
                marker_line_width=existing_line_width if existing_line_width is not None else 1.2,
            )
        elif trace_type == "indicator":
            trace.update(
                number_font=dict(color="#f4f8ff", family="Sora, sans-serif"),
                title_font=dict(color="#9eb0cb"),
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
        "saas_ai_sensitivity": 0.65,
        "saas_confidence_threshold": 0.7,
        "saas_email_alerts": True,
        "saas_in_app_alerts": True,
        "saas_ai_alerts": True,
        "saas_language": "English",
        "saas_region": "Global",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


@st.cache_resource
def _load_risk_model_bundle() -> tuple[Any | None, RiskModelStatus]:
    model_path = settings.risk_model_path_file
    if not model_path.is_absolute():
        model_path = ROOT / model_path

    return load_risk_model(
        enabled=settings.risk_model_enabled,
        model_path=model_path,
        model_version=settings.risk_model_version,
    )


@st.cache_resource
def _initialize_database() -> bool:
    init_db()
    return True


@st.cache_data
def _load_model_metrics() -> dict[str, Any]:
    metrics_path = settings.risk_model_metrics_file
    if not metrics_path.is_absolute():
        metrics_path = ROOT / metrics_path
    if not metrics_path.exists():
        return {}
    return json.loads(metrics_path.read_text(encoding="utf-8"))


@st.cache_data
def _load_portfolio_history() -> pd.DataFrame:
    return pd.read_csv(ROOT / "data" / "project_portfolio_history.csv")


@st.cache_data
def _load_monitoring_snapshot() -> pd.DataFrame:
    return pd.read_csv(ROOT / "data" / "risk_monitoring_snapshot.csv")


def _portfolio_summary(portfolio_df: pd.DataFrame) -> dict[str, float]:
    delayed = (portfolio_df["Delay_Flag"] == "Delayed").mean()
    return {
        "projects": float(len(portfolio_df)),
        "delayed_pct": float(delayed * 100.0),
        "avg_budget_overrun": float(portfolio_df["Budget_Overrun_Pct"].mean()),
        "avg_forecast_error": float(portfolio_df["Forecast_Error_Days"].mean()),
        "avg_complexity": float(portfolio_df["Complexity_Score"].mean()),
    }


def _monitoring_summary(monitoring_df: pd.DataFrame) -> dict[str, float]:
    accuracy = (monitoring_df["Predicted_Risk_Level"] == monitoring_df["Actual_Risk_Level"]).mean()
    return {
        "accuracy_pct": float(accuracy * 100.0),
        "avg_confidence": float(monitoring_df["Prediction_Confidence"].mean() * 100.0),
        "avg_drift": float(monitoring_df["Drift_Score"].mean()),
        "alerts_open": float(monitoring_df["Alerts_Open"].sum()),
        "avg_abs_error": float(monitoring_df["Absolute_Forecast_Error_Days"].mean()),
    }


def _safe_metric(value: float, digits: int = 1) -> str:
    return f"{value:.{digits}f}"


def _persist_run(payload: dict[str, Any]) -> None:
    try:
        _initialize_database()
        save_session_run(
            project_text=payload["project_text"],
            mode=payload["mode"],
            params={
                "sample": payload["sample"],
                "max_tasks": payload["max_tasks"],
                "portfolio_projects": int(payload["portfolio_summary"]["projects"]),
            },
            tasks=payload["tasks"],
            deadline_days=payload["deadline_days"],
            iterations=payload["iterations"],
            seed=payload["seed"],
            metrics=payload["metrics"],
            completion_times=payload["completion"],
            scenarios_df=payload["scenarios_df"],
            ml_features_df=payload["ml_features_df"],
            ml_predictions_df=payload["ml_predictions_df"],
            model_version=str(payload["model_status"].get("model_version", settings.risk_model_version)),
        )
    except Exception:
        # Keep the presentation flow resilient even if SQLite is unavailable.
        return


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
            portfolio_df = _load_portfolio_history()
            monitoring_df = _load_monitoring_snapshot()
            model_metrics = _load_model_metrics()
            portfolio_summary = _portfolio_summary(portfolio_df)
            monitoring_summary = _monitoring_summary(monitoring_df)

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
            "portfolio_df": portfolio_df,
            "monitoring_df": monitoring_df,
            "model_metrics": model_metrics,
            "portfolio_summary": portfolio_summary,
            "monitoring_summary": monitoring_summary,
        }
        st.session_state.saas_payload = payload
        _persist_run(payload)

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


def _current_payload() -> dict[str, Any]:
    _ensure_demo_payload()
    return st.session_state.saas_payload


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
    logo_uri = _logo_data_uri()

    ticker_markup = "".join(f"<span class='ticker-item'>{item}</span>" for item in HOME_TICKER_ITEMS)

    st.markdown(
        dedent(
            f"""
            <div class="hero-shell">
              <div class="home-hero-stage">
                <div class="glass ticker-shell home-hero-ticker">
                  <div class="ticker-mask">
                    <div class="ticker-track">{ticker_markup}{ticker_markup}</div>
                  </div>
                </div>
                <div class="home-logo-stack">
                  <div class="home-logo-frame">
                    {f'<img src="{logo_uri}" class="home-logo-image" alt="certAIn logo" />' if logo_uri else _footer_brand_markup()}
                  </div>
                  <div class="home-powered-pill">
                    <span class="home-powered-glyph">✦</span>
                    <span>Powered by Advanced AI</span>
                    <span class="home-powered-dot"></span>
                  </div>
                </div>
                <h1 class="home-hero-title">
                  <span>Predict Project Delays</span>
                  <span class="home-hero-emphasis">Before They Happen</span>
                </h1>
                <p class="home-hero-copy">
                  AI-powered forecasting using Monte Carlo simulation and dependency analysis.
                </p>
                <div class="home-live-pill">
                  <span class="home-live-dot"></span>
                  <span>AI analyzing 2,847 task dependencies...</span>
                </div>
                <div class="home-hero-actions">
                  <a href="{_href("product")}" class="btn btn-primary btn-outline-cta">View Product Demo</a>
                </div>
                <div class="home-preview-shell">
                  <div class="home-preview-grid">
                    <div class="home-preview-card">
                      <div class="home-preview-head">
                        <span class="home-preview-icon">◫</span>
                        <span>Completion Probability</span>
                      </div>
                      <div class="home-chart-wrap">
                        <div class="home-chart-bars">
                          <span class="home-chart-bar" style="height:18px;"></span>
                          <span class="home-chart-bar" style="height:34px;"></span>
                          <span class="home-chart-bar" style="height:54px;"></span>
                          <span class="home-chart-bar" style="height:78px;"></span>
                          <span class="home-chart-bar" style="height:96px;"></span>
                          <span class="home-chart-bar" style="height:102px;"></span>
                          <span class="home-chart-bar" style="height:90px;"></span>
                          <span class="home-chart-bar" style="height:60px;"></span>
                          <span class="home-chart-bar" style="height:34px;"></span>
                          <span class="home-chart-bar" style="height:14px;"></span>
                        </div>
                        <div class="home-chart-axis"></div>
                        <div class="home-chart-caption">P50: March 15 · P80: March 22</div>
                      </div>
                    </div>
                    <div class="home-preview-card">
                      <div class="home-preview-head">
                        <span class="home-preview-icon">⬡</span>
                        <span>Risk Alerts</span>
                      </div>
                      <div class="home-alert-stack">
                        <div class="home-alert-item high">
                          <span class="home-alert-dot"></span>
                          <span class="home-alert-copy">API Integration at risk — 78% delay probability</span>
                        </div>
                        <div class="home-alert-item medium">
                          <span class="home-alert-dot"></span>
                          <span class="home-alert-copy">Database migration — resource bottleneck</span>
                        </div>
                        <div class="home-alert-item low">
                          <span class="home-alert-dot"></span>
                          <span class="home-alert-copy">Frontend sprint on track — 95% confidence</span>
                        </div>
                      </div>
                    </div>
                    <div class="home-preview-card">
                      <div class="home-preview-head">
                        <span class="home-preview-icon">↗</span>
                        <span>Project Timeline</span>
                      </div>
                      <div class="home-timeline-stack">
                        <div class="home-timeline-row">
                          <div class="home-timeline-top"><span>Design Phase</span><span>100%</span></div>
                          <div class="home-timeline-bar"><span style="width:100%;"></span></div>
                        </div>
                        <div class="home-timeline-row">
                          <div class="home-timeline-top"><span>Development</span><span>72%</span></div>
                          <div class="home-timeline-bar"><span style="width:72%;"></span></div>
                        </div>
                        <div class="home-timeline-row">
                          <div class="home-timeline-top"><span>Testing</span><span>30%</span></div>
                          <div class="home-timeline-bar"><span style="width:30%; background:rgba(255,255,255,0.26);"></span></div>
                        </div>
                        <div class="home-timeline-row">
                          <div class="home-timeline-top"><span>Launch</span><span>0%</span></div>
                          <div class="home-timeline-bar"><span style="width:0%;"></span></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="home-proof-strip">
                  <div class="home-proof-item">
                    <div class="home-proof-value">10000+</div>
                    <div class="home-proof-label">Monte Carlo Simulations</div>
                    <div class="home-proof-copy">Per project forecast</div>
                  </div>
                  <div class="home-proof-item">
                    <div class="home-proof-value">98.7%</div>
                    <div class="home-proof-label">Forecast Accuracy</div>
                    <div class="home-proof-copy">Validated across 500+ projects</div>
                  </div>
                  <div class="home-proof-item">
                    <div class="home-proof-value">47%</div>
                    <div class="home-proof-label">Risk Reduction</div>
                    <div class="home-proof-copy">Average across all clients</div>
                  </div>
                  <div class="home-proof-item">
                    <div class="home-proof-value">3x</div>
                    <div class="home-proof-label">Faster Decisions</div>
                    <div class="home-proof-copy">Compared to traditional PM</div>
                  </div>
                </div>
                <div class="home-intelligence-shell">
                  <div class="home-intelligence-head">
                    <div class="home-intelligence-pill">
                      <span class="home-intelligence-pill-glyph">⌘</span>
                      <span>AI-Powered Features</span>
                    </div>
                    <h2 class="home-intelligence-title">Intelligence at Every Level</h2>
                    <p class="home-intelligence-copy">
                      From task planning to executive reporting — certAIn covers the entire project lifecycle.
                    </p>
                  </div>
                  <div class="home-intelligence-grid">
                    <div class="home-intelligence-card">
                      <div class="home-intelligence-icon-shell">⌘</div>
                      <h3>AI Project Planning</h3>
                      <p>Automatically structure projects with intelligent task decomposition and dependency mapping.</p>
                    </div>
                    <div class="home-intelligence-card">
                      <div class="home-intelligence-icon-shell">∿</div>
                      <h3>Monte Carlo Forecasting</h3>
                      <p>Run thousands of simulations to predict completion dates with statistical confidence.</p>
                    </div>
                    <div class="home-intelligence-card">
                      <div class="home-intelligence-icon-shell">◈</div>
                      <h3>Critical Path Risk Detection</h3>
                      <p>Identify bottlenecks and vulnerable dependencies before they cause delays.</p>
                    </div>
                    <div class="home-intelligence-card">
                      <div class="home-intelligence-icon-shell">↗</div>
                      <h3>Explainable AI Insights</h3>
                      <p>Understand why delays happen with transparent AI reasoning and recommendations.</p>
                    </div>
                    <div class="home-intelligence-card">
                      <div class="home-intelligence-icon-shell">▤</div>
                      <h3>Executive Reporting</h3>
                      <p>Generate stakeholder-ready reports with health scores and mitigation plans.</p>
                    </div>
                    <div class="home-intelligence-card">
                      <div class="home-intelligence-icon-shell">◫</div>
                      <h3>What-If Scenario Simulation</h3>
                      <p>Model budget, timeline, and resource changes to see their impact before committing decisions.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            """,
        ),
        unsafe_allow_html=True,
    )

    _section_intro(
        "Proof points",
        "Enterprise SaaS framing with metrics that feel presentation-ready",
        "These signals are designed to make the product story immediately legible before you move into the live dashboard.",
    )
    st.markdown(
        """
        <div class="home-testimonial-shell">
          <div class="home-testimonial-grid">
            <div class="home-testimonial-card">
              <p class="home-testimonial-quote">"certAIn reduced our project overruns by 40%. The Monte Carlo simulations gave us confidence we never had before."</p>
              <div class="home-testimonial-author">
                <strong>Sarah Chen</strong>
                <span>VP Engineering, TechCorp</span>
              </div>
            </div>
            <div class="home-testimonial-card">
              <p class="home-testimonial-quote">"The AI risk detection caught a critical dependency issue that would have delayed our launch by 3 months."</p>
              <div class="home-testimonial-author">
                <strong>Marcus Weber</strong>
                <span>Program Director, Siemens Digital</span>
              </div>
            </div>
            <div class="home-testimonial-card">
              <p class="home-testimonial-quote">"Finally, a tool that speaks the language of project managers. The executive reports are exactly what our stakeholders need."</p>
              <div class="home-testimonial-author">
                <strong>Elena Rodriguez</strong>
                <span>PMO Lead, Consulting Firm</span>
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        dedent(
            f"""
            <div class="home-cta-shell">
              <div class="home-cta-pill">
                <span class="home-cta-pill-glyph">✦</span>
                <span>Start in under 2 minutes</span>
              </div>
              <h2 class="home-cta-title">Ready to predict your project's future?</h2>
              <p class="home-cta-copy">Start forecasting with AI in minutes. No credit card required.</p>
              <a href="{_href("dashboard")}" class="btn btn-primary btn-outline-cta">Start Free Trial</a>
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
    _ensure_demo_payload()
    payload = st.session_state.saas_payload
    portfolio_df = payload["portfolio_df"]
    monitoring_df = payload["monitoring_df"]
    model_metrics = payload["model_metrics"]

    timeline_df = (
        portfolio_df[["Project_ID", "Planned_Duration_Days", "Actual_Duration_Days"]]
        .sort_values("Planned_Duration_Days")
        .head(40)
    )
    area_figure = go.Figure()
    area_figure.add_trace(
        go.Scatter(
            x=timeline_df["Project_ID"],
            y=timeline_df["Planned_Duration_Days"],
            mode="lines+markers",
            name="Planned timeline",
            line=dict(color="#64a2ff", width=3),
        )
    )
    area_figure.add_trace(
        go.Scatter(
            x=timeline_df["Project_ID"],
            y=timeline_df["Actual_Duration_Days"],
            mode="lines+markers",
            name="Actual timeline",
            line=dict(color="#18d1c7", width=3),
            fill="tonexty",
            fillcolor="rgba(24, 209, 199, 0.14)",
        )
    )
    area_figure.update_layout(
        title="Predicted vs actual project timelines",
        xaxis_title="Portfolio sample",
        yaxis_title="Duration (days)",
    )

    confidence_df = monitoring_df.copy()
    confidence_df["Snapshot_Month"] = pd.to_datetime(confidence_df["Snapshot_Month"])
    confidence_df = (
        confidence_df.groupby("Snapshot_Month", as_index=False)
        .agg(
            avg_confidence=("Prediction_Confidence", "mean"),
            avg_p80=("P80_Forecast_Days", "mean"),
            avg_actual=("Actual_Completion_Days", "mean"),
        )
        .sort_values("Snapshot_Month")
    )
    confidence_figure = go.Figure()
    confidence_figure.add_trace(
        go.Scatter(
            x=confidence_df["Snapshot_Month"],
            y=confidence_df["avg_p80"],
            mode="lines+markers",
            name="P80 forecast",
            line=dict(color="#f5c56b", width=3),
        )
    )
    confidence_figure.add_trace(
        go.Scatter(
            x=confidence_df["Snapshot_Month"],
            y=confidence_df["avg_actual"],
            mode="lines+markers",
            name="Actual completion",
            line=dict(color="#76e7ff", width=3),
        )
    )
    confidence_figure.update_layout(
        title="Confidence interval tracking",
        xaxis_title="Monitoring month",
        yaxis_title="Average completion days",
    )

    selected_model = model_metrics.get("selected_model_name", "unknown")
    cv_macro = model_metrics.get("cv_macro_f1_mean", 0.0) * 100.0
    advisory_high = 0
    if not payload["ml_predictions_df"].empty and "Predicted_Risk_Level" in payload["ml_predictions_df"]:
        advisory_high = int((payload["ml_predictions_df"]["Predicted_Risk_Level"] == "High").sum())

    st.markdown(
        dedent(
            f"""
            <div class="page-shell">
              <div class="page-grid">
                <div class="glass page-hero-card">
                  <span class="kicker">AI Forecasting</span>
                  <h1 class="page-title">Connect forecasts to the real model, not just polished copy.</h1>
                  <p class="page-copy">
                    This page now uses the loaded risk classifier, the monitoring snapshot, and the portfolio history
                    to tell a more credible forecasting story.
                  </p>
                </div>
                <div class="glass page-hero-card">
                  <span class="eyebrow">Connected model facts</span>
                  <div class="data-pair"><span>Selected model</span><strong>{selected_model}</strong></div>
                  <div class="data-pair"><span>Cross-val macro F1</span><strong>{cv_macro:.1f}%</strong></div>
                  <div class="data-pair"><span>Live high-risk tasks</span><strong>{advisory_high}</strong></div>
                  <div class="data-pair"><span>Monitoring coverage</span><strong>{len(monitoring_df)} snapshots</strong></div>
                </div>
              </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    metric_cols = st.columns(4)
    metric_cols[0].metric("Model Version", model_metrics.get("model_version", "unknown"))
    metric_cols[1].metric("Selected Model", selected_model.replace("_", " ").title())
    metric_cols[2].metric("CV Macro F1", f"{cv_macro:.1f}%")
    metric_cols[3].metric("Avg Monitoring Confidence", f"{payload['monitoring_summary']['avg_confidence']:.1f}%")

    chart_cols = st.columns(2, gap="large")
    with chart_cols[0]:
        st.plotly_chart(_theme_chart(area_figure), use_container_width=True)
    with chart_cols[1]:
        st.plotly_chart(_theme_chart(confidence_figure), use_container_width=True)

    _section_intro(
        "Forecast insights",
        "The page combines live advisory scoring and portfolio evidence",
        "That means your AI forecasting story is now tied to the actual classifier, portfolio duration history, and monitoring confidence data.",
    )

    st.markdown(
        dedent(
            f"""
            <div class="detail-grid">
              <div class="detail-card">
                <h3>Live advisory scoring</h3>
                <p>{len(payload['ml_predictions_df'])} task rows were scored using the loaded <code>risk_classifier.joblib</code> artifact.</p>
              </div>
              <div class="detail-card">
                <h3>Forecast drift tracking</h3>
                <p>Average monitoring drift is {_safe_metric(payload['monitoring_summary']['avg_drift'], 3)}, based on <code>risk_monitoring_snapshot.csv</code>.</p>
              </div>
              <div class="detail-card">
                <h3>Portfolio grounding</h3>
                <p>Timeline visuals are drawn from <code>project_portfolio_history.csv</code> so the story reflects historical planning outcomes.</p>
              </div>
            </div>
            """
        ),
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
                <a href="{_href("login")}" class="btn btn-primary btn-outline-cta">Start Trial</a>
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


def _render_contact() -> None:
    st.markdown(
        """
        <div class="page-shell">
          <div class="page-grid">
            <div class="glass page-hero-card">
              <span class="kicker">Contact Us</span>
              <h1 class="page-title">Talk to the team behind cert<span class="ai-gradient">AI</span>n.</h1>
              <p class="page-copy">
                Book a demo, discuss enterprise rollout, or use this page in your capstone presentation to show a production-style contact journey.
              </p>
            </div>
            <div class="glass page-hero-card">
              <span class="eyebrow">Direct lines</span>
              <div class="data-pair"><span>Email</span><strong>hello@certain.ai</strong></div>
              <div class="data-pair"><span>Phone</span><strong>+49 30 5555 2040</strong></div>
              <div class="data-pair"><span>Sales</span><strong>enterprise@certain.ai</strong></div>
              <div class="data-pair"><span>Support SLA</span><strong>&lt; 2 business hours</strong></div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        with st.form("contact_form"):
            st.text_input("Name", key="contact_name")
            st.text_input("Email", key="contact_email")
            st.text_input("Company", key="contact_company")
            st.selectbox("Subject", ["Book demo", "Enterprise inquiry", "Partnership", "Support"], key="contact_subject")
            st.text_area("Message", height=180, key="contact_message")
            submitted = st.form_submit_button("Send message", type="primary", use_container_width=True)
            if submitted:
                st.success("Your request has been captured for the demo flow.")
    with right:
        st.markdown(
            """
            <div class="feature-grid">
              <div class="feature-card">
                <span class="eyebrow">Berlin HQ</span>
                <h3>Alexanderplatz 8</h3>
                <p>10178 Berlin<br/>Germany</p>
              </div>
              <div class="feature-card">
                <span class="eyebrow">London</span>
                <h3>Canary Wharf</h3>
                <p>25 Bank Street<br/>London E14</p>
              </div>
              <div class="feature-card">
                <span class="eyebrow">New York</span>
                <h3>Hudson Yards</h3>
                <p>10th Avenue<br/>New York, NY</p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="history-card" style="margin-top:1rem;">
              <strong style="font-family:Sora,sans-serif;">Social</strong>
              <p>LinkedIn · X · GitHub · YouTube</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("Can certAIn connect to Jira, Asana, and MS Project?"):
        st.write("Yes. The Tools Integration page includes those connectors in the SaaS story.")
    with st.expander("Does the platform support executive reporting?"):
        st.write("Yes. Executive Summary and Decision Hub are designed for stakeholder-ready communication.")
    with st.expander("Can the AI model be monitored after deployment?"):
        st.write("Yes. The dashboard reads `risk_monitoring_snapshot.csv` to visualize monitoring drift and confidence.")


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

    dataset_cols = st.columns(4)
    dataset_cols[0].metric("Portfolio Projects", f"{int(payload['portfolio_summary']['projects'])}")
    dataset_cols[1].metric("Portfolio Delay Rate", f"{payload['portfolio_summary']['delayed_pct']:.1f}%")
    dataset_cols[2].metric("Monitoring Accuracy", f"{payload['monitoring_summary']['accuracy_pct']:.1f}%")
    dataset_cols[3].metric("Open Monitoring Alerts", f"{int(payload['monitoring_summary']['alerts_open'])}")

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


def _render_user_guide() -> None:
    _render_command_bar()
    st.markdown(
        """
        <div class="page-shell">
          <div class="glass dashboard-banner">
            <span class="kicker">User Guide</span>
            <h1 class="page-title">Welcome to the certAIn workspace.</h1>
            <p class="page-copy">
              This landing page helps judges and users understand how to move through the platform from upload to executive reporting.
            </p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    checklist_cols = st.columns(4, gap="large")
    checklist_items = [
        ("1", "Upload your first project"),
        ("2", "Run AI analysis"),
        ("3", "Review risk assessment"),
        ("4", "Generate executive report"),
    ]
    for column, (step, label) in zip(checklist_cols, checklist_items):
        column.markdown(
            f"""
            <div class="history-card">
              <span class="eyebrow">Step {step}</span>
              <strong style="font-family:Sora,sans-serif;">{label}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

    quick_cols = st.columns(4)
    labels = ["Upload Project", "Run Risk Analysis", "View Reports", "Explore AI Features"]
    routes = ["upload", "risk-intelligence", "summary", "forecasting"]
    for col, label, route in zip(quick_cols, labels, routes):
        with col:
            if st.button(label, key=f"guide_{route}", use_container_width=True):
                _set_query_page(route)
                st.rerun()

    st.markdown(
        """
        <div class="history-card" style="margin-top:1rem;">
          <strong style="font-family:Sora,sans-serif;">Spotlight Tip</strong>
          <p>
            To use <strong>Project Spotlight</strong>, press <strong>⌘ K</strong> on Mac or
            <strong>Ctrl K</strong> on Windows/Linux to instantly open the command search and run actions
            from anywhere in the platform.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_decision_hub() -> None:
    _render_command_bar()
    payload = _current_payload()
    portfolio = payload["portfolio_summary"]
    monitoring = payload["monitoring_summary"]
    metrics = payload["metrics"]

    health_score = max(
        32.0,
        min(
            96.0,
            100.0
            - (metrics["delay_probability"] * 42.0)
            - (portfolio["delayed_pct"] * 0.22)
            - (monitoring["avg_drift"] * 18.0),
        ),
    )

    gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=health_score,
            number={"suffix": ""},
            title={"text": "Project health score"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#64a2ff"},
                "bgcolor": "rgba(255,255,255,0.04)",
                "steps": [
                    {"range": [0, 50], "color": "rgba(255,127,140,0.28)"},
                    {"range": [50, 75], "color": "rgba(245,197,107,0.2)"},
                    {"range": [75, 100], "color": "rgba(24,209,199,0.18)"},
                ],
            },
        )
    )
    gauge.update_layout(height=360)

    st.plotly_chart(_theme_chart(gauge), use_container_width=True)

    metric_cols = st.columns(4)
    metric_cols[0].metric("Schedule Performance", f"{max(0.7, 1 - metrics['delay_probability'] * 0.25):.2f}")
    metric_cols[1].metric("Cost Performance", f"{max(0.6, 1 - portfolio['avg_budget_overrun'] / 100):.2f}")
    metric_cols[2].metric("Risk Score", f"{metrics['delay_probability'] * 100:.1f}")
    metric_cols[3].metric("Team Velocity", f"{max(62.0, 100 - portfolio['avg_forecast_error']):.1f}")

    st.markdown(
        f"""
        <div class="history-card">
          <strong style="font-family:Sora,sans-serif;">AI recommendations</strong>
          <p>Increase mitigation on <strong>{payload['drivers'][0]['task_name'] if payload['drivers'] else 'critical dependencies'}</strong>, review the scenario lab before committing the deadline, and use the monitoring drift signal ({monitoring['avg_drift']:.3f}) to explain why executive caution is still justified.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_task_architect() -> None:
    _render_command_bar()
    payload = _current_payload()
    st.markdown(
        """
        <div class="page-shell">
          <div class="glass dashboard-banner">
            <span class="kicker">AI Task Architect</span>
            <h1 class="page-title">Inspect the generated work structure and dependency graph.</h1>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    graph_col, task_col = st.columns([1.0, 1.0], gap="large")
    with graph_col:
        st.plotly_chart(_theme_chart(dependency_graph_figure(payload["graph"], payload["critical_path"])), use_container_width=True)
    with task_col:
        tasks_df = pd.DataFrame(payload["tasks"])
        st.dataframe(tasks_df, use_container_width=True, hide_index=True)
        st.markdown(
            f"""
            <div class="history-card">
              <strong style="font-family:Sora,sans-serif;">Architect notes</strong>
              <p>{len(payload['tasks'])} tasks were generated for this workspace. The baseline critical path spans {payload['critical_path_days']:.1f} days.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_risk_intelligence() -> None:
    _render_command_bar()
    payload = _current_payload()
    portfolio_df = payload["portfolio_df"].copy()
    monitoring_df = payload["monitoring_df"].copy()
    model_metrics = payload["model_metrics"]

    portfolio_df["ProbabilityProxy"] = (
        portfolio_df["Weather_Risk_Index"] + portfolio_df["Procurement_Risk_Index"]
    ) / 2
    heatmap = px.scatter(
        portfolio_df,
        x="ProbabilityProxy",
        y="Budget_Overrun_Pct",
        color="Outcome_Risk_Level",
        size="Complexity_Score",
        hover_name="Project_ID",
        title="Risk heat map: portfolio projects",
        labels={"ProbabilityProxy": "Probability proxy", "Budget_Overrun_Pct": "Impact proxy (%)"},
        color_discrete_map={"High": "#ff7f8c", "Medium": "#f5c56b", "Low": "#18d1c7"},
    )

    monitoring_df["Snapshot_Month"] = pd.to_datetime(monitoring_df["Snapshot_Month"])
    drift_df = monitoring_df.groupby("Snapshot_Month", as_index=False).agg(
        avg_drift=("Drift_Score", "mean"),
        accuracy=("Predicted_Risk_Level", lambda s: 0),  # placeholder to merge below
    )
    accuracy_df = (
        monitoring_df.assign(match=monitoring_df["Predicted_Risk_Level"] == monitoring_df["Actual_Risk_Level"])
        .groupby("Snapshot_Month", as_index=False)["match"]
        .mean()
    )
    drift_df = drift_df.drop(columns=["accuracy"]).merge(accuracy_df, on="Snapshot_Month", how="left")
    drift_line = go.Figure()
    drift_line.add_trace(
        go.Scatter(
            x=drift_df["Snapshot_Month"],
            y=drift_df["avg_drift"],
            mode="lines+markers",
            name="Avg drift",
            line=dict(color="#ff7f8c", width=3),
        )
    )
    drift_line.add_trace(
        go.Scatter(
            x=drift_df["Snapshot_Month"],
            y=drift_df["match"] * 100.0,
            mode="lines+markers",
            name="Accuracy %",
            line=dict(color="#18d1c7", width=3),
            yaxis="y2",
        )
    )
    drift_line.update_layout(
        title="Risk monitoring trend",
        yaxis_title="Drift score",
        yaxis2=dict(title="Accuracy %", overlaying="y", side="right"),
    )

    high_risk_rows = pd.DataFrame()
    if not payload["ml_predictions_df"].empty:
        high_risk_rows = payload["ml_predictions_df"].copy()
        high_cols = [col for col in high_risk_rows.columns if "Probability_High" in col]
        if high_cols:
            high_risk_rows = high_risk_rows.sort_values(high_cols[0], ascending=False).head(5)

    metric_cols = st.columns(4)
    metric_cols[0].metric("Monitoring Accuracy", f"{payload['monitoring_summary']['accuracy_pct']:.1f}%")
    metric_cols[1].metric("Average Drift", f"{payload['monitoring_summary']['avg_drift']:.3f}")
    metric_cols[2].metric("Active Alerts", f"{int(payload['monitoring_summary']['alerts_open'])}")
    metric_cols[3].metric("Model Selected", model_metrics.get("selected_model_name", "unknown"))

    chart_cols = st.columns(2, gap="large")
    with chart_cols[0]:
        st.plotly_chart(_theme_chart(heatmap), use_container_width=True)
    with chart_cols[1]:
        st.plotly_chart(_theme_chart(drift_line), use_container_width=True)

    if not high_risk_rows.empty:
        st.dataframe(high_risk_rows, use_container_width=True, hide_index=True)

    feature_importance = model_metrics.get("feature_importance", [])[:5]
    bullets = "".join(
        f"<li><strong>{item['feature']}</strong>: {float(item['importance']):.4f}</li>"
        for item in feature_importance
    )
    st.markdown(
        f"""
        <div class="history-card">
          <strong style="font-family:Sora,sans-serif;">Mitigation recommendations</strong>
          <p>The current joblib-backed classifier highlights these leading explanatory signals:</p>
          <ul>{bullets}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_simulator() -> None:
    _render_command_bar()
    st.markdown(
        """
        <style>
        .st-key-sim_run_button div.stButton > button,
        .st-key-sim_run_button button {
          width: 100% !important;
          justify-content: center !important;
          min-height: 52px !important;
          padding: 0 1rem !important;
          border: 1.5px solid transparent !important;
          border-radius: 16px !important;
          color: #f5fbff !important;
          background-color: transparent !important;
          background:
            linear-gradient(180deg, #030811, #02060d) padding-box,
            linear-gradient(90deg, var(--purple-strong) 0%, var(--blue-strong) 52%, var(--teal) 100%) border-box !important;
          box-shadow: none !important;
          font-weight: 700 !important;
        }

        .st-key-sim_run_button div.stButton > button:hover,
        .st-key-sim_run_button button:hover {
          transform: translateY(-1px);
          filter: brightness(1.03);
          box-shadow: 0 0 0 1px rgba(117, 231, 255, 0.16) !important;
        }

        .st-key-sim_run_button div.stButton > button[kind="primary"],
        .st-key-sim_run_button button[kind="primary"] {
          background-color: transparent !important;
          background:
            linear-gradient(180deg, #030811, #02060d) padding-box,
            linear-gradient(90deg, var(--purple-strong) 0%, var(--blue-strong) 52%, var(--teal) 100%) border-box !important;
          box-shadow: 0 0 0 1px rgba(117, 231, 255, 0.22) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    payload = _current_payload()
    variance = st.slider("Duration variance multiplier", min_value=0.5, max_value=3.0, value=1.0, step=0.1, key="sim_variance")
    runs = st.slider("Number of simulations", min_value=1000, max_value=10000, value=min(3000, int(payload["iterations"])), step=500, key="sim_runs")
    if st.button("Run AI Simulation", key="sim_run_button", type="primary", use_container_width=True):
        tasks = copy.deepcopy(payload["tasks"])
        for task in tasks:
            task["std_dev"] = float(task["std_dev"]) * float(variance)
        graph = build_project_graph(tasks)
        completion = run_monte_carlo(graph, iterations=int(runs), seed=payload["seed"])
        sim_metrics = compute_metrics(completion, payload["deadline_days"])
        hist = completion_histogram(completion, payload["deadline_days"], sim_metrics["p50"], sim_metrics["p80"])
        st.session_state["simulator_result"] = {"completion": completion, "metrics": sim_metrics, "figure": hist}

    result = st.session_state.get("simulator_result")
    if result:
        cols = st.columns(3)
        cols[0].metric("P50 Timeline", f"{result['metrics']['p50']:.1f}d")
        cols[1].metric("P80 Timeline", f"{result['metrics']['p80']:.1f}d")
        cols[2].metric("Delay Probability", f"{result['metrics']['delay_probability'] * 100:.1f}%")
        st.plotly_chart(_theme_chart(result["figure"]), use_container_width=True)
        st.progress(min(1.0, runs / 10000))
        st.caption("Sampling distributions → Computing paths → Scoring risks")


def _render_what_if() -> None:
    _render_command_bar()
    payload = _current_payload()
    capacity_factor = st.slider("Capacity factor", min_value=0.65, max_value=1.0, value=0.85, step=0.05, key="scenario_capacity")
    deadline_factor = st.slider("Aggressive deadline factor", min_value=0.65, max_value=1.0, value=0.85, step=0.05, key="scenario_deadline")
    scenarios_df = scenario_comparison(
        build_project_graph,
        payload["tasks"],
        deadline_days=payload["deadline_days"],
        iterations=payload["iterations"],
        seed=payload["seed"],
        capacity_factor=float(capacity_factor),
        aggressive_deadline_factor=float(deadline_factor),
    )
    st.plotly_chart(_theme_chart(scenario_comparison_chart(scenarios_df)), use_container_width=True)
    st.dataframe(scenarios_df, use_container_width=True, hide_index=True)


def _render_history() -> None:
    _render_command_bar()
    _initialize_database()
    recent_runs = list_recent_runs(limit=12)
    st.markdown(
        """
        <div class="page-shell">
          <div class="glass dashboard-banner">
            <span class="kicker">Version History</span>
            <h1 class="page-title">Compare recent planning runs and retrieve saved workspaces.</h1>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not recent_runs:
        st.info("No saved runs yet. Generate a forecast from the dashboard first.")
        return

    labels = [
        f"Run {run['simulation_run_id']} · {run['created_at']} · {run['delay_probability'] * 100:.1f}% risk"
        for run in recent_runs
    ]
    selected_label = st.selectbox("Saved workspace", labels, key="history_selected")
    selected_index = labels.index(selected_label)
    selected_run = recent_runs[selected_index]
    details = get_run_details(selected_run["simulation_run_id"])

    if details:
        cols = st.columns(4)
        cols[0].metric("Delay Probability", f"{details['metrics'].get('delay_probability', 0.0) * 100:.1f}%")
        cols[1].metric("P80", f"{details['metrics'].get('p80', 0.0):.1f}d")
        cols[2].metric("Iterations", f"{details['iterations']}")
        cols[3].metric("Mode", details["mode"])
        st.dataframe(pd.DataFrame(details["tasks"]), use_container_width=True, hide_index=True)


def _render_summary() -> None:
    _render_command_bar()
    payload = _current_payload()
    model_metrics = payload["model_metrics"]
    summary_cols = st.columns(4)
    summary_cols[0].metric("Projects in history", f"{int(payload['portfolio_summary']['projects'])}")
    summary_cols[1].metric("Portfolio delay rate", f"{payload['portfolio_summary']['delayed_pct']:.1f}%")
    summary_cols[2].metric("Monitoring accuracy", f"{payload['monitoring_summary']['accuracy_pct']:.1f}%")
    summary_cols[3].metric("Selected model", model_metrics.get("selected_model_name", "unknown"))

    st.markdown(
        f"""
        <div class="history-card">
          <strong style="font-family:Sora,sans-serif;">AI narrative summary</strong>
          <p>
            The current workspace combines live Monte Carlo forecasting with a deployed advisory classifier.
            Portfolio history shows a {payload['portfolio_summary']['delayed_pct']:.1f}% delayed-project rate,
            while monitoring accuracy is {payload['monitoring_summary']['accuracy_pct']:.1f}% across recent snapshots.
            For the active plan, the recommended commitment is {payload['metrics']['p80']:.1f} days and the main driver is
            <strong>{payload['drivers'][0]['task_name'] if payload['drivers'] else 'not available'}</strong>.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    charts = st.columns(2, gap="large")
    with charts[0]:
        cost_df = payload["portfolio_df"].groupby("Portfolio_Segment", as_index=False)["Budget_Overrun_Pct"].mean()
        burn = px.bar(cost_df, x="Portfolio_Segment", y="Budget_Overrun_Pct", title="Budget burn profile by segment")
        st.plotly_chart(_theme_chart(burn), use_container_width=True)
    with charts[1]:
        milestone_df = pd.DataFrame(payload["tasks"])
        milestone_df["Cumulative"] = milestone_df["mean_duration"].cumsum()
        milestone = px.line(milestone_df, x="name", y="Cumulative", markers=True, title="Milestone tracker")
        st.plotly_chart(_theme_chart(milestone), use_container_width=True)

    st.download_button(
        "Export summary to JSON",
        data=_serialize_payload(payload),
        file_name="certain_executive_summary.json",
        mime="application/json",
        use_container_width=True,
    )


def _render_upload() -> None:
    _render_command_bar()
    st.markdown(
        """
        <div class="page-shell">
          <div class="glass dashboard-banner">
            <span class="kicker">Project Upload</span>
            <h1 class="page-title">Drop source files and preview how certAIn would parse them.</h1>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    uploaded = st.file_uploader("Upload .csv, .json, .xlsx, or .xml", type=["csv", "json", "xlsx", "xml", "mpp"])
    if uploaded is not None:
        st.success(f"Uploaded `{uploaded.name}`")
        if uploaded.name.lower().endswith(".csv"):
            preview_df = pd.read_csv(uploaded)
            st.dataframe(preview_df.head(20), use_container_width=True, hide_index=True)
        else:
            st.info("Preview is currently optimized for CSV uploads in this prototype.")

    st.markdown(
        """
        <div class="history-card">
          <strong style="font-family:Sora,sans-serif;">Supported templates</strong>
          <p>.mpp, .xlsx, .csv, .json, and .xml are represented in the interface to support the product story.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_integrations() -> None:
    _render_command_bar()
    integrations = [
        "Jira", "Asana", "Monday.com", "MS Project", "Trello", "Wrike",
        "Microsoft Planner", "Figma", "Google Workspace", "Bing", "Microsoft",
    ]
    cards = "".join(
        f"""
        <div class="feature-card">
          <span class="eyebrow">Available</span>
          <h3>{tool}</h3>
          <p>Connect planning data and sync project status into certAIn.</p>
        </div>
        """
        for tool in integrations
    )
    st.markdown(f"<div class='feature-grid'>{cards}</div>", unsafe_allow_html=True)


def _render_settings_page() -> None:
    _render_command_bar()
    left, right = st.columns(2, gap="large")
    with left:
        st.text_input("Profile name", value="certAIn Team", key="settings_name")
        st.text_input("Email", value=st.session_state.saas_user_email, key="settings_email")
        st.slider("AI sensitivity", min_value=0.1, max_value=1.0, value=float(st.session_state.saas_ai_sensitivity), key="saas_ai_sensitivity")
        st.slider("Confidence threshold", min_value=0.5, max_value=0.99, value=float(st.session_state.saas_confidence_threshold), key="saas_confidence_threshold")
    with right:
        st.toggle("Email alerts", value=bool(st.session_state.saas_email_alerts), key="saas_email_alerts")
        st.toggle("In-app alerts", value=bool(st.session_state.saas_in_app_alerts), key="saas_in_app_alerts")
        st.toggle("AI alerts", value=bool(st.session_state.saas_ai_alerts), key="saas_ai_alerts")
        st.selectbox("Language", ["English", "German", "French"], key="saas_language")
        st.selectbox("Region", ["Global", "EU", "US"], key="saas_region")


def main() -> None:
    _init_state()
    _inject_styles()
    page = _resolve_page()
    _inject_layout_state(page)
    _render_sidebar(page)
    _render_nav(page)
    _render_floating_shortcut(page)

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
    elif page == "contact":
        _render_contact()
    elif page == "about":
        _render_about()
    elif page == "login":
        _render_login()
    elif page == "guide":
        _render_user_guide()
    elif page == "decision-hub":
        _render_decision_hub()
    elif page == "task-architect":
        _render_task_architect()
    elif page == "risk-intelligence":
        _render_risk_intelligence()
    elif page == "simulator":
        _render_simulator()
    elif page == "what-if":
        _render_what_if()
    elif page == "history":
        _render_history()
    elif page == "summary":
        _render_summary()
    elif page == "upload":
        _render_upload()
    elif page == "integrations":
        _render_integrations()
    elif page == "settings-page":
        _render_settings_page()
    else:
        _render_dashboard()

    _render_footer()


if __name__ == "__main__":
    main()
