import { useEffect, useState } from "react";

import { bodyApi } from "../../api/body";
import Field from "../../components/Field.jsx";

const today = () => new Date().toISOString().slice(0, 10);

export default function DailyMetrics() {
  const [metrics, setMetrics] = useState([]);
  const [form, setForm] = useState({ date: today(), weight_lbs: "", sleep_hours: "", notes: "" });
  const [error, setError] = useState("");

  async function load() {
    setMetrics(await bodyApi.getMetrics(30));
  }

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, []);

  async function submit(event) {
    event.preventDefault();
    setError("");
    try {
      await bodyApi.createMetric({
        date: form.date,
        weight_lbs: form.weight_lbs === "" ? null : Number(form.weight_lbs),
        sleep_hours: form.sleep_hours === "" ? null : Number(form.sleep_hours),
        notes: form.notes || null
      });
      setForm({ date: today(), weight_lbs: "", sleep_hours: "", notes: "" });
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="body-module">
      <header className="page-header">
        <h1>Daily Metrics</h1>
        <p>The thirty-day body record: weight, sleep, and a small place for context.</p>
      </header>
      <div className="grid two-col">
        <form className="form-panel" onSubmit={submit}>
          <Field label="Date">
            <input type="date" value={form.date} onChange={(event) => setForm({ ...form, date: event.target.value })} required />
          </Field>
          <div className="row">
            <Field label="Weight lb">
              <input
                type="number"
                step="0.1"
                value={form.weight_lbs}
                onChange={(event) => setForm({ ...form, weight_lbs: event.target.value })}
              />
            </Field>
            <Field label="Sleep h">
              <input
                type="number"
                step="0.1"
                value={form.sleep_hours}
                onChange={(event) => setForm({ ...form, sleep_hours: event.target.value })}
              />
            </Field>
          </div>
          <Field label="Notes">
            <textarea value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} />
          </Field>
          {error ? <p className="error">{error}</p> : null}
          <button type="submit">Save Metric</button>
        </form>
        <div className="entry">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Lb</th>
                <th>Sleep</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {metrics.map((metric) => (
                <tr key={metric.id}>
                  <td>{metric.date}</td>
                  <td>{metric.weight_lbs ?? "-"}</td>
                  <td>{metric.sleep_hours ?? "-"}</td>
                  <td>{metric.notes || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
