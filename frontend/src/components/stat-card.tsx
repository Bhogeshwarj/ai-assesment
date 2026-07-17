import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string;
  delta?: { value: string; direction: "up" | "down"; good: boolean };
  hint?: string;
}

export function StatCard({ label, value, delta, hint }: StatCardProps) {
  return (
    <Card>
      <CardContent className="flex flex-col gap-2 py-2">
        <span className="text-sm text-muted-foreground">{label}</span>
        <span className="text-3xl font-semibold tabular-nums">{value}</span>
        {delta && (
          <span
            className={cn(
              "flex items-center gap-1 text-sm font-medium",
              delta.good ? "text-status-good" : "text-status-critical"
            )}
          >
            {delta.direction === "up" ? (
              <ArrowUpRight className="h-4 w-4" />
            ) : (
              <ArrowDownRight className="h-4 w-4" />
            )}
            {delta.value}
          </span>
        )}
        {hint && <span className="text-xs text-muted-foreground">{hint}</span>}
      </CardContent>
    </Card>
  );
}
