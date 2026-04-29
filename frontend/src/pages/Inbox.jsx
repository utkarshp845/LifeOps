import { useEffect, useMemo, useState } from "react";

import { captureApi } from "../api/capture";
import Field from "../components/Field.jsx";
import QuickCapture from "../components/QuickCapture.jsx";

const today = () => new Date().toISOString().slice(0, 10);

const targets = [
  ["workout", "Workout"],
  ["metric", "Daily Metric"],
  ["golf", "Golf Round"],
  ["book", "Book"],
  ["philosophy", "Philosophy Note"],
  ["decision", "Decision"],
  ["stock", "Stock"],
  ["build_project", "Build Project"],
  ["wealth_snapshot", "Wealth Snapshot"]
];

function emptyDraft(type, raw) {
  const date = today();
  if (type === "workout") return { date, notes: raw, exercise_name: "", sets: "", reps: "", weight_lbs: "" };
  if (type === "metric") return { date, weight_lbs: "", sleep_hours: "", notes: raw };
  if (type === "golf") return { date, course: "", score: "", notes: raw };
  if (type === "book") return { title: "", author: "", date_finished: "", my_reaction: raw };
  if (type === "philosophy") return { thinker: "", source: "", disturbance: raw, date };
  if (type === "stock") return { ticker: "", company_name: "", shares: "", average_cost: "", watchlist: true, thesis: raw, notes: "" };
  if (type === "build_project") {
    return { name: "", description: raw, status: "building", shipped_at: "", url: "", repository_url: "", notes: "" };
  }
  if (type === "wealth_snapshot") {
    return {
      date,
      cash: "",
      investments: "",
      retirement: "",
      crypto: "",
      other_assets: "",
      debt: "",
      annual_expenses: "",
      financial_freedom_number: "",
      notes: raw
    };
  }
  return { date, title: "", context: raw, reasoning: "", expected_outcome: "" };
}

function numberOrNull(value) {
  return value === "" ? null : Number(value);
}

function conversionPayload(type, draft) {
  if (type === "workout") {
    const exercises = draft.exercise_name.trim()
      ? [
          {
            name: draft.exercise_name.trim(),
            sets: numberOrNull(draft.sets),
            reps: numberOrNull(draft.reps),
            weight_lbs: numberOrNull(draft.weight_lbs)
          }
        ]
      : [];
    return { date: draft.date, notes: draft.notes || null, exercises };
  }
  if (type === "metric") {
    return {
      date: draft.date,
      weight_lbs: numberOrNull(draft.weight_lbs),
      sleep_hours: numberOrNull(draft.sleep_hours),
      notes: draft.notes || null
    };
  }
  if (type === "golf") {
    return {
      date: draft.date,
      course: draft.course || null,
      score: numberOrNull(draft.score),
      notes: draft.notes || null
    };
  }
  if (type === "book") {
    return {
      title: draft.title,
      author: draft.author,
      date_finished: draft.date_finished || null,
      my_reaction: draft.my_reaction || null
    };
  }
  if (type === "philosophy") {
    return {
      thinker: draft.thinker,
      source: draft.source || null,
      disturbance: draft.disturbance,
      date: draft.date
    };
  }
  if (type === "stock") {
    return {
      ticker: draft.ticker,
      company_name: draft.company_name || null,
      shares: numberOrNull(draft.shares),
      average_cost: numberOrNull(draft.average_cost),
      watchlist: draft.watchlist,
      thesis: draft.thesis || null,
      notes: draft.notes || null
    };
  }
  if (type === "build_project") {
    return {
      name: draft.name,
      description: draft.description || null,
      status: draft.status,
      shipped_at: draft.shipped_at || null,
      url: draft.url || null,
      repository_url: draft.repository_url || null,
      notes: draft.notes || null
    };
  }
  if (type === "wealth_snapshot") {
    return {
      date: draft.date,
      cash: numberOrNull(draft.cash),
      investments: numberOrNull(draft.investments),
      retirement: numberOrNull(draft.retirement),
      crypto: numberOrNull(draft.crypto),
      other_assets: numberOrNull(draft.other_assets),
      debt: numberOrNull(draft.debt),
      annual_expenses: numberOrNull(draft.annual_expenses),
      financial_freedom_number: numberOrNull(draft.financial_freedom_number),
      notes: draft.notes || null
    };
  }
  return {
    date: draft.date,
    title: draft.title,
    context: draft.context,
    reasoning: draft.reasoning,
    expected_outcome: draft.expected_outcome
  };
}

