import { SimulationForm } from "@/components/simulation-form";

export default function NewSimulationPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">New Simulation</h1>
        <p className="text-sm text-muted-foreground">
          Enter the tea and shipment details. The engine will recommend a package, carton, pallet,
          and container configuration and compare it against current (non-optimized) practice.
        </p>
      </div>
      <SimulationForm />
    </div>
  );
}
