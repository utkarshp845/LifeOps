import { useEffect, useState } from "react";

import { wealthApi } from "../api/wealth";
import Field from "../components/Field.jsx";

const today = () => new Date().toISOString().slice(0, 10);
const money = (value) =>
  value === null || value === undefined
    ? "-"
    : new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);
const pct = (value) => (value === null || value === undefined ? "-" : `${value.toFixed(1)}%`);

function numberOrNull(value) {
  return value === "" ? null : Number(value);
}

export default function Wealth() {
  const [summary, setSummary] = useState(null);
  const [snapshots, setSnapshots] = useState([]);
  const [form, setForm] = useState({
    date: today(),
    cash: "",
    investments: "",
    retirement: "",
    crypto: "",
    other_assets: "",
    debt: "",
    annual_expenses: "",
    financial_freedom_number: "",
    notes: ""
  });
  const [error, setError] = useState("");

  async function load() {
    const [nextSummary, nextSnapshots] = await Promise.all([wealthApi.getSummary(), wealthApi.getSnapshots(30)]);
    setSummary(nextSummary);
    setSnapshots(nextSnapshots);
  }

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, []);

  async function submit(event) {
    event.preventDefault();
    setError("");
    try {
      await wealthApi.createSnapshot({
        date: form.date,
        cash: numberOrNull(form.cash),
        investments: numberOrNull(form.investments),
        retirement: numberOrNull(form.retirement),
        crypto: numberOrNull(form.crypto),
        other_assets: numberOrNull(form.other_assets),
        debt: numberOrNull(form.debt),
        annual_expenses: numberOrNull(form.annual_expenses),
        financial_freedom_number: numberOrNull(form.financial_freedom_number),
        notes: form.notes || null
      });
      setForm({ ...form, notes: "" });
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="body-module">
      <header className="page-header">
        <h1>Wealth</h1>
        <p>Financial freedom tracked as a sober distance: assets, debt, expenses, runway, and progress.</p>
      </header>

      <div className="grid dashboard-grid">
        <article className="entry">
          <h2>Net Worth</h2>
          <p className="metric-large">{money(summary?.net_worth)}</p>
        </article>
        <article className="entry">
          <h2>Freedom Progress</h2>
          <p className="metric-large">{pct(summary?.progress_pct)}</p>
        </article>
        <article className="entry">
          <h2>Freedom Number</h2>
          <p className="metric-large">{money(summary?.financial_freedom_number)}</p>
        </article>
        <article className="entry">
          <h2>Runway</h2>
          <p className="metric-large">{summary?.runway_years !== null && summary?.runway_years !== undefined ? `${summary.runway_years.toFixed(1)} years` : "-"}</p>
        </article>
      </div>

      <div className="grid two-col section-gap">
        <form className="form-panel" onSubmit={submit}>
          <Field label="Date">
            <input type="date" value={form.date} onChange={(event) => setForm({ ...form, date: event.target.value })} required />
          </Field>
          <div className="row">
            <Field label="Cash">
              <input type="number" step="0.01" value={form.cash} onChange={(event) => setForm({ ...form, cash: event.target.value })} />
            </Field>
            <Field label="Investments">
              <input
                type="number"
                step="0.01"
                value={form.investments}
                onChange={(event) => setForm({ ...form, investments: event.target.value })}
              />
            </Field>
          </div>
          <div className="row">
            <Field label="Retirement">
              <input
                type="number"
                step="0.01"
                value={form.retirement}
                onChange={(event) => setForm({ ...form, retirement: event.target.value })}
              />
            </Field>
            <Field label="Crypto">
              <input type="number" step="0.01" value={form.crypto} onChange={(event) => setForm({ ...form, crypto: event.target.value })} />
            </Field>
          </div>
          <div className="row">
            <Field label="Other assets">
              <input
                type="number"
                step="0.01"
                value={form.other_assets}
                onChange={(event) => setForm({ ...form, other_assets: event.target.value })}
              />
            </Field>
            <Field label="Debt">
              <input type="number" step="0.01" value={form.debt} onChange={(event) => setForm({ ...form, debt: event.target.value })} />
            </Field>
          </div>
          <div className="row">
            <Field label="Annual expenses">
              <input
                type="number"
                step="0.01"
                value={form.annual_expenses}
                onChange={(event) => setForm({ ...form, annual_expenses: event.target.value })}
              />
            </Field>
            <Field label="Freedom number">
              <input
                type="number"
                step="0.01"
                value={form.financial_freedom_number}
                onChange={(event) => setForm({ ...form, financial_freedom_number: event.target.value })}
              />
            </Field>
          </div>
          <Field label="Notes">
            <textarea value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} />
          </Field>
          {error ? <p className="error">{error}</p> : null}
          <button type="submit">Save Snapshot</button>
        </form>

        <div className="entry">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Net Worth</th>
                <th>Progress</th>
                <th>Runway</th>
              </tr>
            </thead>
            <tbody>
              {snapshots.map((snapshot) => (
                <tr key={snapshot.id}>
                  <td>{snapshot.date}</td>
                  <td>{money(snapshot.net_worth)}</td>
                  <td>{pct(snapshot.progress_pct)}</td>
                  <td>{snapshot.runway_years !== null && snapshot.runway_years !== undefined ? `${snapshot.runway_years.toFixed(1)}y` : "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
