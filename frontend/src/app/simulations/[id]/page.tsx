import Link from "next/link";
import { notFound } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { formatCurrency, formatDate, formatDims, formatNumber, formatPercent } from "@/lib/format";
import { ArrowRight } from "lucide-react";

export default async function ResultsPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  let simulation;
  try {
    simulation = await api.getSimulation(id);
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) notFound();
    throw err;
  }

  const { best_scenario: best, alternative_scenarios: alternatives, inputs } = simulation;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Optimization Results</h1>
          <p className="text-sm text-muted-foreground">
            Run on {formatDate(simulation.created_at)} &middot; {inputs.tea_density_g_cm3} g/cm3 tea &middot;{" "}
            {inputs.package_weight_g} g packages
          </p>
        </div>
        <Button asChild variant="outline">
          <Link href={`/simulations/${id}/comparison`}>
            Current vs AI Comparison <ArrowRight className="h-4 w-4" />
          </Link>
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="flex flex-col gap-1 py-2">
            <span className="text-sm text-muted-foreground">Total cost</span>
            <span className="text-2xl font-semibold tabular-nums">{formatCurrency(best.total_cost)}</span>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex flex-col gap-1 py-2">
            <span className="text-sm text-muted-foreground">Container utilization</span>
            <span className="text-2xl font-semibold tabular-nums">
              {formatPercent(best.container.best.utilization * 100)}
            </span>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex flex-col gap-1 py-2">
            <span className="text-sm text-muted-foreground">Total units required</span>
            <span className="text-2xl font-semibold tabular-nums">
              {formatNumber(simulation.total_units_required)}
            </span>
          </CardContent>
        </Card>
      </div>

      {/* Module 3 - Package Recommendation */}
      <Card>
        <CardHeader>
          <CardTitle>Package Recommendation</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <div className="flex flex-wrap items-center gap-3">
            <Badge>{best.package.shape}</Badge>
            <span className="font-medium">
              {formatDims(best.package.length_mm, best.package.width_mm, best.package.height_mm)}
            </span>
            <Badge variant="secondary">Fill ratio {formatPercent(best.package.fill_ratio * 100)}</Badge>
            <Badge variant="secondary">{formatCurrency(best.package.estimated_cost)} / unit</Badge>
          </div>
          <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm sm:grid-cols-4">
            <Stat label="Product volume" value={`${best.package.product_volume_cm3.toFixed(1)} cm3`} />
            <Stat label="Package volume" value={`${best.package.package_volume_cm3.toFixed(1)} cm3`} />
            <Stat label="Material usage" value={`${best.package.material_usage_g.toFixed(2)} g`} />
            <Stat label="Surface area" value={`${(best.package.surface_area_m2 * 10000).toFixed(1)} cm2`} />
          </div>

          {alternatives.length > 0 && (
            <div>
              <p className="mb-2 text-sm font-medium text-muted-foreground">Alternative package options</p>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Dimensions</TableHead>
                    <TableHead>Fill ratio</TableHead>
                    <TableHead>Est. cost</TableHead>
                    <TableHead>Scenario total cost</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {alternatives.map((alt, i) => (
                    <TableRow key={i}>
                      <TableCell className="capitalize">{alt.package.name.replaceAll("_", " ")}</TableCell>
                      <TableCell>{formatDims(alt.package.length_mm, alt.package.width_mm, alt.package.height_mm)}</TableCell>
                      <TableCell>{formatPercent(alt.package.fill_ratio * 100)}</TableCell>
                      <TableCell>{formatCurrency(alt.package.estimated_cost)}</TableCell>
                      <TableCell>{formatCurrency(alt.total_cost)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Module 4 - Carton Optimization */}
      <Card>
        <CardHeader>
          <CardTitle>Carton Optimization</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-x-6 gap-y-3 sm:grid-cols-4">
          <Stat label="Carton dimensions" value={formatDims(best.carton.length_mm, best.carton.width_mm, best.carton.height_mm)} />
          <Stat label="Units per carton" value={formatNumber(best.carton.units_per_carton)} />
          <Stat label="Carton weight" value={`${best.carton.carton_weight_kg.toFixed(2)} kg`} />
          <Stat label="Board grade" value={best.carton.board_grade} />
        </CardContent>
      </Card>

      {/* Module 5 - Pallet Optimization */}
      <Card>
        <CardHeader>
          <CardTitle>Pallet Optimization</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-x-6 gap-y-3 sm:grid-cols-4">
          <Stat label="Cartons per layer" value={formatNumber(best.pallet.cartons_per_layer)} />
          <Stat label="Layers" value={formatNumber(best.pallet.layers)} />
          <Stat label="Cartons per pallet" value={formatNumber(best.pallet.cartons_per_pallet)} />
          <Stat label="Pallet height" value={`${best.pallet.pallet_height_mm.toFixed(0)} mm`} />
          <Stat label="Total weight" value={`${best.pallet.total_weight_kg.toFixed(1)} kg`} />
        </CardContent>
      </Card>

      {/* Module 6 - Container Optimization */}
      <Card>
        <CardHeader>
          <CardTitle>Container Optimization</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Container</TableHead>
                <TableHead>Pallets/container</TableHead>
                <TableHead>Cartons/container</TableHead>
                <TableHead>Utilization</TableHead>
                <TableHead>Empty space</TableHead>
                <TableHead>Containers required</TableHead>
                <TableHead>Freight cost</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {[best.container.best, ...best.container.alternatives]
                .sort((a, b) => (a.container_type < b.container_type ? -1 : 1))
                .map((c) => (
                  <TableRow key={c.container_type} className={c.container_type === best.container.best.container_type ? "bg-secondary/50" : ""}>
                    <TableCell className="font-medium">
                      {c.container_type}
                      {c.container_type === best.container.best.container_type && (
                        <Badge className="ml-2" variant="default">
                          Recommended
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>{formatNumber(c.pallets_per_container)}</TableCell>
                    <TableCell>{formatNumber(c.cartons_per_container)}</TableCell>
                    <TableCell>{formatPercent(c.utilization * 100)}</TableCell>
                    <TableCell>{formatPercent(c.empty_space * 100)}</TableCell>
                    <TableCell>{formatNumber(c.containers_required)}</TableCell>
                    <TableCell>{formatCurrency(c.freight_cost)}</TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Cost Summary</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-3 gap-4">
          <Stat label="Packaging cost" value={formatCurrency(best.packaging_cost_total)} />
          <Stat label="Freight cost" value={formatCurrency(best.freight_cost_total)} />
          <Stat label="Total cost" value={formatCurrency(best.total_cost)} />
        </CardContent>
      </Card>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}
