import Link from "next/link";
import { notFound } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { StatCard } from "@/components/stat-card";
import { formatCurrency, formatPercent } from "@/lib/format";
import { cn } from "@/lib/utils";
import { ArrowLeft } from "lucide-react";

export default async function ComparisonPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  let simulation;
  try {
    simulation = await api.getSimulation(id);
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) notFound();
    throw err;
  }

  const { best_scenario: best, baseline_scenario: baseline, comparison } = simulation;
  const totalSavings = baseline.total_cost - best.total_cost;
  const savingsPct = baseline.total_cost ? (totalSavings / baseline.total_cost) * 100 : 0;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Current vs AI Comparison</h1>
          <p className="text-sm text-muted-foreground">
            Current = a generic, non-optimized packaging choice. AI = the recommended scenario.
          </p>
        </div>
        <Button asChild variant="outline">
          <Link href={`/simulations/${id}`}>
            <ArrowLeft className="h-4 w-4" /> Back to Results
          </Link>
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard label="Total savings" value={formatCurrency(totalSavings)} />
        <StatCard
          label="Savings percentage"
          value={formatPercent(savingsPct)}
          delta={{ value: formatPercent(savingsPct), direction: "up", good: savingsPct >= 0 }}
        />
        <StatCard label="Baseline total cost" value={formatCurrency(baseline.total_cost)} hint="Current, non-optimized cost" />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Parameter Comparison</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Parameter</TableHead>
                <TableHead>Current</TableHead>
                <TableHead>AI</TableHead>
                <TableHead>Improvement</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {comparison.map((row) => (
                <TableRow key={row.parameter}>
                  <TableCell className="font-medium">{row.parameter}</TableCell>
                  <TableCell>{row.current}</TableCell>
                  <TableCell>{row.ai}</TableCell>
                  <TableCell>
                    {row.improvement_pct === null ? (
                      <span className="text-muted-foreground">&mdash;</span>
                    ) : (
                      <span
                        className={cn(
                          "font-medium",
                          row.improvement_pct >= 0 ? "text-status-good" : "text-status-critical"
                        )}
                      >
                        {row.improvement_pct >= 0 ? "+" : ""}
                        {formatPercent(row.improvement_pct)}
                      </span>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
