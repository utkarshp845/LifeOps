import { useState } from "react";

import { bodyApi } from "../../api/body";
import Field from "../../components/Field.jsx";

const today = () => new Date().toISOString().slice(0, 10);
const emptyExercise = () => ({ name: "", sets: "", reps: "", weight_lbs: "" });

function numericOrNull(value) {
  return value === "" ? null : Number(value);
}

export default function WorkoutLog() {
  const [date, setDate] = useState(today());
  const [notes, setNotes] = useState("");
  const [exercises, setExercises] = useState([emptyExercise()]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  function updateExercise(index, key, value) {
    setExercises((current) => current.map((exercise, i) => (i === index ? { ...exercise, [key]: value } : exercise)));
  }

  async function submit(event) {
    event.preventDefault();
    setMessage("");
    setError("");
    const payload = {
      date,
      notes: notes || null,
      exercises: exercises
        .filter((exercise) => exercise.name.trim())
        .map((exercise) => ({
          name: exercise.name.trim(),
          sets: numericOrNull(exercise.sets),
          reps: numericOrNull(exercise.reps),
          weight_lbs: numericOrNull(exercise.weight_lbs)
        }))
    };

    try {
      await bodyApi.createWorkout(payload);
      setDate(today());
      setNotes("");
      setExercises([emptyExercise()]);
      setMessage("Workout logged.");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="body-module">
      <header className="page-header">
        <h1>Log Workout</h1>
        <p>Training recorded as plain facts: date, work, load, and whatever needs remembering.</p>
      </header>
      <form className="form-panel" onSubmit={submit}>
        <div className="row">
          <Field label="Date">
            <input type="date" value={date} onChange={(event) => setDate(event.target.value)} required />
          </Field>
          <Field label="Notes">
            <input value={notes} onChange={(event) => setNotes(event.target.value)} />
          </Field>
        </div>

        <p className="section-title">Exercises</p>
        <div className="stack">
          {exercises.map((exercise, index) => (
            <div className="inline-row" key={index}>
              <Field label="Name">
                <input value={exercise.name} onChange={(event) => updateExercise(index, "name", event.target.value)} />
              </Field>
              <Field label="Sets">
                <input type="number" min="0" value={exercise.sets} onChange={(event) => updateExercise(index, "sets", event.target.value)} />
              </Field>
              <Field label="Reps">
                <input type="number" min="0" value={exercise.reps} onChange={(event) => updateExercise(index, "reps", event.target.value)} />
              </Field>
              <Field label="Weight">
                <input
                  type="number"
                  min="0"
                  step="0.5"
                  value={exercise.weight_lbs}
                  onChange={(event) => updateExercise(index, "weight_lbs", event.target.value)}
                />
              </Field>
              <button
                className="secondary"
                type="button"
                onClick={() => setExercises((current) => current.filter((_, i) => i !== index))}
                disabled={exercises.length === 1}
              >
                Remove
              </button>
            </div>
          ))}
        </div>

        <button type="button" className="secondary" onClick={() => setExercises((current) => [...current, emptyExercise()])}>
          Add Exercise
        </button>
        {message ? <p className="success">{message}</p> : null}
        {error ? <p className="error">{error}</p> : null}
        <button type="submit">Save Workout</button>
      </form>
    </section>
  );
}
