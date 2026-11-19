// Domain registry - single source of truth (docs/web/PAGES.md).
// Order is fixed. Status drives color, panel type, and icon.

export type DomainStatus = "active" | "planned" | "exploring";

export interface DomainDef {
  order: number;
  id: string;
  label: string;
  status: DomainStatus;
  children: { id: string; label: string; status: DomainStatus }[];
}

export const DOMAINS: DomainDef[] = [
  {
    order: 1,
    id: "batteries",
    label: "Batteries",
    status: "active",
    children: [
      { id: "cathodes", label: "Cathodes", status: "active" },
      { id: "electrolytes", label: "Electrolytes", status: "planned" },
    ],
  },
  { order: 2, id: "supercapacitors", label: "Supercapacitors", status: "planned", children: [] },
  { order: 3, id: "solar-absorbers", label: "Solar Absorbers", status: "planned", children: [] },
  { order: 4, id: "hydrogen-storage", label: "Hydrogen Storage", status: "planned", children: [] },
  { order: 5, id: "catalysts", label: "Catalysts", status: "planned", children: [] },
  { order: 6, id: "thermoelectrics", label: "Thermoelectrics", status: "exploring", children: [] },
  { order: 7, id: "wind-energy", label: "Wind Energy", status: "exploring", children: [] },
  { order: 8, id: "hydro-energy", label: "Hydro Energy", status: "exploring", children: [] },
  { order: 9, id: "geothermal-energy", label: "Geothermal Energy", status: "exploring", children: [] },
];
