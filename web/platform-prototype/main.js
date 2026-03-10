const demoLibrary = {
  beta_release: {
    label: "certAIn beta release",
    brief:
      "Launch the certAIn Project Intelligence beta for enterprise PMO teams with onboarding, risk forecasting, stakeholder export, and a coach-ready presentation flow before the final capstone showcase.",
    scenarios: {
      baseline: {
        label: "Baseline commitment",
        riskLabel: "Risk watch",
        delayProb: 38,
        p80: 94,
        p50: 83,
        mean: 87,
        deadline: 90,
        confidence: 81,
        driver: "Integration hardening",
        executiveBrief:
          "The current plan is credible but fragile. Integration hardening is the main constraint, so the safer move is to preserve scope and commit against the P80 window.",
        summary:
          "Keep the current scope stable, preserve decision quality, and manage stakeholder expectations with a slightly safer commitment date.",
        distribution: [12, 16, 22, 28, 42, 58, 66, 74, 82, 90, 95, 90, 78, 61, 39, 22],
        p50Index: 8,
        p80Index: 11,
        deadlineIndex: 10,
        tasks: [
          { name: "Task generation reliability pass", owner: "AI", duration: "9d", risk: "Medium", critical: "Critical path" },
          { name: "Scenario engine QA", owner: "DS", duration: "11d", risk: "High", critical: "Critical path" },
          { name: "Stakeholder export and slide sync", owner: "PM", duration: "7d", risk: "Medium", critical: "Near-critical" },
          { name: "Demo deployment hardening", owner: "Ops", duration: "8d", risk: "High", critical: "Critical path" }
        ],
        signalItems: [
          { title: "Scenario engine QA", body: "Minor probability drift against aggressive deadline assumptions.", risk: "High", owner: "DS lead" },
          { title: "Demo deployment hardening", body: "Presentation-day resilience depends on mock-mode fallback and stable hosting.", risk: "High", owner: "Ops" },
          { title: "Stakeholder export sync", body: "Formatting debt is manageable if deck source remains frozen before demo week.", risk: "Medium", owner: "PM" },
          { title: "Narrative polish", body: "Low execution risk, but high presentation leverage for judge clarity.", risk: "Low", owner: "Team" }
        ],
        scenarioRows: [
          { label: "Scope stability", kpi: "High", metric: "No major cuts", tone: "Low" },
          { label: "Commitment confidence", kpi: "81%", metric: "Exec-safe", tone: "Low" },
          { label: "Mitigation urgency", kpi: "Focused", metric: "Integration first", tone: "Medium" }
        ],
        feed: [
          { time: "Now", title: "Sponsor readout", body: "Lead with risk-aware commitment instead of optimistic mean duration." },
          { time: "Next 24h", title: "Product decision", body: "Freeze deck narrative and align demo script with the P80 recommendation." },
          { time: "Before launch", title: "Ops checkpoint", body: "Verify mock mode, hosting, and export flow under presentation conditions." }
        ]
      },
      mitigate: {
        label: "Mitigate risk",
        riskLabel: "Recommended",
        delayProb: 24,
        p80: 88,
        p50: 79,
        mean: 82,
        deadline: 90,
        confidence: 88,
        driver: "Deployment hardening",
        executiveBrief:
          "This is the strongest decision path. A targeted mitigation sprint lowers schedule exposure without cutting core functionality or weakening the demo story.",
        summary:
          "Add temporary engineering support to deployment and QA, keep the deck freeze strict, and present this as the recommended commitment path.",
        distribution: [10, 14, 18, 28, 44, 60, 74, 86, 95, 90, 80, 60, 36, 24, 14, 8],
        p50Index: 7,
        p80Index: 10,
        deadlineIndex: 11,
        tasks: [
          { name: "Deployment hardening sprint", owner: "Ops", duration: "6d", risk: "Medium", critical: "Critical path" },
          { name: "Scenario engine QA", owner: "DS", duration: "9d", risk: "Medium", critical: "Critical path" },
          { name: "Evidence pack lock", owner: "PM", duration: "5d", risk: "Low", critical: "Protected" },
          { name: "Capstone demo rehearsal", owner: "Team", duration: "4d", risk: "Low", critical: "Near-critical" }
        ],
        signalItems: [
          { title: "Deployment hardening sprint", body: "Additional capacity materially lowers presentation-day failure risk.", risk: "Medium", owner: "Ops" },
          { title: "Scenario engine QA", body: "Residual risk remains but no longer dominates the schedule.", risk: "Medium", owner: "DS lead" },
          { title: "Evidence pack lock", body: "Business framing becomes stable enough for sponsor review.", risk: "Low", owner: "PM" },
          { title: "Capstone rehearsal", body: "Presentation coherence improves forecast confidence.", risk: "Low", owner: "Team" }
        ],
        scenarioRows: [
          { label: "Scope stability", kpi: "High", metric: "Core story preserved", tone: "Low" },
          { label: "Commitment confidence", kpi: "88%", metric: "Best option", tone: "Low" },
          { label: "Mitigation urgency", kpi: "Funded", metric: "1 focused sprint", tone: "Low" }
        ],
        feed: [
          { time: "Now", title: "Recommended path", body: "Present this as the decision-grade scenario for judges and stakeholders." },
          { time: "Next 24h", title: "Resource action", body: "Shift one contributor into deployment and QA hardening." },
          { time: "Before launch", title: "Confidence narrative", body: "Frame the reduced delay probability as the result of specific mitigation, not generic optimism." }
        ]
      },
      accelerate: {
        label: "Accelerate",
        riskLabel: "Watch escalation",
        delayProb: 49,
        p80: 97,
        p50: 85,
        mean: 89,
        deadline: 84,
        confidence: 69,
        driver: "Compressed QA window",
        executiveBrief:
          "Acceleration raises narrative appeal but pushes the system into a brittle state. This path should be presented as high-visibility, not recommended.",
        summary:
          "Compressing the timeline to chase an earlier milestone increases schedule fragility faster than it creates value.",
        distribution: [14, 16, 20, 26, 40, 52, 64, 74, 80, 82, 79, 74, 66, 49, 30, 18],
        p50Index: 8,
        p80Index: 12,
        deadlineIndex: 7,
        tasks: [
          { name: "Compressed QA window", owner: "DS", duration: "7d", risk: "High", critical: "Critical path" },
          { name: "Demo deployment hardening", owner: "Ops", duration: "7d", risk: "High", critical: "Critical path" },
          { name: "Narrative polish", owner: "PM", duration: "3d", risk: "Medium", critical: "Protected" },
          { name: "Launch cutover rehearsal", owner: "Team", duration: "5d", risk: "High", critical: "Near-critical" }
        ],
        signalItems: [
          { title: "Compressed QA window", body: "Highest failure probability due to reduced verification depth.", risk: "High", owner: "DS lead" },
          { title: "Launch cutover rehearsal", body: "Limited rehearsal coverage weakens demo confidence.", risk: "High", owner: "Team" },
          { title: "Narrative polish", body: "Fast to finish but no longer the controlling factor.", risk: "Medium", owner: "PM" },
          { title: "Deployment hardening", body: "Still exposed because earlier cutover reduces recovery time.", risk: "High", owner: "Ops" }
        ],
        scenarioRows: [
          { label: "Scope stability", kpi: "Medium", metric: "Cuts likely", tone: "Medium" },
          { label: "Commitment confidence", kpi: "69%", metric: "Not judge-safe", tone: "High" },
          { label: "Mitigation urgency", kpi: "Immediate", metric: "High strain", tone: "High" }
        ],
        feed: [
          { time: "Now", title: "Decision warning", body: "Use this scenario to show tradeoffs, not as the recommended commitment." },
          { time: "Next 24h", title: "Executive message", body: "Explain that earlier dates reduce resilience more than they improve value." },
          { time: "Before launch", title: "Fallback need", body: "Only proceed if you are willing to accept higher demo and schedule risk." }
        ]
      }
    }
  },
  erp_rollout: {
    label: "ERP rollout",
    brief:
      "Plan a 12-week ERP rollout across finance, procurement, and reporting teams with integration testing, training, and cutover support for regional stakeholders.",
    scenarios: {
      baseline: {
        label: "Baseline commitment",
        riskLabel: "Risk watch",
        delayProb: 42,
        p80: 83,
        p50: 74,
        mean: 77,
        deadline: 78,
        confidence: 79,
        driver: "Cross-system integration",
        executiveBrief:
          "The rollout is schedule-feasible, but integration and stakeholder training create a wide tail. A safer commitment should be defended with the P80 forecast.",
        summary:
          "Hold the current launch scope, but communicate that dependency risk sits inside integration and training readiness.",
        distribution: [10, 15, 19, 26, 38, 52, 66, 76, 90, 96, 88, 68, 48, 33, 20, 10],
        p50Index: 8,
        p80Index: 11,
        deadlineIndex: 9,
        tasks: [
          { name: "Integration mapping", owner: "Tech lead", duration: "13d", risk: "High", critical: "Critical path" },
          { name: "Regional training design", owner: "PMO", duration: "10d", risk: "Medium", critical: "Critical path" },
          { name: "Cutover rehearsal", owner: "Ops", duration: "6d", risk: "High", critical: "Near-critical" },
          { name: "Executive adoption review", owner: "Sponsor", duration: "4d", risk: "Low", critical: "Protected" }
        ],
        signalItems: [
          { title: "Integration mapping", body: "Most likely to propagate delay into testing and reporting.", risk: "High", owner: "Tech lead" },
          { title: "Cutover rehearsal", body: "Operational prep remains sensitive to upstream slippage.", risk: "High", owner: "Ops" },
          { title: "Regional training design", body: "Needs earlier alignment to prevent late rollout friction.", risk: "Medium", owner: "PMO" },
          { title: "Executive adoption review", body: "Low task risk, high communications importance.", risk: "Low", owner: "Sponsor" }
        ],
        scenarioRows: [
          { label: "Scope stability", kpi: "High", metric: "All regions", tone: "Low" },
          { label: "Commitment confidence", kpi: "79%", metric: "Manageable", tone: "Medium" },
          { label: "Mitigation urgency", kpi: "Training + integration", metric: "Dual focus", tone: "Medium" }
        ],
        feed: [
          { time: "Now", title: "PMO readout", body: "Anchor the story around integration risk and training readiness." },
          { time: "Next 24h", title: "Sponsor decision", body: "Decide whether to preserve all-region scope or stage the rollout." },
          { time: "Before launch", title: "Operations check", body: "Validate cutover rehearsal completeness against the P80 commitment." }
        ]
      },
      mitigate: {
        label: "Mitigate risk",
        riskLabel: "Recommended",
        delayProb: 27,
        p80: 79,
        p50: 72,
        mean: 74,
        deadline: 78,
        confidence: 86,
        driver: "Training readiness",
        executiveBrief:
          "Adding structured training prep and earlier integration checkpoints narrows the tail enough to support a confident launch recommendation.",
        summary:
          "This path balances sponsor confidence with execution realism and is the best presentation-quality recommendation.",
        distribution: [8, 10, 14, 20, 32, 48, 66, 80, 94, 91, 76, 58, 36, 20, 12, 7],
        p50Index: 7,
        p80Index: 10,
        deadlineIndex: 11,
        tasks: [
          { name: "Early integration checkpoint", owner: "Tech lead", duration: "10d", risk: "Medium", critical: "Critical path" },
          { name: "Regional champion training", owner: "PMO", duration: "8d", risk: "Low", critical: "Critical path" },
          { name: "Cutover rehearsal", owner: "Ops", duration: "5d", risk: "Medium", critical: "Near-critical" },
          { name: "Executive adoption review", owner: "Sponsor", duration: "4d", risk: "Low", critical: "Protected" }
        ],
        signalItems: [
          { title: "Regional champion training", body: "Becomes the leading control lever once integration risk is reduced.", risk: "Low", owner: "PMO" },
          { title: "Early integration checkpoint", body: "Removes downstream surprise and stabilizes testing.", risk: "Medium", owner: "Tech lead" },
          { title: "Cutover rehearsal", body: "Residual risk remains but no longer dominates.", risk: "Medium", owner: "Ops" },
          { title: "Executive adoption review", body: "Can proceed as planned with lower communications strain.", risk: "Low", owner: "Sponsor" }
        ],
        scenarioRows: [
          { label: "Scope stability", kpi: "High", metric: "All regions", tone: "Low" },
          { label: "Commitment confidence", kpi: "86%", metric: "Recommended", tone: "Low" },
          { label: "Mitigation urgency", kpi: "Preplanned", metric: "Low scramble", tone: "Low" }
        ],
        feed: [
          { time: "Now", title: "Recommended path", body: "Frame this as a deliberate investment in rollout reliability." },
          { time: "Next 24h", title: "Resource action", body: "Assign regional champions and schedule the integration checkpoint." },
          { time: "Before launch", title: "Final message", body: "Use improved confidence and narrower tail as sponsor talking points." }
        ]
      },
      accelerate: {
        label: "Accelerate",
        riskLabel: "Watch escalation",
        delayProb: 56,
        p80: 86,
        p50: 75,
        mean: 79,
        deadline: 72,
        confidence: 64,
        driver: "Training compression",
        executiveBrief:
          "Acceleration is possible only by shrinking the training window, which creates a fragile go-live and a difficult stakeholder narrative.",
        summary:
          "A faster launch date materially increases delivery and adoption risk and should be shown only as a tradeoff case.",
        distribution: [14, 18, 24, 30, 42, 55, 67, 76, 82, 84, 79, 70, 58, 40, 26, 15],
        p50Index: 8,
        p80Index: 12,
        deadlineIndex: 6,
        tasks: [
          { name: "Training compression", owner: "PMO", duration: "6d", risk: "High", critical: "Critical path" },
          { name: "Integration mapping", owner: "Tech lead", duration: "12d", risk: "High", critical: "Critical path" },
          { name: "Cutover rehearsal", owner: "Ops", duration: "4d", risk: "High", critical: "Near-critical" },
          { name: "Sponsor communications", owner: "Sponsor", duration: "3d", risk: "Medium", critical: "Protected" }
        ],
        signalItems: [
          { title: "Training compression", body: "Largest adoption risk increase across the acceleration path.", risk: "High", owner: "PMO" },
          { title: "Cutover rehearsal", body: "Less rehearsal coverage makes the launch more brittle.", risk: "High", owner: "Ops" },
          { title: "Integration mapping", body: "Still the main technical bottleneck.", risk: "High", owner: "Tech lead" },
          { title: "Sponsor communications", body: "Harder narrative because the date is optimistic against the risk profile.", risk: "Medium", owner: "Sponsor" }
        ],
        scenarioRows: [
          { label: "Scope stability", kpi: "Medium", metric: "Stretching teams", tone: "Medium" },
          { label: "Commitment confidence", kpi: "64%", metric: "Low", tone: "High" },
          { label: "Mitigation urgency", kpi: "Immediate", metric: "High pressure", tone: "High" }
        ],
        feed: [
          { time: "Now", title: "Tradeoff warning", body: "Acceleration looks attractive but weakens operational readiness." },
          { time: "Next 24h", title: "Leadership choice", body: "Decide whether earlier visibility is worth lower rollout confidence." },
          { time: "Before launch", title: "Fallback needed", body: "Keep a staged go-live fallback if this path is chosen." }
        ]
      }
    }
  },
  fitout_program: {
    label: "Construction fit-out",
    brief:
      "Forecast a commercial fit-out project with permitting, procurement, subcontractor sequencing, site inspection, and final client handover under a fixed deadline.",
    scenarios: {
      baseline: {
        label: "Baseline commitment",
        riskLabel: "Risk watch",
        delayProb: 45,
        p80: 118,
        p50: 103,
        mean: 108,
        deadline: 110,
        confidence: 76,
        driver: "Procurement lead time",
        executiveBrief:
          "The baseline plan is exposed to procurement and inspection dependencies. The deadline can be defended only if stakeholders accept meaningful schedule risk.",
        summary:
          "Maintain the current path but communicate that supplier and inspection variability dominate the tail.",
        distribution: [8, 12, 18, 26, 34, 46, 58, 71, 84, 93, 97, 88, 72, 52, 34, 18],
        p50Index: 8,
        p80Index: 11,
        deadlineIndex: 10,
        tasks: [
          { name: "Permit approval", owner: "PM", duration: "15d", risk: "Medium", critical: "Critical path" },
          { name: "Material procurement", owner: "Procurement", duration: "18d", risk: "High", critical: "Critical path" },
          { name: "Subcontractor sequencing", owner: "Site lead", duration: "12d", risk: "High", critical: "Near-critical" },
          { name: "Final inspection", owner: "Client rep", duration: "5d", risk: "Medium", critical: "Protected" }
        ],
        signalItems: [
          { title: "Material procurement", body: "Largest source of schedule volatility across the project.", risk: "High", owner: "Procurement" },
          { title: "Subcontractor sequencing", body: "Highly sensitive to supplier and permitting drift.", risk: "High", owner: "Site lead" },
          { title: "Permit approval", body: "Moderate uncertainty but still on the controlling chain.", risk: "Medium", owner: "PM" },
          { title: "Final inspection", body: "Low direct risk until upstream work slips.", risk: "Medium", owner: "Client rep" }
        ],
        scenarioRows: [
          { label: "Scope stability", kpi: "High", metric: "Full handover", tone: "Low" },
          { label: "Commitment confidence", kpi: "76%", metric: "Moderate", tone: "Medium" },
          { label: "Mitigation urgency", kpi: "Procurement first", metric: "Critical", tone: "High" }
        ],
        feed: [
          { time: "Now", title: "Client readout", body: "Anchor the narrative on procurement risk and the safer P80 completion date." },
          { time: "Next 24h", title: "Vendor action", body: "Escalate procurement dependencies and confirm inspection windows." },
          { time: "Before handover", title: "Site coordination", body: "Sequence subcontractors against the most constrained materials." }
        ]
      },
      mitigate: {
        label: "Mitigate risk",
        riskLabel: "Recommended",
        delayProb: 29,
        p80: 111,
        p50: 99,
        mean: 103,
        deadline: 110,
        confidence: 84,
        driver: "Inspection scheduling",
        executiveBrief:
          "Pre-ordering long-lead materials and locking inspection windows turns the schedule into a more defensible commitment without reducing delivery scope.",
        summary:
          "This is the recommended path because it protects handover quality while materially reducing deadline exposure.",
        distribution: [6, 9, 13, 18, 26, 40, 56, 73, 88, 96, 89, 70, 48, 30, 18, 10],
        p50Index: 7,
        p80Index: 10,
        deadlineIndex: 11,
        tasks: [
          { name: "Pre-order long-lead materials", owner: "Procurement", duration: "14d", risk: "Medium", critical: "Critical path" },
          { name: "Inspection slot reservation", owner: "PM", duration: "5d", risk: "Low", critical: "Critical path" },
          { name: "Subcontractor sequencing", owner: "Site lead", duration: "10d", risk: "Medium", critical: "Near-critical" },
          { name: "Final inspection", owner: "Client rep", duration: "5d", risk: "Low", critical: "Protected" }
        ],
        signalItems: [
          { title: "Pre-order long-lead materials", body: "Early action reduces the main uncertainty driver.", risk: "Medium", owner: "Procurement" },
          { title: "Inspection slot reservation", body: "Small effort with outsized schedule protection.", risk: "Low", owner: "PM" },
          { title: "Subcontractor sequencing", body: "Still needs active coordination but no longer dominates.", risk: "Medium", owner: "Site lead" },
          { title: "Final inspection", body: "Lower residual risk under a locked schedule.", risk: "Low", owner: "Client rep" }
        ],
        scenarioRows: [
          { label: "Scope stability", kpi: "High", metric: "Full handover", tone: "Low" },
          { label: "Commitment confidence", kpi: "84%", metric: "Recommended", tone: "Low" },
          { label: "Mitigation urgency", kpi: "Early procurement", metric: "Planned", tone: "Low" }
        ],
        feed: [
          { time: "Now", title: "Recommended path", body: "Show this as the strongest balance of client confidence and delivery realism." },
          { time: "Next 24h", title: "Procurement move", body: "Lock long-lead orders and inspection windows immediately." },
          { time: "Before handover", title: "Site message", body: "Sequence trades around the protected materials plan." }
        ]
      },
      accelerate: {
        label: "Accelerate",
        riskLabel: "Watch escalation",
        delayProb: 58,
        p80: 121,
        p50: 104,
        mean: 109,
        deadline: 102,
        confidence: 61,
        driver: "Trade stacking",
        executiveBrief:
          "Acceleration depends on stacking subcontractor work and tighter material timing, which pushes the project into a visibly riskier posture.",
        summary:
          "Use this scenario to explain the tradeoff between an earlier target and a much weaker certainty profile.",
        distribution: [10, 14, 20, 25, 34, 43, 55, 66, 77, 85, 88, 83, 72, 56, 36, 20],
        p50Index: 8,
        p80Index: 12,
        deadlineIndex: 7,
        tasks: [
          { name: "Trade stacking", owner: "Site lead", duration: "9d", risk: "High", critical: "Critical path" },
          { name: "Material procurement", owner: "Procurement", duration: "16d", risk: "High", critical: "Critical path" },
          { name: "Inspection compression", owner: "PM", duration: "4d", risk: "High", critical: "Near-critical" },
          { name: "Client handover prep", owner: "Client rep", duration: "4d", risk: "Medium", critical: "Protected" }
        ],
        signalItems: [
          { title: "Trade stacking", body: "Main execution risk because concurrent work increases rework probability.", risk: "High", owner: "Site lead" },
          { title: "Inspection compression", body: "Compressed approvals reduce slack and recovery options.", risk: "High", owner: "PM" },
          { title: "Material procurement", body: "Supplier drift becomes more punishing under acceleration.", risk: "High", owner: "Procurement" },
          { title: "Client handover prep", body: "Less risk than operations, but the narrative becomes harder to defend.", risk: "Medium", owner: "Client rep" }
        ],
        scenarioRows: [
          { label: "Scope stability", kpi: "Medium", metric: "Execution strain", tone: "Medium" },
          { label: "Commitment confidence", kpi: "61%", metric: "Low", tone: "High" },
          { label: "Mitigation urgency", kpi: "Immediate", metric: "Tradeoffs rising", tone: "High" }
        ],
        feed: [
          { time: "Now", title: "Client caution", body: "Explain that acceleration increases rework and coordination risk." },
          { time: "Next 24h", title: "Site decision", body: "Only accelerate if the client values speed over certainty." },
          { time: "Before handover", title: "Fallback plan", body: "Keep schedule contingency and staged handover options ready." }
        ]
      }
    }
  }
};

