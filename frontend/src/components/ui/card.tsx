import { cn } from "@/lib/utils";
import { HTMLAttributes } from "react";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-2xl border border-white/10 bg-[#111622]/80 p-4 shadow-[0_20px_40px_-28px_rgba(0,0,0,0.7)] backdrop-blur",
        className,
      )}
      {...props}
    />
  );
}
