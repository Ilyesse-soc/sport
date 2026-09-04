"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, Bot, ChartLine, Dumbbell, Home, Utensils } from "lucide-react";
import { cn } from "@/lib/utils";

const nav = [
  { href: "/", label: "Aujourd'hui", icon: Home },
  { href: "/nutrition", label: "Nutrition", icon: Utensils },
  { href: "/training", label: "Training", icon: Dumbbell },
  { href: "/progression", label: "Progression", icon: ChartLine },
  { href: "/coach", label: "Coach IA", icon: Bot },
  { href: "/recovery", label: "Recup", icon: Activity },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="mx-auto flex min-h-screen w-full max-w-7xl bg-transparent text-zinc-100">
      <aside className="hidden w-64 shrink-0 border-r border-white/10 p-6 lg:block">
        <div className="text-xl font-black tracking-tight text-cyan-300">SPORT COACH</div>
        <nav className="mt-6 space-y-2">
          {nav.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-xl px-3 py-2 text-sm transition",
                  active ? "bg-cyan-500/20 text-cyan-200" : "text-zinc-300 hover:bg-white/5",
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>

      <main className="flex-1 px-4 pb-24 pt-4 lg:px-8 lg:py-8">{children}</main>

      <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-white/10 bg-[#0a0f19]/95 p-2 backdrop-blur lg:hidden">
        <div className="mx-auto grid max-w-lg grid-cols-5 gap-1">
          {nav.slice(0, 5).map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex flex-col items-center gap-1 rounded-lg px-2 py-2 text-[11px]",
                  active ? "bg-cyan-500/20 text-cyan-200" : "text-zinc-400",
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </div>
      </nav>
    </div>
  );
}
