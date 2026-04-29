import { useEffect, useState } from "react";

import { bodyApi } from "../../api/body";
import Field from "../../components/Field.jsx";

const today = () => new Date().toISOString().slice(0, 10);

export default function GolfLog() {
  const [rounds, setRounds] = useState([]);
  const [form, setForm] = useState({ date: today(), course: "", score: "", notes: "" });
  const [error, setError] = useState("");

  async function load() {
    setRounds(await bodyApi.getGolf());
  }

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, []);

  async function submit(event) {
    event.preventDefault();
    setError("");
    try {
      await bodyApi.createGolf({
        date: form.date,
        course: form.course || null,
        score: form.score === "" ? null : Number(form.score),
        notes: form.notes || null
      });
      setForm({ date: today(), course: "", score: "", notes: "" });
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="body-module">
      <header className="page-header">
        <h1>Golf Log</h1>
        <p>Rounds kept without ceremony: course, score, notes.</p>
      </header>
      <div className="grid two-col">
        <form className="form-panel" onSubmit={submit}>
          <Field label="Date">
            <input type="date" value={form.date} onChange={(event) => setForm({ ...form, date: event.target.value })} required />
          </Field>
          <Field label="Course">
            <input value={form.course} onChange={(event) => setForm({ ...form, course: event.target.value })} />
          </Field>
          <Field label="Score">
            <input type="number" value={form.score} onChange={(event) => setForm({ ...form, score: event.target.value })} />
          </Field>
          <Field label="Notes">
            <textarea value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} />
          </Field>
          {error ? <p className="error">{error}</p> : null}
          <button type="submit">Save Round</button>
        </form>
        <div className="list">
          {rounds.map((round) => (
            <article className="entry" key={round.id}>
              <h2>{round.date}</h2>
              <p className="metric-line">
                {round.course || "Course unlisted"} / {round.score ?? "-"}
              </p>
              {round.notes ? <p>{round.notes}</p> : null}
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
