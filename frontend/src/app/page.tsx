import Link from "next/link";
import { api, ApiError } from "@/lib/api";
import { StatCard } from "@/components/stat-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { formatCurrency, formatDate, formatPercent } from "@/lib/format";
import { PlusCircle } from "lucide-react";

export default async function DashboardPage() {
  let summary;
  let error: string | null = null;
  try {
    summary = await api.dashboardSummary();
  } catch (err) {
    error = err instanceof ApiError ? err.message : "Could not reach the API.";
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
          <p className="text-sm text-muted-foreground">
            Overview of every optimization run and how much they saved versus current practice.
          </p>
        </div>
        <Button asChild>
          <Link href="/simulations/new">
            <PlusCircle className="h-4 w-4" />
            New Simulation
          </Link>
        </Button>
      </div>

      {error && (
        <Card className="border-status-critical/40">
          <CardContent className="py-4 text-sm text-status-critical">
            {error} Make sure the backend API is running (see README setup instructions).
          </CardContent>
        </Card>
      )}

      {summary && (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <StatCard label="Total simulations" value={summary.total_simulations.toString()} />
            <StatCard
              label="Total savings"
              value={formatCurrency(summary.total_savings)}
              hint="Sum of AI vs. current cost savings across all runs"
            />
            <StatCard
              label="Average container utilization"
              value={formatPercent(summary.average_container_utilization * 100)}
              hint="Mean utilization of the AI-recommended container"
            />
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Recent simulations</CardTitle>
            </CardHeader>
            <CardContent>
              {summary.recent_simulations.length === 0 ? (
                <p className="py-8 text-center text-sm text-muted-foreground">
                  No simulations yet.{" "}
                  <Link href="/simulations/new" className="font-medium text-foreground underline underline-offset-4">
                    Run your first optimization
                  </Link>
                  .
                </p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date</TableHead>
                      <TableHead>Package weight</TableHead>
                      <TableHead>Shipment quantity</TableHead>
                      <TableHead>Total cost (AI)</TableHead>
                      <TableHead>Savings</TableHead>
                      <TableHead>Utilization</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {summary.recent_simulations.map((sim) => (
                      <TableRow key={sim.id} className="cursor-pointer">
                        <TableCell>
                          <Link href={`/simulations/${sim.id}`} className="block">
                            {formatDate(sim.created_at)}
                          </Link>
                        </TableCell>
                        <TableCell>{sim.package_weight_g} g</TableCell>
                        <TableCell>{sim.shipment_quantity}</TableCell>
                        <TableCell>{formatCurrency(sim.total_cost_ai)}</TableCell>
                        <TableCell className="text-status-good">
                          {formatPercent(sim.savings_pct)}
                        </TableCell>
                        <TableCell>{formatPercent(sim.container_utilization_ai * 100)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