const state = {
  sampleId: "beta_release",
  scenarioId: "baseline",
  liveStory: false
};

const sampleSelect = document.querySelector("#sample-select");
const briefInput = document.querySelector("#brief-input");
const generateButton = document.querySelector("#generate-button");
const shuffleButton = document.querySelector("#shuffle-button");
const modeToggle = document.querySelector("#mode-toggle");
const modePill = document.querySelector("#mode-pill");
const generationStatus = document.querySelector("#generation-status");
const selectedMotion = document.querySelector("#selected-motion");
const riskChip = document.querySelector("#risk-chip");
const delayProb = document.querySelector("#delay-prob");
const p80Value = document.querySelector("#p80-value");
const confidenceValue = document.querySelector("#confidence-value");
const driverValue = document.querySelector("#driver-value");
const executiveBriefCopy = document.querySelector("#executive-brief-copy");
const meanValue = document.querySelector("#mean-value");
const p50Value = document.querySelector("#p50-value");
const p80Ribbon = document.querySelector("#p80-ribbon");
const deadlineValue = document.querySelector("#deadline-value");
const distributionBars = document.querySelector("#distribution-bars");
const criticalTaskList = document.querySelector("#critical-task-list");
const scenarioButtons = Array.from(document.querySelectorAll(".scenario-button"));
const scenarioTitle = document.querySelector("#scenario-title");
const scenarioSummaryCopy = document.querySelector("#scenario-summary-copy");
const scenarioTable = document.querySelector("#scenario-table");
const signalGrid = document.querySelector("#signal-grid");
const decisionFeed = document.querySelector("#decision-feed");

