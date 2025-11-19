import type { FC } from "react";
import { theme } from "../styles/theme";

interface HeaderProps {
  title: string;
  subtitle: string;
}

export const Header: FC<HeaderProps> = ({ title, subtitle }) => {
  return (
    <header
      className="rounded-[28px] border border-white/10 px-8 py-6 shadow-[0_12px_40px_rgba(0,0,0,0.2)] backdrop-blur-xl"
      style={{ background: theme.colors.headerGradient }}
    >
      <div className="flex items-center justify-between gap-6">
        <div>
          <p className="font-semibold uppercase tracking-[0.35em] text-white/70 text-xs sm:text-sm">
            Ask anything
          </p>
          <h1 className="mt-3 text-2xl sm:text-3xl md:text-4xl font-semibold text-white">
            {title}
          </h1>
          <p className="mt-2 text-sm sm:text-base text-white/70">{subtitle}</p>
        </div>
        <div className="hidden sm:flex h-16 w-16 flex-none items-center justify-center rounded-2xl border border-white/10 bg-white/10 text-white shadow-[0_12px_40px_rgba(56,189,248,0.35)]">
          <span className="text-lg font-semibold">AI</span>
        </div>
      </div>
    </header>
  );
};
