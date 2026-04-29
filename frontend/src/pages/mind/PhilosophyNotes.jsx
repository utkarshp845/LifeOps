import { useEffect, useState } from "react";

import { mindApi } from "../../api/mind";
import Field from "../../components/Field.jsx";

const today = () => new Date().toISOString().slice(0, 10);

export default function PhilosophyNotes() {
  const [notes, setNotes] = useState([]);
  const [form, setForm] = useState({ thinker: "", source: "", disturbance: "", date: today() });
  const [error, setError] = useState("");

  async function load() {
    setNotes(await mindApi.getPhilosophy());
  }

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, []);

  async function submit(event) {
    event.preventDefault();
    setError("");
    try {
      await mindApi.createPhilosophy({
        thinker: form.thinker,
        source: form.source || null,
        disturbance: form.disturbance,
        date: form.date
      });
      setForm({ thinker: "", source: "", disturbance: "", date: today() });
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="mind-module">
      <header className="page-header">
        <h1>Philosophy Notes</h1>
        <p>Notes stay as they were first written: the thinker, the source, and the disturbance.</p>
      </header>
      <div className="grid two-col">
        <form className="form-panel" onSubmit={submit}>
          <Field label="Thinker">
            <input value={form.thinker} onChange={(event) => setForm({ ...form, thinker: event.target.value })} required />
          </Field>
          <Field label="Source">
            <input value={form.source} onChange={(event) => setForm({ ...form, source: event.target.value })} />
          </Field>
          <Field label="Date">
            <input type="date" value={form.date} onChange={(event) => setForm({ ...form, date: event.target.value })} required />
          </Field>
          <Field label="Disturbance">
            <textarea value={form.disturbance} onChange={(event) => setForm({ ...form, disturbance: event.target.value })} required />
          </Field>
          {error ? <p className="error">{error}</p> : null}
          <button type="submit">Save Note</button>
        </form>
        <div className="list">
          {notes.map((note) => (
            <article className="entry" key={note.id}>
              <h2>{note.thinker}</h2>
              <p className="muted">
                {note.date}
                {note.source ? ` / ${note.source}` : ""}
              </p>
              <p className="journal-text">{note.disturbance}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
