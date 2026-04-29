import { useEffect, useState } from "react";

import { buildApi } from "../api/build";
import Field from "../components/Field.jsx";

const today = () => new Date().toISOString().slice(0, 10);

export default function Build() {
  const [projects, setProjects] = useState([]);
  const [form, setForm] = useState({
    name: "",
    description: "",
    status: "building",
    shipped_at: "",
    url: "",
    repository_url: "",
    notes: ""
  });
  const [error, setError] = useState("");

  async function load() {
    setProjects(await buildApi.getProjects());
  }

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, []);

  async function submit(event) {
    event.preventDefault();
    setError("");
    try {
      await buildApi.createProject({
        name: form.name,
        description: form.description || null,
        status: form.status,
        shipped_at: form.shipped_at || null,
        url: form.url || null,
        repository_url: form.repository_url || null,
        notes: form.notes || null
      });
      setForm({ name: "", description: "", status: "building", shipped_at: "", url: "", repository_url: "", notes: "" });
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function markShipped(project) {
    setError("");
    try {
      await buildApi.patchProject(project.id, { status: "shipped", shipped_at: project.shipped_at || today() });
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="mind-module">
      <header className="page-header">
        <h1>Build</h1>
        <p>A record of what you have made real: ideas, shipped work, maintenance, and the trail each project leaves.</p>
      </header>
      <div className="grid two-col">
        <form className="form-panel" onSubmit={submit}>
          <Field label="Name">
            <input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required />
          </Field>
          <Field label="Description">
            <textarea value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} />
          </Field>
          <div className="row">
            <Field label="Status">
              <select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value })}>
                <option value="idea">Idea</option>
                <option value="building">Building</option>
                <option value="shipped">Shipped</option>
                <option value="maintained">Maintained</option>
                <option value="paused">Paused</option>
              </select>
            </Field>
            <Field label="Shipped at">
              <input type="date" value={form.shipped_at} onChange={(event) => setForm({ ...form, shipped_at: event.target.value })} />
            </Field>
          </div>
          <div className="row">
            <Field label="URL">
              <input value={form.url} onChange={(event) => setForm({ ...form, url: event.target.value })} />
            </Field>
            <Field label="Repository">
              <input value={form.repository_url} onChange={(event) => setForm({ ...form, repository_url: event.target.value })} />
            </Field>
          </div>
          <Field label="Notes">
            <textarea value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} />
          </Field>
          {error ? <p className="error">{error}</p> : null}
          <button type="submit">Save Project</button>
        </form>

        <div className="list">
          {projects.map((project) => (
            <article className="entry" key={project.id}>
              <div className="split-heading">
                <h2>{project.name}</h2>
                {project.status !== "shipped" ? (
                  <button className="secondary" type="button" onClick={() => markShipped(project)}>
                    Mark Shipped
                  </button>
                ) : null}
              </div>
              <p className="muted">
                {project.status}
                {project.shipped_at ? ` / ${project.shipped_at}` : ""}
              </p>
              {project.description ? <p className="journal-text">{project.description}</p> : null}
              <div className="link-row">
                {project.url ? (
                  <a className="text-link" href={project.url} target="_blank" rel="noreferrer">
                    Live
                  </a>
                ) : null}
                {project.repository_url ? (
                  <a className="text-link" href={project.repository_url} target="_blank" rel="noreferrer">
                    Repo
                  </a>
                ) : null}
              </div>
              {project.notes ? <p>{project.notes}</p> : null}
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
