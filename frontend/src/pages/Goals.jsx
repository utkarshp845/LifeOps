import { useEffect, useState } from "react";

import { goalsApi } from "../api/goals";
import Field from "../components/Field.jsx";

function numberOrNull(value) {
  return value === "" ? null : Number(value);
}

function pct(value) {
  return value === null || value === undefined ? "-" : `${value.toFixed(1)}%`;
}

export default function Goals() {
  const [areas, setAreas] = useState([]);
  const [goals, setGoals] = useState([]);
  const [areaForm, setAreaForm] = useState({ name: "", description: "", position: 0 });
  const [goalForm, setGoalForm] = useState({
    area_id: "",
    title: "",
    why: "",
    status: "active",
    target_date: "",
    metric_name: "",
    target_value: "",
    current_value: "",
    unit: "",
    notes: ""
  });
  const [error, setError] = useState("");

  async function load() {
    const [nextAreas, nextGoals] = await Promise.all([goalsApi.getAreas(), goalsApi.getGoals()]);
    setAreas(nextAreas);
    setGoals(nextGoals);
  }

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, []);

  async function saveArea(event) {
    event.preventDefault();
    setError("");
    try {
      await goalsApi.createArea({ ...areaForm, position: Number(areaForm.position) || 0 });
      setAreaForm({ name: "", description: "", position: 0 });
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function saveGoal(event) {
    event.preventDefault();
    setError("");
    try {
      await goalsApi.createGoal({
        area_id: goalForm.area_id || null,
        title: goalForm.title,
        why: goalForm.why || null,
        status: goalForm.status,
        target_date: goalForm.target_date || null,
        metric_name: goalForm.metric_name || null,
        target_value: numberOrNull(goalForm.target_value),
        current_value: numberOrNull(goalForm.current_value),
        unit: goalForm.unit || null,
        notes: goalForm.notes || null
      });
      setGoalForm({ area_id: "", title: "", why: "", status: "active", target_date: "", metric_name: "", target_value: "", current_value: "", unit: "", notes: "" });
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function updateGoal(goal, payload) {
    setError("");
    try {
      await goalsApi.patchGoal(goal.id, payload);
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="mind-module">
      <header className="page-header">
        <h1>Goals</h1>
        <p>The spine of Life OS: a few high-level aims that give the rest of the data a job.</p>
      </header>
      <div className="grid two-col">
        <div className="stack">
          <form className="form-panel" onSubmit={saveArea}>
            <p className="section-title">Life Area</p>
            <Field label="Name">
              <input value={areaForm.name} onChange={(event) => setAreaForm({ ...areaForm, name: event.target.value })} required />
            </Field>
            <Field label="Description">
              <textarea value={areaForm.description} onChange={(event) => setAreaForm({ ...areaForm, description: event.target.value })} />
            </Field>
            <Field label="Position">
              <input type="number" value={areaForm.position} onChange={(event) => setAreaForm({ ...areaForm, position: event.target.value })} />
            </Field>
            <button type="submit">Save Area</button>
          </form>

          <form className="form-panel" onSubmit={saveGoal}>
            <p className="section-title">Goal</p>
            <Field label="Area">
              <select value={goalForm.area_id} onChange={(event) => setGoalForm({ ...goalForm, area_id: event.target.value })}>
                <option value="">Unassigned</option>
                {areas.map((area) => (
                  <option key={area.id} value={area.id}>
                    {area.name}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Title">
              <input value={goalForm.title} onChange={(event) => setGoalForm({ ...goalForm, title: event.target.value })} required />
            </Field>
            <Field label="Why">
              <textarea value={goalForm.why} onChange={(event) => setGoalForm({ ...goalForm, why: event.target.value })} />
            </Field>
            <div className="row">
              <Field label="Target date">
                <input type="date" value={goalForm.target_date} onChange={(event) => setGoalForm({ ...goalForm, target_date: event.target.value })} />
              </Field>
              <Field label="Metric">
                <input value={goalForm.metric_name} onChange={(event) => setGoalForm({ ...goalForm, metric_name: event.target.value })} />
              </Field>
            </div>
            <div className="row">
              <Field label="Current">
                <input type="number" step="0.01" value={goalForm.current_value} onChange={(event) => setGoalForm({ ...goalForm, current_value: event.target.value })} />
              </Field>
              <Field label="Target">
                <input type="number" step="0.01" value={goalForm.target_value} onChange={(event) => setGoalForm({ ...goalForm, target_value: event.target.value })} />
              </Field>
            </div>
            <Field label="Unit">
              <input value={goalForm.unit} onChange={(event) => setGoalForm({ ...goalForm, unit: event.target.value })} />
            </Field>
            <Field label="Notes">
              <textarea value={goalForm.notes} onChange={(event) => setGoalForm({ ...goalForm, notes: event.target.value })} />
            </Field>
            {error ? <p className="error">{error}</p> : null}
            <button type="submit">Save Goal</button>
          </form>
        </div>

        <div className="list">
          {goals.map((goal) => (
            <article className="entry" key={goal.id}>
              <div className="split-heading">
                <h2>{goal.title}</h2>
                <select value={goal.status} onChange={(event) => updateGoal(goal, { status: event.target.value })}>
                  <option value="active">Active</option>
                  <option value="paused">Paused</option>
                  <option value="achieved">Achieved</option>
                  <option value="dropped">Dropped</option>
                </select>
              </div>
              <p className="muted">
                {goal.area?.name || "Unassigned"}
                {goal.target_date ? ` / ${goal.target_date}` : ""}
              </p>
              {goal.why ? <p className="journal-text">{goal.why}</p> : null}
              <p className="metric-line">
                {goal.metric_name || "Progress"}: {goal.current_value ?? "-"} / {goal.target_value ?? "-"} {goal.unit || ""} ({pct(goal.progress_pct)})
              </p>
              {goal.notes ? <p>{goal.notes}</p> : null}
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
