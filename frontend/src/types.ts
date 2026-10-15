export const STATUS_LABELS = {
  pending: "Pendiente",
  in_progress: "En reparación",
  completed: "Terminada",
} as const;

export type RepairStatus = keyof typeof STATUS_LABELS;

export interface RepairOrderCreate {
  customer_code: string;
  bicycle_description: string;
  reported_issue: string;
}

export interface RepairOrder extends RepairOrderCreate {
  id: number;
  status: RepairStatus;
}
