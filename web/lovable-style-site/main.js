const canvas = document.querySelector("#starfield");
const page = document.body.dataset.page || "home";

const navItems = [
  { id: "home", label: "Home", href: "index.html" },
  { id: "product", label: "Product", href: "product.html" },
  { id: "forecasting", label: "AI Forecasting", href: "ai-forecasting.html" },
  { id: "monte-carlo", label: "Monte Carlo", href: "monte-carlo.html" },
  { id: "pricing", label: "Pricing", href: "pricing.html" },
  { id: "dashboard", label: "Dashboard", href: "dashboard.html" },
  { id: "about", label: "About Us", href: "about.html" }
];

function buildHeader() {
  const headerHost = document.querySelector(".js-site-header");
  if (!headerHost) return;

  const navMarkup = navItems
    .map(
      (item) =>
        `<a href="${item.href}" class="nav-link ${item.id === page ? "active" : ""}">${item.label}</a>`
    )
    .join("");

  headerHost.innerHTML = `
    <header class="site-header">
      <a class="brand" href="index.html" aria-label="certAIn home">
        <div class="brand-mark" aria-hidden="true">
          <span class="brand-triangle"></span>
          <span class="brand-core">A</span>
        </div>
        <span class="brand-word">certAIn</span>
      </a>

      <button class="menu-toggle" id="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav">
        <span></span>
        <span></span>
        <span></span>
      </button>

      <nav class="site-nav" id="site-nav">${navMarkup}</nav>

      <div class="header-actions">
        <a href="login.html" class="text-link">Login</a>
        <a href="dashboard.html" class="button button-primary">Start Free Trial</a>
      </div>
    </header>
  `;
}

function buildFooter() {
  const footerHost = document.querySelector(".js-site-footer");
  if (!footerHost) return;

  footerHost.innerHTML = `
    <footer class="site-footer">
      <div class="footer-brand">
        <a class="brand" href="index.html">
          <div class="brand-mark small" aria-hidden="true">
            <span class="brand-triangle"></span>
            <span class="brand-core">A</span>
          </div>
          <span class="brand-word">certAIn</span>
        </a>
        <p>
          AI-powered forecasting using Monte Carlo simulation, dependency analysis,
          and stakeholder-ready decision support.
        </p>
      </div>

      <div class="footer-columns">
        <div>
          <h3>Product</h3>
          <a href="product.html">Features</a>
          <a href="ai-forecasting.html">AI Forecasting</a>
          <a href="monte-carlo.html">Monte Carlo</a>
          <a href="dashboard.html">Dashboard</a>
        </div>
        <div>
          <h3>Company</h3>
          <a href="about.html">About Us</a>
          <a href="pricing.html">Pricing</a>
          <a href="login.html">Login</a>
        </div>
        <div>
          <h3>Resources</h3>
          <a href="index.html">Overview</a>
          <a href="product.html">Product Tour</a>
          <a href="dashboard.html">Forecast Console</a>
          <a href="about.html">Project Story</a>
        </div>
        <div>
          <h3>Legal</h3>
          <span class="footer-badge">Capstone project</span>
          <span class="footer-badge">Presentation-ready</span>
          <span class="footer-badge">Portfolio-ready</span>
        </div>
      </div>

      <div class="footer-bottom">
        <span>© 2026 certAIn. All rights reserved.</span>
        <div class="footer-meta">
          <span>AI Planning</span>
          <span>Risk Forecasting</span>
          <span>Monte Carlo</span>
        </div>
      </div>
    </footer>
  `;
}

function setupMenu() {
  const menuToggle = document.querySelector("#menu-toggle");
  const siteNav = document.querySelector("#site-nav");
  const headerActions = document.querySelector(".header-actions");
  if (!menuToggle || !siteNav || !headerActions) return;

  menuToggle.addEventListener("click", () => {
    const expanded = menuToggle.getAttribute("aria-expanded") === "true";
    menuToggle.setAttribute("aria-expanded", String(!expanded));
    siteNav.classList.toggle("open");
    headerActions.classList.toggle("open");
  });
}

function drawStarfield() {
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  const ratio = window.devicePixelRatio || 1;
  const width = window.innerWidth;
  const height = window.innerHeight;

  canvas.width = Math.floor(width * ratio);
  canvas.height = Math.floor(height * ratio);
  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  ctx.clearRect(0, 0, width, height);

  const stars = Array.from(
    { length: Math.max(90, Math.floor((width * height) / 18000)) },
    () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      r: Math.random() * 1.6 + 0.25,
      a: Math.random() * 0.65 + 0.15
    })
  );

  for (const star of stars) {
    ctx.beginPath();
    ctx.fillStyle = `rgba(196, 221, 255, ${star.a})`;
    ctx.arc(star.x, star.y, star.r, 0, Math.PI * 2);
    ctx.fill();
  }

  for (let i = 0; i < 6; i += 1) {
    const x = Math.random() * width;
    const y = Math.random() * height;
    const radius = Math.random() * 1.8 + 0.8;
    const glow = ctx.createRadialGradient(x, y, 0, x, y, radius * 16);
    glow.addColorStop(0, "rgba(91,157,255,0.18)");
    glow.addColorStop(1, "rgba(91,157,255,0)");
    ctx.beginPath();
    ctx.fillStyle = glow;
    ctx.arc(x, y, radius * 16, 0, Math.PI * 2);
    ctx.fill();
  }
}

function wireMockLogin() {
  const loginForm = document.querySelector(".login-form");
  if (!loginForm) return;

  loginForm.addEventListener("submit", (event) => {
    event.preventDefault();
    window.location.href = "dashboard.html";
  });
}

buildHeader();
buildFooter();
setupMenu();
wireMockLogin();
window.addEventListener("resize", drawStarfield);
drawStarfield();