function getActiveScenario() {
  return demoLibrary[state.sampleId].scenarios[state.scenarioId];
}

function renderSampleOptions() {
  sampleSelect.innerHTML = Object.entries(demoLibrary)
    .map(
      ([id, item]) =>
        `<option value="${id}" ${id === state.sampleId ? "selected" : ""}>${item.label}</option>`
    )
    .join("");
}

function riskToneClass(value) {
  if (value === "High") return "risk-high";
  if (value === "Medium") return "risk-medium";
  return "risk-low";
}

function renderDistribution(activeScenario) {
  distributionBars.innerHTML = activeScenario.distribution
    .map((point, index) => {
      const classes = ["distribution-bar"];
      if (index === activeScenario.p50Index) classes.push("anchor-p50");
      if (index === activeScenario.p80Index) classes.push("anchor-p80");
      if (index === activeScenario.deadlineIndex) classes.push("anchor-deadline");

      return `<div class="${classes.join(" ")}" style="height:${Math.max(point, 10)}%"></div>`;
    })
    .join("");
}

function renderTasks(activeScenario) {
  criticalTaskList.innerHTML = activeScenario.tasks
    .map(
      (task) => `
        <div class="task-row">
          <div>
            <div class="task-name">${task.name}</div>
            <div class="task-meta">${task.owner}</div>
          </div>
          <span class="task-meta">${task.duration}</span>
          <span class="task-badge ${riskToneClass(task.risk)}">${task.risk}</span>
          <span class="task-meta">${task.critical}</span>
        </div>
      `
    )
    .join("");
}

