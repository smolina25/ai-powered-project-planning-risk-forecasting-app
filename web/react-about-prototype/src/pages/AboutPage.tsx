import { motion } from "framer-motion";
import {
  ArrowRight,
  Eye,
  Globe,
  Heart,
  Shield,
  Sparkles,
  Target,
  Users,
  Zap,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useMemo } from "react";
import certAInLogo from "../assets/logo.png";
import { useLanguage } from "../hooks/useLanguage";

const premiumEase = [0.22, 1, 0.36, 1] as const;

const fadeUp = {
  initial: { opacity: 0, y: 18 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true },
  transition: { duration: 0.48, ease: premiumEase },
};

function ensurePlainText(value: string): string {
  return value.replace(/<[^>]*>/g, "").trim();
}

type ValueItem = {
  icon: LucideIcon;
  title: string;
  description: string;
};

type Milestone = {
  year: string;
  title: string;
  description: string;
};

type TeamMember = {
  name: string;
  role: string;
  bio: string;
  imageSrc: string;
};

type TimelineCardAlign = "left" | "right" | "mobile";

function renderBrandAccent(text: string) {
  const parts = text.split("certAIn");

  if (parts.length === 1) {
    return text;
  }

  return parts.flatMap((part, index) =>
    index < parts.length - 1
      ? [part, <span key={`brand-${index}`}>cert<span className="text-ai-gradient font-extrabold">AI</span>n</span>]
      : [part],
  );
}

function TeamAvatar({ src, alt }: { src: string; alt: string }) {
  return (
    <div className="avatar-wrapper">
      <div className="avatar team-avatar">
        <img src={src} alt={alt} loading="lazy" decoding="async" />
      </div>
    </div>
  );
}

function TimelineMilestoneCard({
  milestone,
  align,
}: {
  milestone: Milestone;
  align: TimelineCardAlign;
}) {
  const isLeft = align === "left";

  return (
    <article
      className={[
        "about-timeline-card",
        align === "mobile" ? "about-timeline-card-mobile" : "",
        isLeft ? "about-timeline-card-left" : "about-timeline-card-right",
      ]
        .filter(Boolean)
        .join(" ")}
    >
      <span className="about-timeline-year">{milestone.year}</span>
      <h3 className="about-timeline-title">{milestone.title}</h3>
      <p className="about-timeline-description">{milestone.description}</p>
    </article>
  );
}

function HeroSection({
  titlePrefix,
  titleHighlight,
  titleSuffix,
  subtitle,
}: {
  titlePrefix: string;
  titleHighlight: string;
  titleSuffix: string;
  subtitle: string;
}) {
  return (
    <motion.section {...fadeUp} className="about-hero">
      <div className="about-hero-logo-shell">
        <img
          src={certAInLogo}
          alt="certAIn logo"
          className="about-hero-logo logo-ai-glow"
        />
      </div>
      <h1 className="about-hero-title">
        {titlePrefix}
        <span className="text-ai-gradient font-extrabold">
          {titleHighlight}
        </span>
        {titleSuffix}
      </h1>
      <p className="about-hero-subtitle">{subtitle}</p>
    </motion.section>
  );
}

function MissionVisionSection({
  missionTitle,
  missionDescription,
  visionTitle,
  visionDescription,
}: {
  missionTitle: string;
  missionDescription: string;
  visionTitle: string;
  visionDescription: string;
}) {
  return (
    <section className="about-two-up">
      <motion.article
        initial={{ opacity: 0, x: -24 }}
        whileInView={{ opacity: 1, x: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5, ease: premiumEase }}
        className="about-mv-card"
      >
        <div className="icon-ai mb-5">
          <Target className="h-6 w-6" />
        </div>
        <h2 className="mb-4 font-display text-[1.85rem] font-semibold tracking-tight text-foreground">
          {missionTitle}
        </h2>
        <p className="text-[1.02rem] leading-7 text-muted">{missionDescription}</p>
      </motion.article>

      <motion.article
        initial={{ opacity: 0, x: 24 }}
        whileInView={{ opacity: 1, x: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5, ease: premiumEase }}
        className="about-mv-card"
      >
        <div className="icon-ai mb-5">
          <Eye className="h-6 w-6" />
        </div>
        <h2 className="mb-4 font-display text-[1.85rem] font-semibold tracking-tight text-foreground">
          {visionTitle}
        </h2>
        <p className="text-[1.02rem] leading-7 text-muted">{visionDescription}</p>
      </motion.article>
    </section>
  );
}

