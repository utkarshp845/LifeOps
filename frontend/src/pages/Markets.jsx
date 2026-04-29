import { useEffect, useState } from "react";

import { marketsApi } from "../api/markets";
import Field from "../components/Field.jsx";

const money = (value) =>
  value === null || value === undefined
    ? "-"
    : new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(value);

function numberOrNull(value) {
  return value === "" ? null : Number(value);
}

export default function Markets() {
  const [stocks, setStocks] = useState([]);
  const [form, setForm] = useState({
    ticker: "",
    company_name: "",
    shares: "",
    average_cost: "",
    watchlist: false,
    thesis: "",
    notes: ""
  });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function load() {
    setStocks(await marketsApi.getStocks());
  }

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, []);

  async function submit(event) {
    event.preventDefault();
    setError("");
    setMessage("");
    try {
      await marketsApi.createStock({
        ticker: form.ticker,
        company_name: form.company_name || null,
        shares: numberOrNull(form.shares),
        average_cost: numberOrNull(form.average_cost),
        watchlist: form.watchlist,
        thesis: form.thesis || null,
        notes: form.notes || null
      });
      setForm({ ticker: "", company_name: "", shares: "", average_cost: "", watchlist: false, thesis: "", notes: "" });
      await load();
      setMessage("Stock saved.");
    } catch (err) {
      setError(err.message);
    }
  }

  async function refreshQuote(stock) {
    setError("");
    setMessage("");
    try {
      await marketsApi.refreshQuote(stock.id);
      await load();
      setMessage(`${stock.ticker} quote refreshed.`);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="body-module">
      <header className="page-header">
        <h1>Markets</h1>
        <p>Positions, watchlist names, and quote checks kept beside the thesis that makes them worth your attention.</p>
      </header>
      <div className="grid two-col">
        <form className="form-panel" onSubmit={submit}>
          <div className="row">
            <Field label="Ticker">
              <input value={form.ticker} onChange={(event) => setForm({ ...form, ticker: event.target.value })} required />
            </Field>
            <Field label="Company">
              <input value={form.company_name} onChange={(event) => setForm({ ...form, company_name: event.target.value })} />
            </Field>
          </div>
          <div className="row">
            <Field label="Shares">
              <input type="number" step="0.0001" value={form.shares} onChange={(event) => setForm({ ...form, shares: event.target.value })} />
            </Field>
            <Field label="Average cost">
              <input
                type="number"
                step="0.01"
                value={form.average_cost}
                onChange={(event) => setForm({ ...form, average_cost: event.target.value })}
              />
            </Field>
          </div>
          <label className="checkbox-line">
            <input type="checkbox" checked={form.watchlist} onChange={(event) => setForm({ ...form, watchlist: event.target.checked })} />
            Watchlist only
          </label>
          <Field label="Thesis">
            <textarea value={form.thesis} onChange={(event) => setForm({ ...form, thesis: event.target.value })} />
          </Field>
          <Field label="Notes">
            <textarea value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} />
          </Field>
          {error ? <p className="error">{error}</p> : null}
          {message ? <p className="success">{message}</p> : null}
          <button type="submit">Save Stock</button>
        </form>

        <div className="list">
          {stocks.map((stock) => {
            const quote = stock.latest_quote;
            const marketValue = quote && stock.shares ? quote.price * stock.shares : null;
            const costBasis = stock.average_cost && stock.shares ? stock.average_cost * stock.shares : null;
            const gain = marketValue !== null && costBasis !== null ? marketValue - costBasis : null;
            return (
              <article className="entry" key={stock.id}>
                <div className="split-heading">
                  <h2>{stock.ticker}</h2>
                  <button className="secondary" type="button" onClick={() => refreshQuote(stock)}>
                    Refresh Quote
                  </button>
                </div>
                <p className="metric-line">
                  {stock.company_name || "Company unlisted"} / {stock.watchlist ? "watchlist" : `${stock.shares ?? "-"} shares`}
                </p>
                <table>
                  <tbody>
                    <tr>
                      <th>Price</th>
                      <td>{quote ? money(quote.price) : "-"}</td>
                    </tr>
                    <tr>
                      <th>Change</th>
                      <td>{quote ? `${quote.change_amount ?? 0} / ${quote.change_percent ?? 0}%` : "-"}</td>
                    </tr>
                    <tr>
                      <th>Market Value</th>
                      <td>{money(marketValue)}</td>
                    </tr>
                    <tr>
                      <th>Gain/Loss</th>
                      <td>{money(gain)}</td>
                    </tr>
                  </tbody>
                </table>
                {stock.thesis ? <p>{stock.thesis}</p> : null}
                {stock.notes ? <p className="muted">{stock.notes}</p> : null}
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