function renderScenarioTable(activeScenario) {
  scenarioTable.innerHTML = activeScenario.scenarioRows
    .map(
      (row) => `
        <div class="scenario-row">
          <div>
            <strong>${row.label}</strong>
            <div class="task-meta">${row.metric}</div>
          </div>
          <span class="scenario-kpi ${riskToneClass(row.tone)}">${row.kpi}</span>
          <span class="task-meta">${row.metric}</span>
          <span class="task-meta">${row.tone === "High" ? "Escalation" : row.tone === "Medium" ? "Manage closely" : "Healthy"}</span>
        </div>
      `
    )
    .join("");
}

function renderSignalGrid(activeScenario) {
  signalGrid.innerHTML = activeScenario.signalItems
    .map(
      (item) => `
        <div class="signal-item">
          <h4>${item.title}</h4>
          <p>${item.body}</p>
          <div class="signal-meta">
            <span>${item.owner}</span>
            <span class="signal-badge ${riskToneClass(item.risk)}">${item.risk}</span>
          </div>
        </div>
      `
    )
    .join("");
}

function renderFeed(activeScenario) {
  decisionFeed.innerHTML = activeScenario.feed
    .map(
      (item) => `
        <div class="feed-item">
          <span class="feed-time">${item.time}</span>
          <h4>${item.title}</h4>
          <p>${item.body}</p>
        </div>
      `
    )
    .join("");
}

