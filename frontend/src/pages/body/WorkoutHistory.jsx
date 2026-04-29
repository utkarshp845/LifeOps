import { useEffect, useState } from "react";

import { bodyApi } from "../../api/body";

export default function WorkoutHistory() {
  const [workouts, setWorkouts] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    bodyApi.getWorkoutHistory().then(setWorkouts).catch((err) => setError(err.message));
  }, []);

  return (
    <section className="body-module">
      <header className="page-header">
        <h1>Workout History</h1>
        <p>A scrollable training ledger with every movement left open to inspection.</p>
      </header>
      {error ? <p className="error">{error}</p> : null}
      <div className="list">
        {workouts.map((workout) => (
          <article className="entry" key={workout.id}>
            <h2>{workout.date}</h2>
            {workout.notes ? <p>{workout.notes}</p> : null}
            {workout.exercises.length ? (
              <table>
                <thead>
                  <tr>
                    <th>Exercise</th>
                    <th>Sets</th>
                    <th>Reps</th>
                    <th>Lb</th>
                  </tr>
                </thead>
                <tbody>
                  {workout.exercises.map((exercise) => (
                    <tr key={exercise.id}>
                      <td>{exercise.name}</td>
                      <td>{exercise.sets ?? "-"}</td>
                      <td>{exercise.reps ?? "-"}</td>
                      <td>{exercise.weight_lbs ?? "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="muted">No exercises attached.</p>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}
