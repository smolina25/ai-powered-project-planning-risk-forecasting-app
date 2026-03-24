import {
  ReactNode,
  createContext,
  useContext,
  useMemo,
  useState,
} from "react";

type Locale = "en";

type Dictionary = {
  about: {
    heroTitlePrefix: string;
    heroTitleHighlight: string;
    heroTitleSuffix: string;
    heroSubtitle: string;
    mission: { title: string; description: string };
    vision: { title: string; description: string };
    valuesLabel: string;
    valuesTitle: string;
    journeyTitle: string;
    journeySubtitle: string;
    teamTitle: string;
    ctaTitle: string;
    ctaSubtitle: string;
    ctaButton: string;
  };
};

const dictionary: Record<Locale, Dictionary> = {
  en: {
    about: {
      heroTitlePrefix: "About cert",
      heroTitleHighlight: "AI",
      heroTitleSuffix: "n",
      heroSubtitle:
        "We're building the future of project intelligence — where AI helps teams deliver on time, every time.",
      mission: {
        title: "Our Mission",
        description:
          "To eliminate project failure by giving every team access to AI-powered forecasting and risk intelligence. We believe that project delays are predictable — and preventable — when teams have the right data at the right time.",
      },
      vision: {
        title: "Our Vision",
        description:
          "A world where every project plan comes with a probability of success. Where project managers can confidently tell stakeholders not just when a project will finish — but how certain they are about it.",
      },
      valuesLabel: "What Drives Us",
      valuesTitle: "Our Core Values",
      journeyTitle: "Our Journey",
      journeySubtitle: "From idea to industry-leading AI platform",
      teamTitle: "Leadership Team",
      ctaTitle: "Ready to Transform Your Projects?",
      ctaSubtitle:
        "Join 500+ enterprise teams already using certAIn to deliver projects with AI-powered certainty.",
      ctaButton: "Contact Sales",
    },
  },
};

type LanguageContextValue = {
  language: Locale;
  setLanguage: (next: Locale) => void;
  t: (key: string) => string;
};

const LanguageContext = createContext<LanguageContextValue | undefined>(undefined);

function getNestedValue(source: Dictionary, key: string): string {
  return key.split(".").reduce<unknown>((current, part) => {
    if (current && typeof current === "object" && part in current) {
      return (current as Record<string, unknown>)[part];
    }
    return key;
  }, source) as string;
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Locale>("en");

  const value = useMemo<LanguageContextValue>(
    () => ({
      language,
      setLanguage,
      t: (key) => getNestedValue(dictionary[language], key),
    }),
    [language],
  );

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within LanguageProvider");
  }
  return context;
}