function renderScenarioButtons() {
  scenarioButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.scenario === state.scenarioId);
  });
}

function renderScene() {
  const sample = demoLibrary[state.sampleId];
  const activeScenario = getActiveScenario();

  briefInput.value = sample.brief;
  generationStatus.textContent = state.liveStory
    ? "Live story mode enabled"
    : "Ready to simulate";
  selectedMotion.textContent = activeScenario.label;
  modePill.textContent = state.liveStory ? "Live narrative mode" : "Mock advisory mode";

  riskChip.textContent = activeScenario.riskLabel;
  delayProb.textContent = `${activeScenario.delayProb}%`;
  p80Value.textContent = `${activeScenario.p80} days`;
  confidenceValue.textContent = `${activeScenario.confidence}%`;
  driverValue.textContent = activeScenario.driver;
  executiveBriefCopy.textContent = activeScenario.executiveBrief;
  meanValue.textContent = `${activeScenario.mean}d`;
  p50Value.textContent = `${activeScenario.p50}d`;
  p80Ribbon.textContent = `${activeScenario.p80}d`;
  deadlineValue.textContent = `${activeScenario.deadline}d`;
  scenarioTitle.textContent = activeScenario.label;
  scenarioSummaryCopy.textContent = activeScenario.summary;

  renderDistribution(activeScenario);
  renderTasks(activeScenario);
  renderScenarioTable(activeScenario);
  renderSignalGrid(activeScenario);
  renderFeed(activeScenario);
  renderScenarioButtons();
}

