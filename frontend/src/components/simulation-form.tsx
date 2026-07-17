"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import type { SimulationInput } from "@/types/simulation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Loader2 } from "lucide-react";

const PACKAGE_WEIGHT_OPTIONS_G = [50, 100, 125, 250, 500, 1000];

export function SimulationForm() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState<SimulationInput>({
    tea_density_g_cm3: 0.45,
    package_weight_g: 250,
    shipment_quantity: 20000,
    shipment_type: "total_weight",
    package_shape: "square",
    packaging_material: "paper",
    target_market: "",
  });

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const payload: SimulationInput = {
        ...form,
        target_market: form.target_market?.trim() ? form.target_market.trim() : null,
      };
      const result = await api.createSimulation(payload);
      router.push(`/simulations/${result.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong running the simulation.");
      setSubmitting(false);
    }
  }

  return (
    <Card className="max-w-2xl">
      <CardHeader>
        <CardTitle>New Optimization</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="tea_density">Tea density (g/cm3)</Label>
              <Input
                id="tea_density"
                type="number"
                step="0.01"
                min="0.01"
                required
                value={form.tea_density_g_cm3}
                onChange={(e) => setForm({ ...form, tea_density_g_cm3: Number(e.target.value) })}
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="package_weight">Package weight</Label>
              <Select
                value={String(form.package_weight_g)}
                onValueChange={(v) => setForm({ ...form, package_weight_g: Number(v) })}
              >
                <SelectTrigger id="package_weight" className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {PACKAGE_WEIGHT_OPTIONS_G.map((g) => (
                    <SelectItem key={g} value={String(g)}>
                      {g} g
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="shipment_type">Shipment type</Label>
              <Select
                value={form.shipment_type}
                onValueChange={(v) => setForm({ ...form, shipment_type: v as SimulationInput["shipment_type"] })}
              >
                <SelectTrigger id="shipment_type" className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="total_weight">Total Weight (kg)</SelectItem>
                  <SelectItem value="per_container">Per Container (# containers)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="shipment_quantity">
                Shipment quantity {form.shipment_type === "total_weight" ? "(kg)" : "(containers)"}
              </Label>
              <Input
                id="shipment_quantity"
                type="number"
                min="1"
                required
                value={form.shipment_quantity}
                onChange={(e) => setForm({ ...form, shipment_quantity: Number(e.target.value) })}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="package_shape">Package shape</Label>
              <Select
                value={form.package_shape}
                onValueChange={(v) => setForm({ ...form, package_shape: v as SimulationInput["package_shape"] })}
              >
                <SelectTrigger id="package_shape" className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="square">Square</SelectItem>
                  <SelectItem value="round">Round</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="packaging_material">Packaging material</Label>
              <Select
                value={form.packaging_material}
                onValueChange={(v) =>
                  setForm({ ...form, packaging_material: v as SimulationInput["packaging_material"] })
                }
              >
                <SelectTrigger id="packaging_material" className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="paper">Paper</SelectItem>
                  <SelectItem value="plastic">Plastic</SelectItem>
                  <SelectItem value="metal">Metal</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="target_market">Target market (optional)</Label>
            <Input
              id="target_market"
              placeholder="e.g. European Union"
              value={form.target_market ?? ""}
              onChange={(e) => setForm({ ...form, target_market: e.target.value })}
            />
          </div>

          {error && <p className="text-sm text-status-critical">{error}</p>}

          <Button type="submit" disabled={submitting} className="w-fit">
            {submitting && <Loader2 className="h-4 w-4 animate-spin" />}
            {submitting ? "Optimizing..." : "Run Optimization"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
