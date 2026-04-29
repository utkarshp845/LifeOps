const navGroups = [
  {
    label: "Capture",
    links: [["/inbox", "Inbox"]]
  },
  {
    label: "Direction",
    links: [
      ["/goals", "Goals"],
      ["/reviews", "Reviews"]
    ]
  },
  {
    label: "Body",
    links: [
      ["/workout", "Log Workout"],
      ["/workouts", "Workout History"],
      ["/golf", "Golf Log"],
      ["/metrics", "Daily Metrics"]
    ]
  },
  {
    label: "Mind",
    links: [
      ["/books", "Book Log"],
      ["/philosophy", "Philosophy Notes"],
      ["/decisions", "Decision Journal"]
    ]
  },
  {
    label: "Life",
    links: [
      ["/markets", "Markets"],
      ["/build", "Build"],
      ["/wealth", "Wealth"]
    ]
  }
];

export default function Layout({ children, route, onLogout }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a href="#/" className="brand" aria-current={route === "/" ? "page" : undefined}>
          Life OS
        </a>
        <nav>
          {navGroups.map((group) => (
            <section className="nav-group" key={group.label}>
              <p>{group.label}</p>
              {group.links.map(([href, label]) => (
                <a key={href} href={`#${href}`} aria-current={route === href ? "page" : undefined}>
                  {label}
                </a>
              ))}
            </section>
          ))}
        </nav>
        <button className="secondary full" type="button" onClick={onLogout}>
          Sign Out
        </button>
      </aside>
      <main className="main-frame">{children}</main>
    </div>
  );
}