function switchSample(nextSampleId) {
  state.sampleId = nextSampleId;
  state.scenarioId = "baseline";
  renderScene();
}

function cycleSample() {
  const sampleIds = Object.keys(demoLibrary);
  const currentIndex = sampleIds.indexOf(state.sampleId);
  const nextIndex = (currentIndex + 1) % sampleIds.length;
  sampleSelect.value = sampleIds[nextIndex];
  switchSample(sampleIds[nextIndex]);
}

sampleSelect.addEventListener("change", (event) => {
  switchSample(event.target.value);
});

shuffleButton.addEventListener("click", cycleSample);

generateButton.addEventListener("click", () => {
  generationStatus.textContent = "Generating AI plan, simulation, and scenario story...";
  generateButton.disabled = true;

  window.setTimeout(() => {
    generationStatus.textContent = state.liveStory
      ? "Live story refreshed from selected brief"
      : "Forecast story regenerated from mock engine";
    renderScene();
    generateButton.disabled = false;
  }, 720);
});

scenarioButtons.forEach((button) => {
  button.addEventListener("click", () => {
    state.scenarioId = button.dataset.scenario;
    renderScene();
  });
});

modeToggle.addEventListener("click", () => {
  state.liveStory = !state.liveStory;
  modeToggle.textContent = state.liveStory ? "Switch to mock advisory" : "Switch to live story";
  renderScene();
});

renderSampleOptions();
renderScene();
