import { PropsWithChildren } from "react";

export default function MarketingLayout({ children }: PropsWithChildren) {
  return (
    <div className="relative min-h-screen overflow-x-hidden bg-background text-foreground">
      <div className="marketing-bg-base pointer-events-none absolute inset-0" />
      <div className="marketing-bg-glow pointer-events-none absolute inset-0" />
      <div className="marketing-bg-network pointer-events-none absolute inset-0" />
      <div className="marketing-bg-particles pointer-events-none absolute inset-0" />
      <div className="relative z-10">{children}</div>
    </div>
  );
}