function CoreValuesSection({
  label,
  title,
  values,
}: {
  label: string;
  title: string;
  values: ValueItem[];
}) {
  return (
    <section className="space-y-6">
      <motion.div {...fadeUp} className="about-section-intro">
        <div className="about-pill">
          <Sparkles className="h-4 w-4" />
          <span>{label}</span>
        </div>
        <h2 className="about-section-title">{title}</h2>
      </motion.div>

      <div className="about-values-grid">
        {values.map((value, index) => {
          const Icon = value.icon;

          return (
            <motion.article
              key={value.title}
              initial={{ opacity: 0, y: 18 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.48, ease: premiumEase, delay: index * 0.08 }}
              className="about-value-card-premium"
            >
              <div className="icon-ai mx-auto mb-5">
                <Icon className="h-6 w-6" />
              </div>
              <h3 className="mb-2.5 font-display text-[1.4rem] font-semibold tracking-tight text-foreground">
                {value.title}
              </h3>
              <p className="text-[0.98rem] leading-6 text-muted">{value.description}</p>
            </motion.article>
          );
        })}
      </div>
    </section>
  );
}

function JourneySection({
  title,
  subtitle,
  milestones,
}: {
  title: string;
  subtitle: string;
  milestones: Milestone[];
}) {
  return (
    <section className="space-y-6">
      <motion.div {...fadeUp} className="about-section-intro">
        <h2 className="about-section-title">{title}</h2>
        <p className="about-section-subtitle">{subtitle}</p>
      </motion.div>

      <div className="about-timeline">
        <div className="about-timeline-spine" aria-hidden="true" />

        <div className="about-timeline-list">
          {milestones.map((milestone, index) => {
            const isLeft = index % 2 === 0;

            return (
              <motion.div
                key={`${milestone.year}-${milestone.title}`}
                initial={{ opacity: 0, y: 18 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.48, ease: premiumEase, delay: index * 0.06 }}
                className="about-timeline-row"
              >
                <div className="about-timeline-slot about-timeline-slot-left">
                  {isLeft ? <TimelineMilestoneCard milestone={milestone} align="left" /> : null}
                </div>

                <div className="about-timeline-center">
                  <span className="about-timeline-node" />
                </div>

                <div className="about-timeline-slot about-timeline-slot-right">
                  {!isLeft ? <TimelineMilestoneCard milestone={milestone} align="right" /> : null}
                </div>

                <div className="about-timeline-mobile">
                  <TimelineMilestoneCard milestone={milestone} align="mobile" />
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function TeamSection({
  title,
  teamMembers,
}: {
  title: string;
  teamMembers: TeamMember[];
}) {
  return (
    <section className="space-y-6">
      <motion.div {...fadeUp} className="flex items-center gap-3">
        <Users className="h-6 w-6 text-foreground" />
        <h2 className="about-section-title !mt-0 !text-left">{title}</h2>
      </motion.div>

      <div className="about-team-grid">
        {teamMembers.map((member, index) => (
          <motion.article
            key={member.name}
            initial={{ opacity: 0, y: 18 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.48, ease: premiumEase, delay: index * 0.08 }}
            className="about-team-card"
          >
            <TeamAvatar src={member.imageSrc} alt={`${member.name} portrait`} />
            <h3 className="text-ai-gradient font-display text-[1.4rem] font-semibold tracking-tight">
              {member.name}
            </h3>
            <p className="mt-2 text-sm font-semibold uppercase tracking-[0.12em] text-ai-gradient">
              {member.role}
            </p>
            <p className="mt-4 text-[0.98rem] leading-6 text-muted">{renderBrandAccent(member.bio)}</p>
          </motion.article>
        ))}
      </div>
    </section>
  );
}

function CtaSection({
  title,
  subtitle,
  buttonLabel,
}: {
  title: string;
  subtitle: string;
  buttonLabel: string;
}) {
  return (
    <motion.section {...fadeUp} className="about-cta-band">
      <div className="about-cta-inner">
        <h2 className="about-section-title !mt-0">{title}</h2>
        <p className="mt-4 text-base leading-7 text-muted sm:text-lg">{subtitle}</p>
        <div className="mt-7 flex justify-center">
          <a href="/contact" className="btn-ai about-cta-button inline-flex">
            <span>{buttonLabel}</span>
            <ArrowRight className="h-5 w-5" />
          </a>
        </div>
      </div>
    </motion.section>
  );
}

export default function AboutPage() {
  const { t } = useLanguage();

  const values = useMemo<ValueItem[]>(
    () => [
      {
        icon: Zap,
        title: ensurePlainText("Innovation First"),
        description: ensurePlainText("We push the boundaries of what AI can do for project management."),
      },
      {
        icon: Shield,
        title: ensurePlainText("Trust & Security"),
        description: ensurePlainText("Enterprise-grade security and compliance are non-negotiable."),
      },
      {
        icon: Heart,
        title: ensurePlainText("Customer Obsession"),
        description: ensurePlainText("Every feature is driven by real feedback from project teams."),
      },
      {
        icon: Globe,
        title: ensurePlainText("Global Perspective"),
        description: ensurePlainText("Built for teams of every size, across every continent."),
      },
    ],
    [],
  );

  const milestones = useMemo<Milestone[]>(
    () => [
      {
        year: ensurePlainText("2023"),
        title: ensurePlainText("Company Founded"),
        description: ensurePlainText("certAIn launched with a vision to bring AI certainty to project management."),
      },
      {
        year: ensurePlainText("2023"),
        title: ensurePlainText("Seed Funding"),
        description: ensurePlainText("Raised $4.2M seed round to build the core AI forecasting engine."),
      },
      {
        year: ensurePlainText("2024"),
        title: ensurePlainText("Product Launch"),
        description: ensurePlainText(
          "Launched Monte Carlo simulations & AI risk detection to first 100 enterprise clients.",
        ),
      },
      {
        year: ensurePlainText("2024"),
        title: ensurePlainText("SOC2 & GDPR Certified"),
        description: ensurePlainText("Achieved full compliance for enterprise-ready security."),
      },
      {
        year: ensurePlainText("2025"),
        title: ensurePlainText("Series A"),
        description: ensurePlainText("Raised $18M to expand globally and scale AI capabilities."),
      },
      {
        year: ensurePlainText("2025"),
        title: ensurePlainText("500+ Enterprise Teams"),
        description: ensurePlainText("Powering project forecasting for Fortune 500 companies worldwide."),
      },
    ],
    [],
  );

  const teamMembers = useMemo<TeamMember[]>(
    () => [
      {
        name: ensurePlainText("Meysameh Shojaei"),
        role: ensurePlainText("Founder & CEO"),
        bio: ensurePlainText(
          "AI Product Leader building data-driven decision systems for next-generation project planning. Leads product strategy and execution from concept to deployment. Originator of the certAIn vision, creating a scalable AI platform that redefines how teams plan, forecast risk, and make critical decisions.",
        ),
        imageSrc: "/leadership_images/CEO.jpeg",
      },
      {
        name: ensurePlainText("Santiago Molina"),
        role: ensurePlainText("COO"),
        bio: ensurePlainText(
          "Industrial Engineer and AI Project Leader driving end-to-end digital initiatives in international environments. Specializes in product development, workflow optimization, and operational efficiency using Agile methodologies. Experienced in large-scale transformation, including process redesign and cloud migration.",
        ),
        imageSrc: "/leadership_images/COO.jpg",
      },
      {
        name: ensurePlainText("James Park"),
        role: ensurePlainText("CTO"),
        bio: ensurePlainText(
          "Ex-Microsoft engineer building scalable ML infrastructure and high-performance systems. Expert in data pipelines, model deployment, and simulation systems for complex forecasting and decision-making applications.",
        ),
        imageSrc: "/leadership_images/CTO.jpg",
      },
      {
        name: ensurePlainText("Maria Smith"),
        role: ensurePlainText("CFO"),
        bio: ensurePlainText(
          "Former Deloitte Partner with 18+ years in corporate finance and scaling technology ventures. Specializes in financial strategy, fundraising, and operational efficiency across AI and SaaS organizations.",
        ),
        imageSrc: "/leadership_images/CFO.jpg",
      },
      {
        name: ensurePlainText("Lisa Schmidt"),
        role: ensurePlainText("Head of AI"),
        bio: ensurePlainText(
          "PhD in Operations Research leading advanced AI and predictive analytics initiatives. Expert in forecasting models, optimization, and building scalable data-driven systems for complex planning challenges.",
        ),
        imageSrc: "/leadership_images/Head%20AI.jpg",
      },
      {
        name: ensurePlainText("David Chen"),
        role: ensurePlainText("Head of Product"),
        bio: ensurePlainText(
          "Product leader with experience building project management tools at Atlassian and Asana. Focused on scalable, user-centric products that improve workflow efficiency and team collaboration.",
        ),
        imageSrc: "/leadership_images/Head%20Product.jpg",
      },
    ],
    [],
  );

  const aboutCopy = useMemo(
    () => ({
      heroTitlePrefix: ensurePlainText(t("about.heroTitlePrefix")),
      heroTitleHighlight: ensurePlainText(t("about.heroTitleHighlight")),
      heroTitleSuffix: ensurePlainText(t("about.heroTitleSuffix")),
      heroSubtitle: ensurePlainText(t("about.heroSubtitle")),
      missionTitle: ensurePlainText(t("about.mission.title")),
      missionDescription: ensurePlainText(t("about.mission.description")),
      visionTitle: ensurePlainText(t("about.vision.title")),
      visionDescription: ensurePlainText(t("about.vision.description")),
      valuesLabel: ensurePlainText(t("about.valuesLabel")),
      valuesTitle: ensurePlainText(t("about.valuesTitle")),
      journeyTitle: ensurePlainText(t("about.journeyTitle")),
      journeySubtitle: ensurePlainText(t("about.journeySubtitle")),
      teamTitle: ensurePlainText(t("about.teamTitle")),
      ctaTitle: ensurePlainText(t("about.ctaTitle")),
      ctaSubtitle: ensurePlainText(t("about.ctaSubtitle")),
      ctaButton: ensurePlainText(t("about.ctaButton")),
    }),
    [t],
  );

  return (
    <main className="about-shell">
      <HeroSection
        titlePrefix={aboutCopy.heroTitlePrefix}
        titleHighlight={aboutCopy.heroTitleHighlight}
        titleSuffix={aboutCopy.heroTitleSuffix}
        subtitle={aboutCopy.heroSubtitle}
      />
      <MissionVisionSection
        missionTitle={aboutCopy.missionTitle}
        missionDescription={aboutCopy.missionDescription}
        visionTitle={aboutCopy.visionTitle}
        visionDescription={aboutCopy.visionDescription}
      />
      <CoreValuesSection
        label={aboutCopy.valuesLabel}
        title={aboutCopy.valuesTitle}
        values={values}
      />
      <JourneySection
        title={aboutCopy.journeyTitle}
        subtitle={aboutCopy.journeySubtitle}
        milestones={milestones}
      />
      <TeamSection title={aboutCopy.teamTitle} teamMembers={teamMembers} />
      <CtaSection
        title={aboutCopy.ctaTitle}
        subtitle={aboutCopy.ctaSubtitle}
        buttonLabel={aboutCopy.ctaButton}
      />
    </main>
  );
}
