import { useEffect, useState } from "react";

import { clearToken, getToken, setToken } from "./api/client";
import Layout from "./components/Layout.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Inbox from "./pages/Inbox.jsx";
import Login from "./pages/Login.jsx";
import DailyMetrics from "./pages/body/DailyMetrics.jsx";
import GolfLog from "./pages/body/GolfLog.jsx";
import WorkoutHistory from "./pages/body/WorkoutHistory.jsx";
import WorkoutLog from "./pages/body/WorkoutLog.jsx";
import BookLog from "./pages/mind/BookLog.jsx";
import DecisionJournal from "./pages/mind/DecisionJournal.jsx";
import PhilosophyNotes from "./pages/mind/PhilosophyNotes.jsx";

const routes = {
  "/": Dashboard,
  "/inbox": Inbox,
  "/workout": WorkoutLog,
  "/workouts": WorkoutHistory,
  "/golf": GolfLog,
  "/metrics": DailyMetrics,
  "/books": BookLog,
  "/philosophy": PhilosophyNotes,
  "/decisions": DecisionJournal
};

function currentRoute() {
  return window.location.hash.replace("#", "") || "/";
}

export default function App() {
  const [route, setRoute] = useState(currentRoute());
  const [authenticated, setAuthenticated] = useState(Boolean(getToken()));

  useEffect(() => {
    const onHashChange = () => setRoute(currentRoute());
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  function handleLogin(token) {
    setToken(token);
    setAuthenticated(true);
    window.location.hash = "#/";
  }

  function handleLogout() {
    clearToken();
    setAuthenticated(false);
    window.location.hash = "#/login";
  }

  if (!authenticated || route === "/login") {
    return <Login onLogin={handleLogin} />;
  }

  const Page = routes[route] || Dashboard;

  return (
    <Layout route={route} onLogout={handleLogout}>
      <Page />
    </Layout>
  );
}
