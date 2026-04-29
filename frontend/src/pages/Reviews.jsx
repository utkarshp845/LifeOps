import { useEffect, useState } from "react";

import { goalsApi } from "../api/goals";
import Field from "../components/Field.jsx";

const today = () => new Date().toISOString().slice(0, 10);

export default function Reviews() {
  const [goals, setGoals] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [due, setDue] = useState(null);
  const [form, setForm] = useState({
    kind: "weekly",
    date: today(),
    goal_id: "",
    wins: "",
    friction: "",
    lessons: "",
    next_actions: "",
    notes: ""
  });
  const [error, setError] = useState("");

  async function load() {
    const [nextGoals, nextReviews, nextDue] = await Promise.all([goalsApi.getGoals("active"), goalsApi.getReviews(), goalsApi.getReviewDue()]);
    setGoals(nextGoals);
    setReviews(nextReviews);
    setDue(nextDue);
  }

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, []);

  async function submit(event) {
    event.preventDefault();
    setError("");
    try {
      await goalsApi.createReview({
        kind: form.kind,
        date: form.date,
        goal_id: form.goal_id || null,
        wins: form.wins || null,
        friction: form.friction || null,
        lessons: form.lessons || null,
        next_actions: form.next_actions || null,
        notes: form.notes || null
      });
      setForm({ kind: form.kind, date: today(), goal_id: "", wins: "", friction: "", lessons: "", next_actions: "", notes: "" });
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="mind-module">
      <header className="page-header">
        <h1>Reviews</h1>
        <p>The feedback loop: what moved, what resisted, what you learned, and what changes next.</p>
      </header>

      <div className="grid dashboard-grid">
        <article className="entry">
          <h2>Daily</h2>
          <p className="journal-text">{due?.daily_done ? "Complete" : "Due"}</p>
        </article>
        <article className="entry">
          <h2>Weekly</h2>
          <p className="journal-text">{due?.weekly_done ? "Complete" : "Due"}</p>
        </article>
        <article className="entry">
          <h2>Monthly</h2>
          <p className="journal-text">{due?.monthly_done ? "Complete" : "Due"}</p>
        </article>
      </div>

      <div className="grid two-col section-gap">
        <form className="form-panel" onSubmit={submit}>
          <div className="row">
            <Field label="Kind">
              <select value={form.kind} onChange={(event) => setForm({ ...form, kind: event.target.value })}>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </Field>
            <Field label="Date">
              <input type="date" value={form.date} onChange={(event) => setForm({ ...form, date: event.target.value })} required />
            </Field>
          </div>
          <Field label="Related goal">
            <select value={form.goal_id} onChange={(event) => setForm({ ...form, goal_id: event.target.value })}>
              <option value="">Whole system</option>
              {goals.map((goal) => (
                <option key={goal.id} value={goal.id}>
                  {goal.title}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Wins">
            <textarea value={form.wins} onChange={(event) => setForm({ ...form, wins: event.target.value })} />
          </Field>
          <Field label="Friction">
            <textarea value={form.friction} onChange={(event) => setForm({ ...form, friction: event.target.value })} />
          </Field>
          <Field label="Lessons">
            <textarea value={form.lessons} onChange={(event) => setForm({ ...form, lessons: event.target.value })} />
          </Field>
          <Field label="Next actions">
            <textarea value={form.next_actions} onChange={(event) => setForm({ ...form, next_actions: event.target.value })} />
          </Field>
          <Field label="Notes">
            <textarea value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} />
          </Field>
          {error ? <p className="error">{error}</p> : null}
          <button type="submit">Save Review</button>
        </form>

        <div className="list">
          {reviews.map((review) => (
            <article className="entry" key={review.id}>
              <h2>
                {review.kind} / {review.date}
              </h2>
              <p className="muted">{review.goal?.title || "Whole system"}</p>
              {review.wins ? <p className="journal-text">{review.wins}</p> : null}
              {review.friction ? <p>{review.friction}</p> : null}
              {review.lessons ? <p>{review.lessons}</p> : null}
              {review.next_actions ? <p>{review.next_actions}</p> : null}
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
