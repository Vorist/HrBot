// frontend/src/components/TrainingTab.jsx
import React, { useState } from "react";
import { Button } from "@/components/ui/button";

export default function TrainingTab() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [log, setLog] = useState("");

  const train = async (type) => {
    setLoading(true);
    setStatus(`⏳ Навчання ${type}...`);
    setLog("");

    try {
      const res = await fetch(`/api/training/${type}`, { method: "POST" });
      const output = await res.text();

      if (res.ok) {
        setStatus(`✅ ${type.toUpperCase()} навчання завершено.`);
      } else {
        setStatus(`❌ Помилка під час навчання (${type})`);
      }

      setLog(output);
    } catch (err) {
      setStatus(`❌ Помилка: ${err.message || "Невідома"}`);
      setLog(err.message || "Невідома помилка");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">🧠 Навчання бота</h2>

      <div className="flex flex-wrap gap-3">
        <Button onClick={() => train("good")} disabled={loading}>
          ✅ Навчити на good_dialogs
        </Button>
        <Button onClick={() => train("bad")} disabled={loading}>
          ⚠️ Навчити на bad_dialogs
        </Button>
        <Button onClick={() => train("feedback")} disabled={loading}>
          💬 Навчити з урахуванням фідбеку
        </Button>
        <Button onClick={() => train("real")} disabled={loading}>
          📥 Навчити на real_dialogs
        </Button>
        <Button onClick={() => train("all")} disabled={loading}>
          🧠 Повне навчання (all)
        </Button>
      </div>

      {status && <p className="text-sm font-medium">{status}</p>}

      {log && (
        <pre className="bg-white p-3 rounded text-sm whitespace-pre-wrap max-h-[400px] overflow-auto border border-gray-300">
          {log}
        </pre>
      )}
    </div>
  );
}
