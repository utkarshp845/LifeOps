import { useEffect, useState } from "react";

import { mindApi } from "../../api/mind";
import Field from "../../components/Field.jsx";

const today = () => new Date().toISOString().slice(0, 10);

export default function DecisionJournal() {
  const [decisions, setDecisions] = useState([]);
  const [selected, setSelected] = useState(null);
  const [review, setReview] = useState({ actual_outcome: "", reviewed_at: today() });
  const [form, setForm] = useState({
    date: today(),
    title: "",
    context: "",
    reasoning: "",
    expected_outcome: ""
  });
  const [error, setError] = useState("");

  async function load() {
    const items = await mindApi.getDecisions();
    setDecisions(items);
    if (!selected && items[0]) {
      await selectDecision(items[0].id);
    }
  }

  async function selectDecision(id) {
    const decision = await mindApi.getDecision(id);
    setSelected(decision);
    setReview({
      actual_outcome: decision.actual_outcome || "",
      reviewed_at: decision.reviewed_at || today()
    });
  }

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, []);

  async function submit(event) {
    event.preventDefault();
    setError("");
    try {
      const decision = await mindApi.createDecision(form);
      setForm({ date: today(), title: "", context: "", reasoning: "", expected_outcome: "" });
      await load();
      await selectDecision(decision.id);
    } catch (err) {
      setError(err.message);
    }
  }

  async function saveReview() {
    if (!selected) return;
    setError("");
    try {
      const updated = await mindApi.patchDecision(selected.id, {
        actual_outcome: review.actual_outcome || null,
        reviewed_at: review.reviewed_at || null
      });
      setSelected(updated);
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="mind-module">
      <header className="page-header">
        <h1>Decision Journal</h1>
        <p>A record of choices made under uncertainty, revisited when reality has answered.</p>
      </header>

      <form className="form-panel" onSubmit={submit}>
        <div className="row">
          <Field label="Date">
            <input type="date" value={form.date} onChange={(event) => setForm({ ...form, date: event.target.value })} required />
          </Field>
          <Field label="Title">
            <input value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} required />
          </Field>
        </div>
        <div className="row">
          <Field label="Context">
            <textarea value={form.context} onChange={(event) => setForm({ ...form, context: event.target.value })} required />
          </Field>
          <Field label="Reasoning">
            <textarea value={form.reasoning} onChange={(event) => setForm({ ...form, reasoning: event.target.value })} required />
          </Field>
        </div>
        <Field label="Expected outcome">
          <textarea value={form.expected_outcome} onChange={(event) => setForm({ ...form, expected_outcome: event.target.value })} required />
        </Field>
        {error ? <p className="error">{error}</p> : null}
        <button type="submit">Save Decision</button>
      </form>

      <p className="section-title">Review</p>
      <div className="split-list">
        <div className="list">
          {decisions.map((decision) => (
            <button
              type="button"
              className={`selectable ${selected?.id === decision.id ? "is-active" : ""}`}
              key={decision.id}
              onClick={() => selectDecision(decision.id).catch((err) => setError(err.message))}
            >
              {decision.title}
              <br />
              <span className="muted">{decision.date}</span>
            </button>
          ))}
        </div>
        <article className="entry decision-detail">
          {selected ? (
            <div className="stack">
              <h2>{selected.title}</h2>
              <p className="journal-text">{selected.context}</p>
              <p className="journal-text">{selected.reasoning}</p>
              <p className="journal-text">{selected.expected_outcome}</p>
              <Field label="Actual outcome">
                <textarea value={review.actual_outcome} onChange={(event) => setReview({ ...review, actual_outcome: event.target.value })} />
              </Field>
              <Field label="Reviewed at">
                <input type="date" value={review.reviewed_at} onChange={(event) => setReview({ ...review, reviewed_at: event.target.value })} />
              </Field>
              <button type="button" className="secondary" onClick={saveReview}>
                Save Review
              </button>
            </div>
          ) : (
            <p className="muted">No decision selected.</p>
          )}
        </article>
      </div>
    </section>
  );
}
