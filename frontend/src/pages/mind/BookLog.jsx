import { useEffect, useState } from "react";

import { mindApi } from "../../api/mind";
import Field from "../../components/Field.jsx";

function BookItem({ book, onSaved }) {
  const [dateFinished, setDateFinished] = useState(book.date_finished || "");
  const [reaction, setReaction] = useState(book.my_reaction || "");
  const [error, setError] = useState("");

  async function save() {
    setError("");
    try {
      await mindApi.patchBook(book.id, {
        date_finished: dateFinished || null,
        my_reaction: reaction || null
      });
      onSaved();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <article className="entry">
      <h2>{book.title}</h2>
      <p className="muted">{book.author}</p>
      <div className="stack">
        <Field label="Date finished">
          <input type="date" value={dateFinished} onChange={(event) => setDateFinished(event.target.value)} />
        </Field>
        <Field label="My reaction">
          <textarea value={reaction} onChange={(event) => setReaction(event.target.value)} />
        </Field>
        {error ? <p className="error">{error}</p> : null}
        <button type="button" className="secondary" onClick={save}>
          Save Book Notes
        </button>
      </div>
    </article>
  );
}

export default function BookLog() {
  const [books, setBooks] = useState([]);
  const [form, setForm] = useState({ title: "", author: "", date_finished: "", my_reaction: "" });
  const [error, setError] = useState("");

  async function load() {
    setBooks(await mindApi.getBooks());
  }

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, []);

  async function submit(event) {
    event.preventDefault();
    setError("");
    try {
      await mindApi.createBook({
        title: form.title,
        author: form.author,
        date_finished: form.date_finished || null,
        my_reaction: form.my_reaction || null
      });
      setForm({ title: "", author: "", date_finished: "", my_reaction: "" });
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="mind-module">
      <header className="page-header">
        <h1>Book Log</h1>
        <p>Books belong here as encounters: title, author, finish date, and the reaction they left behind.</p>
      </header>
      <div className="grid two-col">
        <form className="form-panel" onSubmit={submit}>
          <Field label="Title">
            <input value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} required />
          </Field>
          <Field label="Author">
            <input value={form.author} onChange={(event) => setForm({ ...form, author: event.target.value })} required />
          </Field>
          <Field label="Date finished">
            <input type="date" value={form.date_finished} onChange={(event) => setForm({ ...form, date_finished: event.target.value })} />
          </Field>
          <Field label="My reaction">
            <textarea value={form.my_reaction} onChange={(event) => setForm({ ...form, my_reaction: event.target.value })} />
          </Field>
          {error ? <p className="error">{error}</p> : null}
          <button type="submit">Save Book</button>
        </form>
        <div className="list">
          {books.map((book) => (
            <BookItem key={book.id} book={book} onSaved={load} />
          ))}
        </div>
      </div>
    </section>
  );
}
