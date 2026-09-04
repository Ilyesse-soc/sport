import { cn } from "@/lib/utils";

type Props = {
  label: string;
  value: number;
  goal: number;
  unit?: string;
};

export function MetricProgress({ label, value, goal, unit = "" }: Props) {
  const ratio = goal > 0 ? Math.min(100, Math.round((value / goal) * 100)) : 0;
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm text-zinc-300">
        <span>{label}</span>
        <span>
          {Math.round(value)} / {goal}
          {unit}
        </span>
      </div>
      <div className="h-2 rounded-full bg-zinc-800">
        <div
          className={cn("h-2 rounded-full bg-gradient-to-r from-emerald-400 to-cyan-400")}
          style={{ width: `${ratio}%` }}
        />
      </div>
    </div>
  );
}
