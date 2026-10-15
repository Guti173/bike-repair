import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { createRepairOrder, listRepairOrders, updateRepairStatus } from "./api";
import { STATUS_LABELS } from "./types";
import type { RepairOrder, RepairOrderCreate, RepairStatus } from "./types";

const EMPTY_ORDER: RepairOrderCreate = {
  customer_code: "",
  bicycle_description: "",
  reported_issue: "",
};

function errorMessage(error: unknown): string {
  return error instanceof Error
    ? error.message
    : "Se ha producido un error. Inténtalo de nuevo.";
}

export default function App() {
  const [orders, setOrders] = useState<RepairOrder[]>([]);
  const [form, setForm] = useState<RepairOrderCreate>(EMPTY_ORDER);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [createError, setCreateError] = useState<string | null>(null);
  const [updatingIds, setUpdatingIds] = useState<Set<number>>(new Set());
  const [statusErrors, setStatusErrors] = useState<Record<number, string>>({});

  async function loadOrders(signal?: AbortSignal) {
    setIsLoading(true);
    setLoadError(null);
    try {
      const loadedOrders = await listRepairOrders(signal);
      if (!signal?.aborted) setOrders(loadedOrders);
    } catch (error) {
      if (!signal?.aborted) setLoadError(errorMessage(error));
    } finally {
      if (!signal?.aborted) setIsLoading(false);
    }
  }

  useEffect(() => {
    const controller = new AbortController();
    void loadOrders(controller.signal);
    return () => controller.abort();
  }, []);

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsCreating(true);
    setCreateError(null);
    try {
      const created = await createRepairOrder(form);
      setOrders((current) => [...current, created]);
      setForm(EMPTY_ORDER);
    } catch (error) {
      setCreateError(errorMessage(error));
    } finally {
      setIsCreating(false);
    }
  }

  async function handleStatusChange(id: number, status: RepairStatus) {
    setUpdatingIds((current) => new Set(current).add(id));
    setStatusErrors((current) => ({ ...current, [id]: "" }));
    try {
      const updated = await updateRepairStatus(id, status);
      setOrders((current) =>
        current.map((order) => (order.id === id ? updated : order)),
      );
    } catch (error) {
      setStatusErrors((current) => ({ ...current, [id]: errorMessage(error) }));
    } finally {
      setUpdatingIds((current) => {
        const remaining = new Set(current);
        remaining.delete(id);
        return remaining;
      });
    }
  }

  return (
    <main className="page">
      <header className="page-header">
        <h1>Reparaciones de bicicletas</h1>
      </header>

      <div className="workspace">
        <section className="create-section" aria-labelledby="create-heading">
          <h2 id="create-heading">Nueva reparación</h2>
          <p className="hint" id="synthetic-hint">Usa solo datos ficticios.</p>
          <form onSubmit={handleCreate} autoComplete="off" aria-describedby="synthetic-hint">
            <fieldset disabled={isCreating || isLoading || loadError !== null}>
              <label htmlFor="customer-code">Código de cliente</label>
              <input
                id="customer-code"
                name="customer_code"
                required
                value={form.customer_code}
                onChange={(event) =>
                  setForm({ ...form, customer_code: event.target.value })
                }
              />

              <label htmlFor="bicycle-description">Descripción de la bicicleta</label>
              <input
                id="bicycle-description"
                name="bicycle_description"
                required
                value={form.bicycle_description}
                onChange={(event) =>
                  setForm({ ...form, bicycle_description: event.target.value })
                }
              />

              <label htmlFor="reported-issue">Problema informado</label>
              <textarea
                id="reported-issue"
                name="reported_issue"
                rows={4}
                required
                value={form.reported_issue}
                onChange={(event) =>
                  setForm({ ...form, reported_issue: event.target.value })
                }
              />

              <button type="submit">{isCreating ? "Guardando…" : "Crear orden"}</button>
            </fieldset>
            {createError && <p role="alert" className="error">{createError}</p>}
          </form>
        </section>

        <section className="orders-section" aria-labelledby="orders-heading" aria-busy={isLoading}>
          <h2 id="orders-heading">Órdenes de reparación</h2>
          {isLoading && <p role="status" className="hint">Cargando reparaciones…</p>}
          {loadError && (
            <div className="load-error">
              <p role="alert" className="error">{loadError}</p>
              <button type="button" className="secondary" onClick={() => void loadOrders()}>
                Reintentar
              </button>
            </div>
          )}
          {!isLoading && !loadError && orders.length === 0 && (
            <p className="empty-state">No hay reparaciones registradas.</p>
          )}
          {orders.length > 0 && (
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th scope="col">Orden</th>
                    <th scope="col">Código de cliente</th>
                    <th scope="col">Bicicleta</th>
                    <th scope="col">Problema</th>
                    <th scope="col">Estado</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map((order) => (
                    <tr key={order.id}>
                      <th scope="row">#{order.id}</th>
                      <td>{order.customer_code}</td>
                      <td>{order.bicycle_description}</td>
                      <td className="issue-text">{order.reported_issue}</td>
                      <td className="status-cell">
                        <select
                          aria-label={`Estado de la orden ${order.id}`}
                          aria-describedby={statusErrors[order.id] ? `status-error-${order.id}` : undefined}
                          value={order.status}
                          disabled={isLoading || updatingIds.has(order.id)}
                          onChange={(event) =>
                            void handleStatusChange(order.id, event.target.value as RepairStatus)
                          }
                        >
                          {Object.entries(STATUS_LABELS).map(([value, label]) => (
                            <option key={value} value={value}>{label}</option>
                          ))}
                        </select>
                        {updatingIds.has(order.id) && (
                          <small role="status" className="hint">Guardando…</small>
                        )}
                        {statusErrors[order.id] && (
                          <p id={`status-error-${order.id}`} role="alert" className="error">
                            {statusErrors[order.id]}
                          </p>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
