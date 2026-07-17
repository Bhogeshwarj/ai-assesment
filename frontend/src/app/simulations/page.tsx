import Link from "next/link";
import { api, ApiError } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { formatCurrency, formatDate, formatPercent } from "@/lib/format";

export default async function HistoryPage() {
  let simulations;
  let error: string | null = null;
  try {
    simulations = await api.listSimulations();
  } catch (err) {
    error = err instanceof ApiError ? err.message : "Could not reach the API.";
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">History</h1>
        <p className="text-sm text-muted-foreground">All past optimization runs, most recent first.</p>
      </div>

      {error && (
        <Card className="border-status-critical/40">
          <CardContent className="py-4 text-sm text-status-critical">{error}</CardContent>
        </Card>
      )}

      {simulations && (
        <Card>
          <CardContent>
            {simulations.length === 0 ? (
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
                    <TableHead>Tea density</TableHead>
                    <TableHead>Package weight</TableHead>
                    <TableHead>Shipment quantity</TableHead>
                    <TableHead>Total cost (AI)</TableHead>
                    <TableHead>Savings</TableHead>
                    <TableHead>Utilization</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {simulations.map((sim) => (
                    <TableRow key={sim.id}>
                      <TableCell>
                        <Link href={`/simulations/${sim.id}`} className="block hover:underline">
                          {formatDate(sim.created_at)}
                        </Link>
                      </TableCell>
                      <TableCell>{sim.tea_density_g_cm3} g/cm3</TableCell>
                      <TableCell>{sim.package_weight_g} g</TableCell>
                      <TableCell>{sim.shipment_quantity}</TableCell>
                      <TableCell>{formatCurrency(sim.total_cost_ai)}</TableCell>
                      <TableCell className="text-status-good">{formatPercent(sim.savings_pct)}</TableCell>
                      <TableCell>{formatPercent(sim.container_utilization_ai * 100)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