function ConvertForm({ item, onConverted }) {
  const [type, setType] = useState("workout");
  const [draft, setDraft] = useState(() => emptyDraft("workout", item.raw_text));
  const [error, setError] = useState("");

  function changeType(nextType) {
    setType(nextType);
    setDraft(emptyDraft(nextType, item.raw_text));
    setError("");
  }

  function update(key, value) {
    setDraft((current) => ({ ...current, [key]: value }));
  }

  async function convert(event) {
    event.preventDefault();
    setError("");
    try {
      await captureApi.convertCapture(item.id, {
        target_type: type,
        payload: conversionPayload(type, draft)
      });
      onConverted();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <form className="convert-panel" onSubmit={convert}>
      <Field label="Convert to">
        <select value={type} onChange={(event) => changeType(event.target.value)}>
          {targets.map(([value, label]) => (
            <option value={value} key={value}>
              {label}
            </option>
          ))}
        </select>
      </Field>

      {type === "workout" ? (
        <>
          <Field label="Date">
            <input type="date" value={draft.date} onChange={(event) => update("date", event.target.value)} required />
          </Field>
          <Field label="Notes">
            <textarea value={draft.notes} onChange={(event) => update("notes", event.target.value)} />
          </Field>
          <div className="inline-row compact">
            <Field label="Exercise">
              <input value={draft.exercise_name} onChange={(event) => update("exercise_name", event.target.value)} />
            </Field>
            <Field label="Sets">
              <input type="number" value={draft.sets} onChange={(event) => update("sets", event.target.value)} />
            </Field>
            <Field label="Reps">
              <input type="number" value={draft.reps} onChange={(event) => update("reps", event.target.value)} />
            </Field>
            <Field label="Weight">
              <input type="number" step="0.5" value={draft.weight_lbs} onChange={(event) => update("weight_lbs", event.target.value)} />
            </Field>
          </div>
        </>
      ) : null}

      {type === "metric" ? (
        <>
          <Field label="Date">
            <input type="date" value={draft.date} onChange={(event) => update("date", event.target.value)} required />
          </Field>
          <div className="row">
            <Field label="Weight lb">
              <input type="number" step="0.1" value={draft.weight_lbs} onChange={(event) => update("weight_lbs", event.target.value)} />
            </Field>
            <Field label="Sleep h">
              <input type="number" step="0.1" value={draft.sleep_hours} onChange={(event) => update("sleep_hours", event.target.value)} />
            </Field>
          </div>
          <Field label="Notes">
            <textarea value={draft.notes} onChange={(event) => update("notes", event.target.value)} />
          </Field>
        </>
      ) : null}

      {type === "golf" ? (
        <>
          <Field label="Date">
            <input type="date" value={draft.date} onChange={(event) => update("date", event.target.value)} required />
          </Field>
          <div className="row">
            <Field label="Course">
              <input value={draft.course} onChange={(event) => update("course", event.target.value)} />
            </Field>
            <Field label="Score">
              <input type="number" value={draft.score} onChange={(event) => update("score", event.target.value)} />
            </Field>
          </div>
          <Field label="Notes">
            <textarea value={draft.notes} onChange={(event) => update("notes", event.target.value)} />
          </Field>
        </>
      ) : null}

      {type === "book" ? (
        <>
          <div className="row">
            <Field label="Title">
              <input value={draft.title} onChange={(event) => update("title", event.target.value)} required />
            </Field>
            <Field label="Author">
              <input value={draft.author} onChange={(event) => update("author", event.target.value)} required />
            </Field>
          </div>
          <Field label="Date finished">
            <input type="date" value={draft.date_finished} onChange={(event) => update("date_finished", event.target.value)} />
          </Field>
          <Field label="My reaction">
            <textarea value={draft.my_reaction} onChange={(event) => update("my_reaction", event.target.value)} />
          </Field>
        </>
      ) : null}

      {type === "philosophy" ? (
        <>
          <div className="row">
            <Field label="Thinker">
              <input value={draft.thinker} onChange={(event) => update("thinker", event.target.value)} required />
            </Field>
            <Field label="Source">
              <input value={draft.source} onChange={(event) => update("source", event.target.value)} />
            </Field>
          </div>
          <Field label="Date">
            <input type="date" value={draft.date} onChange={(event) => update("date", event.target.value)} required />
          </Field>
          <Field label="Disturbance">
            <textarea value={draft.disturbance} onChange={(event) => update("disturbance", event.target.value)} required />
          </Field>
        </>
      ) : null}

      {type === "decision" ? (
        <>
          <div className="row">
            <Field label="Date">
              <input type="date" value={draft.date} onChange={(event) => update("date", event.target.value)} required />
            </Field>
            <Field label="Title">
              <input value={draft.title} onChange={(event) => update("title", event.target.value)} required />
            </Field>
          </div>
          <Field label="Context">
            <textarea value={draft.context} onChange={(event) => update("context", event.target.value)} required />
          </Field>
          <Field label="Reasoning">
            <textarea value={draft.reasoning} onChange={(event) => update("reasoning", event.target.value)} required />
          </Field>
          <Field label="Expected outcome">
            <textarea value={draft.expected_outcome} onChange={(event) => update("expected_outcome", event.target.value)} required />
          </Field>
        </>
      ) : null}

      {type === "stock" ? (
        <>
          <div className="row">
            <Field label="Ticker">
              <input value={draft.ticker} onChange={(event) => update("ticker", event.target.value)} required />
            </Field>
            <Field label="Company">
              <input value={draft.company_name} onChange={(event) => update("company_name", event.target.value)} />
            </Field>
          </div>
          <div className="row">
            <Field label="Shares">
              <input type="number" step="0.0001" value={draft.shares} onChange={(event) => update("shares", event.target.value)} />
            </Field>
            <Field label="Average cost">
              <input type="number" step="0.01" value={draft.average_cost} onChange={(event) => update("average_cost", event.target.value)} />
            </Field>
          </div>
          <label className="checkbox-line">
            <input type="checkbox" checked={draft.watchlist} onChange={(event) => update("watchlist", event.target.checked)} />
            Watchlist only
          </label>
          <Field label="Thesis">
            <textarea value={draft.thesis} onChange={(event) => update("thesis", event.target.value)} />
          </Field>
          <Field label="Notes">
            <textarea value={draft.notes} onChange={(event) => update("notes", event.target.value)} />
          </Field>
        </>
      ) : null}

      {type === "build_project" ? (
        <>
          <Field label="Name">
            <input value={draft.name} onChange={(event) => update("name", event.target.value)} required />
          </Field>
          <Field label="Description">
            <textarea value={draft.description} onChange={(event) => update("description", event.target.value)} />
          </Field>
          <div className="row">
            <Field label="Status">
              <select value={draft.status} onChange={(event) => update("status", event.target.value)}>
                <option value="idea">Idea</option>
                <option value="building">Building</option>
                <option value="shipped">Shipped</option>
                <option value="maintained">Maintained</option>
                <option value="paused">Paused</option>
              </select>
            </Field>
            <Field label="Shipped at">
              <input type="date" value={draft.shipped_at} onChange={(event) => update("shipped_at", event.target.value)} />
            </Field>
          </div>
          <div className="row">
            <Field label="URL">
              <input value={draft.url} onChange={(event) => update("url", event.target.value)} />
            </Field>
            <Field label="Repository">
              <input value={draft.repository_url} onChange={(event) => update("repository_url", event.target.value)} />
            </Field>
          </div>
          <Field label="Notes">
            <textarea value={draft.notes} onChange={(event) => update("notes", event.target.value)} />
          </Field>
        </>
      ) : null}

      {type === "wealth_snapshot" ? (
        <>
          <Field label="Date">
            <input type="date" value={draft.date} onChange={(event) => update("date", event.target.value)} required />
          </Field>
          <div className="row">
            <Field label="Cash">
              <input type="number" step="0.01" value={draft.cash} onChange={(event) => update("cash", event.target.value)} />
            </Field>
            <Field label="Investments">
              <input type="number" step="0.01" value={draft.investments} onChange={(event) => update("investments", event.target.value)} />
            </Field>
          </div>
          <div className="row">
            <Field label="Retirement">
              <input type="number" step="0.01" value={draft.retirement} onChange={(event) => update("retirement", event.target.value)} />
            </Field>
            <Field label="Debt">
              <input type="number" step="0.01" value={draft.debt} onChange={(event) => update("debt", event.target.value)} />
            </Field>
          </div>
          <div className="row">
            <Field label="Annual expenses">
              <input type="number" step="0.01" value={draft.annual_expenses} onChange={(event) => update("annual_expenses", event.target.value)} />
            </Field>
            <Field label="Freedom number">
              <input
                type="number"
                step="0.01"
                value={draft.financial_freedom_number}
                onChange={(event) => update("financial_freedom_number", event.target.value)}
              />
            </Field>
          </div>
          <Field label="Notes">
            <textarea value={draft.notes} onChange={(event) => update("notes", event.target.value)} />
          </Field>
        </>
      ) : null}

      {error ? <p className="error">{error}</p> : null}
      <button type="submit">Convert</button>
    </form>
  );
}

function CaptureCard({ item, onChanged }) {
  const [open, setOpen] = useState(false);
  const createdAt = useMemo(() => new Date(item.created_at).toLocaleString(), [item.created_at]);

  async function archive() {
    await captureApi.updateCapture(item.id, { status: "archived" });
    onChanged();
  }

  return (
    <article className="entry capture-card">
      <p className="capture-text">{item.raw_text}</p>
      <p className="muted">{createdAt}</p>
      <div className="capture-actions">
        <button className="secondary" type="button" onClick={() => setOpen((value) => !value)}>
          {open ? "Close" : "Convert"}
        </button>
        <button className="ghost" type="button" onClick={archive}>
          Archive
        </button>
      </div>
      {open ? <ConvertForm item={item} onConverted={onChanged} /> : null}
    </article>
  );
}

export default function Inbox() {
  const [captures, setCaptures] = useState([]);
  const [error, setError] = useState("");

  async function load() {
    setCaptures(await captureApi.getCaptures("open"));
  }

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, []);

  return (
    <section>
      <header className="page-header">
        <h1>Inbox</h1>
        <p>Capture first. Decide what it means later.</p>
      </header>
      <QuickCapture onCaptured={load} />
      {error ? <p className="error">{error}</p> : null}
      <p className="section-title">Open Captures</p>
      <div className="list">
        {captures.length ? (
          captures.map((item) => <CaptureCard key={item.id} item={item} onChanged={load} />)
        ) : (
          <article className="entry">
            <p className="muted">Inbox is clear.</p>
          </article>
        )}
      </div>
    </section>
  );
}
