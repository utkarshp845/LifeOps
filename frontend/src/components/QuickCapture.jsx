import { useState } from "react";

import { captureApi } from "../api/capture";

export default function QuickCapture({ onCaptured }) {
  const [rawText, setRawText] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault();
    const text = rawText.trim();
    if (!text) return;
    setSaving(true);
    setMessage("");
    setError("");
    try {
      const item = await captureApi.createCapture({ raw_text: text, source: "quick" });
      setRawText("");
      setMessage("Captured.");
      if (onCaptured) onCaptured(item);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="quick-capture" onSubmit={submit}>
      <textarea
        value={rawText}
        onChange={(event) => setRawText(event.target.value)}
        placeholder="Catch it before it fragments..."
        aria-label="Quick capture"
      />
      <div className="capture-actions">
        <span className={error ? "error" : "success"}>{error || message}</span>
        <button type="submit" disabled={saving || !rawText.trim()}>
          Capture
        </button>
      </div>
    </form>
  );
}
