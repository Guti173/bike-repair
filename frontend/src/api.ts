import type { RepairOrder, RepairOrderCreate, RepairStatus } from "./types";

const API_URL = "http://127.0.0.1:8000";

const FIELD_LABELS: Record<string, string> = {
  customer_code: "código de cliente",
  bicycle_description: "descripción de la bicicleta",
  reported_issue: "problema informado",
  status: "estado",
};

interface ValidationIssue {
  loc?: (string | number)[];
  type?: string;
  ctx?: { max_length?: number };
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, options);
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw error;
    }
    throw new Error("No se pudo conectar con el servidor. Inténtalo de nuevo.");
  }

  if (response.status === 422) {
    const body = await response.json().catch(() => null);
    const issue: ValidationIssue | undefined = Array.isArray(body?.detail)
      ? body.detail[0]
      : undefined;
    const field = issue?.loc?.at(-1);
    const label = typeof field === "string" ? FIELD_LABELS[field] : undefined;

    if (label && (issue?.type === "missing" || issue?.type === "string_too_short")) {
      throw new Error(`Completa el campo «${label}».`);
    }
    if (label && issue?.type === "string_too_long" && issue.ctx?.max_length) {
      throw new Error(
        `El campo «${label}» admite hasta ${issue.ctx.max_length} caracteres.`,
      );
    }
    if (field === "status") {
      throw new Error("Selecciona un estado válido.");
    }
    throw new Error("Revisa los datos de la reparación e inténtalo de nuevo.");
  }

  if (response.status === 404) {
    throw new Error("La orden de reparación ya no está disponible.");
  }
  if (!response.ok) {
    throw new Error("No se pudo completar la solicitud. Inténtalo de nuevo.");
  }

  return response.json().catch(() => {
    throw new Error("El servidor devolvió una respuesta no válida.");
  }) as Promise<T>;
}

export function listRepairOrders(signal?: AbortSignal): Promise<RepairOrder[]> {
  return request("/repair-orders", { signal });
}

export function createRepairOrder(order: RepairOrderCreate): Promise<RepairOrder> {
  return request("/repair-orders", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(order),
  });
}

export function updateRepairStatus(
  id: number,
  status: RepairStatus,
): Promise<RepairOrder> {
  return request(`/repair-orders/${id}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
}
