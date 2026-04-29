import { useEffect, useState } from "react";

import { bodyApi } from "../api/body";
import { mindApi } from "../api/mind";
import { captureApi } from "../api/capture";
import QuickCapture from "../components/QuickCapture.jsx";

function parseDay(value) {
  return new Date(`${value}T00:00:00`);
}

function Empty({ children }) {
  return <p className="muted">{children}</p>;
}

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const [workouts, golf, metrics, books, philosophy, decisions, captures] = await Promise.all([
          bodyApi.getWorkouts(),
          bodyApi.getGolf(),
          bodyApi.getMetrics(1),
          mindApi.getBooks(),
          mindApi.getPhilosophy(),
          mindApi.getDecisions(),
          captureApi.getCaptures("open")
        ]);
        if (!cancelled) {
          setData({ workouts, golf, metrics, books, philosophy, decisions, captures });
        }
      } catch (err) {
        if (!cancelled) setError(err.message);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const today = new Date();
  const cutoff = new Date(today);
  cutoff.setDate(today.getDate() - 6);
  const recentWorkouts = (data?.workouts || []).filter((workout) => parseDay(workout.date) >= cutoff);
  const currentBook = (data?.books || []).find((book) => !book.date_finished);

  return (
    <section>
      <header className="page-header">
        <h1>Dashboard</h1>
        <p>A private daily surface for the body you maintain and the mind you answer to.</p>
      </header>

      {error ? <p className="error">{error}</p> : null}
      <QuickCapture
        onCaptured={(item) =>
          setData((current) =>
            current ? { ...current, captures: [item, ...(current.captures || [])] } : current
          )
        }
      />

      <div className="grid dashboard-grid">
        <article className="entry">
          <h2>Inbox</h2>
          <p className="journal-text">{data?.captures?.length || 0} open captures</p>
          <a className="text-link" href="#/inbox">
            Process inbox
          </a>
        </article>

        <article className="entry body-module">
          <h2>Last 7 Days of Workouts</h2>
          {recentWorkouts.length ? (
            <div className="stack">
              {recentWorkouts.map((workout) => (
                <p className="metric-line" key={workout.id}>
                  {workout.date} / {workout.exercises.length} exercises
                </p>
              ))}
            </div>
          ) : (
            <Empty>No workout entries in the last seven days.</Empty>
          )}
        </article>

        <article className="entry body-module">
          <h2>Last Golf Round</h2>
          {data?.golf?.[0] ? (
            <p className="metric-line">
              {data.golf[0].date} / {data.golf[0].course || "Course unlisted"} / {data.golf[0].score || "-"}
            </p>
          ) : (
            <Empty>No golf rounds logged.</Empty>
          )}
        </article>

        <article className="entry body-module">
          <h2>Latest Daily Metric</h2>
          {data?.metrics?.[0] ? (
            <p className="metric-line">
              {data.metrics[0].date} / {data.metrics[0].weight_lbs ?? "-"} lb / {data.metrics[0].sleep_hours ?? "-"} h
            </p>
          ) : (
            <Empty>No daily metrics logged.</Empty>
          )}
        </article>

        <article className="entry mind-module">
          <h2>Currently Reading</h2>
          {currentBook ? (
            <p className="journal-text">
              {currentBook.title} by {currentBook.author}
            </p>
          ) : (
            <Empty>No unfinished book is logged.</Empty>
          )}
        </article>

        <article className="entry mind-module">
          <h2>Last Philosophy Note</h2>
          {data?.philosophy?.[0] ? (
            <p className="journal-text">
              {data.philosophy[0].thinker}: {data.philosophy[0].disturbance}
            </p>
          ) : (
            <Empty>No philosophy notes logged.</Empty>
          )}
        </article>

        <article className="entry mind-module">
          <h2>Last Decision</h2>
          {data?.decisions?.[0] ? (
            <p className="journal-text">
              {data.decisions[0].title} / {data.decisions[0].date}
            </p>
          ) : (
            <Empty>No decisions logged.</Empty>
          )}
        </article>
      </div>
    </section>
  );
}
