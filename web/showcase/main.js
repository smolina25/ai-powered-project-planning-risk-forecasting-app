const config = window.CERTAIN_PI_CONFIG;

document.title = `${config.brand} | ${config.appTitle}`;
document.querySelectorAll("[data-brand]").forEach((node) => {
  node.textContent = config.brand;
});
document.querySelectorAll("[data-app-title]").forEach((node) => {
  node.textContent = config.appTitle;
});

const repoLink = document.getElementById("repo-link");
const repoLinkSecondary = document.getElementById("repo-link-secondary");
const deckLink = document.getElementById("deck-link");
const evidenceLink = document.getElementById("evidence-link");
const demoLink = document.getElementById("demo-link");
const demoStatus = document.getElementById("demo-status");

repoLink.href = config.repoUrl;
repoLinkSecondary.href = config.repoUrl;
deckLink.href = config.deckUrl;
evidenceLink.href = config.evidenceUrl;

if (config.demoUrl && config.demoUrl.trim()) {
  demoLink.href = config.demoUrl;
  demoLink.textContent = "Launch Live Demo";
  demoStatus.textContent = "Live demo URL connected.";
} else {
  demoLink.href = config.deploymentGuideUrl;
  demoLink.textContent = "View Demo Launch Guide";
  demoStatus.textContent =
    "Live deployment URL not set yet. Update web/showcase/config.js after Streamlit deployment.";
}

document.getElementById("year").textContent = new Date().getFullYear();
